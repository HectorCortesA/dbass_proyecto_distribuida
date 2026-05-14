import re
import json
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.jwt_middleware import get_current_user
from app.schemas.sql_schema import SqlQuerySchema
from app.grpc_clients.db_client import DbClient
from app.grpc_clients.query_client import QueryClient

router = APIRouter(tags=["SQL Interface"])
db_grpc = DbClient()
query_grpc = QueryClient()

def parse_value(v: str):
    v = v.strip()
    # Strip surrounding quotes if present
    if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
        return v[1:-1]
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            if v.upper() == 'TRUE': return True
            if v.upper() == 'FALSE': return False
            if v.upper() == 'NULL': return None
            return v

def parse_condition(cond_str: str) -> dict:
    filters = {}
    if not cond_str or not cond_str.strip():
        return filters
    
    # Try parsing multiple conditions with AND (basic support)
    conditions = re.split(r'\s+AND\s+', cond_str, flags=re.IGNORECASE)
    for cond in conditions:
        match = re.match(r"^\s*(\w+)\s*([=><!]+)\s*(.+)\s*$", cond.strip())
        if match:
            col, op, val = match.groups()
            parsed_val = parse_value(val)
            if op == '=' or op == '==':
                filters[col] = parsed_val
            elif op == '>':
                filters[col] = {"$gt": parsed_val}
            elif op == '<':
                filters[col] = {"$lt": parsed_val}
            elif op == '>=':
                filters[col] = {"$gte": parsed_val}
            elif op == '<=':
                filters[col] = {"$lte": parsed_val}
            elif op == '!=':
                filters[col] = {"$ne": parsed_val}
    return filters

@router.post("/execute")
def execute_sql_command(data: SqlQuerySchema, current_user: dict = Depends(get_current_user)):
    cmd = data.command.strip().rstrip(';').strip()
    db_name = data.db_name.strip() if data.db_name else ""
    
    # 1. CREATE DATABASE
    match = re.match(r"^CREATE\s+DATABASE\s+(\w+)$", cmd, re.IGNORECASE)
    if match:
        target_db = match.group(1)
        res = db_grpc.create_database(user_id=current_user["id"], db_name=target_db)
        if hasattr(res, 'error') and res.error:
            raise HTTPException(status_code=500, detail=res.error)
        return {"message": res.message, "operation": "CREATE DATABASE"}
        
    # 2. DROP DATABASE
    match = re.match(r"^DROP\s+DATABASE\s+(\w+)$", cmd, re.IGNORECASE)
    if match:
        target_db = match.group(1)
        res = db_grpc.delete_database(user_id=current_user["id"], db_name=target_db)
        if hasattr(res, 'error') and res.error:
            raise HTTPException(status_code=500, detail=res.error)
        return {"message": res.message, "operation": "DROP DATABASE"}

    # Support optional USE prefix: e.g. "USE test; SELECT * FROM users"
    if match := re.match(r"^USE\s+(\w+)\s*;\s*(.*)$", cmd, re.IGNORECASE):
        db_name = match.group(1)
        cmd = match.group(2).strip().rstrip(';').strip()
        if not cmd:
            return {"message": f"Switched to database {db_name}", "database": db_name}

    # 3. CREATE TABLE
    match = re.match(r"^CREATE\s+TABLE\s+(\w+)", cmd, re.IGNORECASE)
    if match:
        if not db_name:
            raise HTTPException(status_code=400, detail="Database name is required context for creating a table.")
        table_name = match.group(1)
        res = db_grpc.create_collection(user_id=current_user["id"], db_name=db_name, collection_name=table_name)
        if hasattr(res, 'error') and res.error:
            raise HTTPException(status_code=500, detail=res.error)
        return {"message": res.message, "operation": "CREATE TABLE"}

    # 4. DROP TABLE
    match = re.match(r"^DROP\s+TABLE\s+(\w+)$", cmd, re.IGNORECASE)
    if match:
        if not db_name:
            raise HTTPException(status_code=400, detail="Database name is required context for dropping a table.")
        table_name = match.group(1)
        res = db_grpc.delete_collection(user_id=current_user["id"], db_name=db_name, collection_name=table_name)
        if hasattr(res, 'error') and res.error:
            raise HTTPException(status_code=500, detail=res.error)
        return {"message": res.message, "operation": "DROP TABLE"}

    # 5. INSERT INTO
    match = re.match(r"^INSERT\s+INTO\s+(\w+)(?:\s*\(([^)]+)\))?\s*VALUES\s*\(([^)]+)\)$", cmd, re.IGNORECASE)
    if match:
        if not db_name:
            raise HTTPException(status_code=400, detail="Database name is required context for inserting documents.")
        table_name, cols_str, vals_str = match.groups()
        
        raw_vals = re.split(r',\s*(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)', vals_str)
        vals = [parse_value(v) for v in raw_vals]
        
        doc = {}
        if cols_str:
            cols = [c.strip() for c in cols_str.split(',')]
            for i, col in enumerate(cols):
                doc[col] = vals[i] if i < len(vals) else None
        else:
            for i, val in enumerate(vals):
                doc[f"col_{i}"] = val
                
        res = db_grpc.insert_document(db_name=db_name, collection_name=table_name, document=doc, owner_id=current_user["id"])
        if hasattr(res, 'error') and res.error:
            raise HTTPException(status_code=500, detail=res.error)
        return {"message": res.message, "id": res.id, "operation": "INSERT"}

    # 6. UPDATE
    match = re.match(r"^UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?$", cmd, re.IGNORECASE)
    if match:
        if not db_name:
            raise HTTPException(status_code=400, detail="Database name is required context for updating documents.")
        table_name, set_str, where_str = match.groups()
        
        new_data = {}
        assignments = re.split(r',\s*(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)', set_str)
        for assign in assignments:
            if '=' in assign:
                k, v = assign.split('=', 1)
                new_data[k.strip()] = parse_value(v)
                
        filter_query = parse_condition(where_str) if where_str else {}
        res = db_grpc.update_document(db_name=db_name, collection_name=table_name, filter_query=filter_query, new_data=new_data, owner_id=current_user["id"])
        if hasattr(res, 'error') and res.error:
            raise HTTPException(status_code=500, detail=res.error)
        return {"message": res.message, "modified_count": res.modified_count, "operation": "UPDATE"}

    # 7. DELETE
    match = re.match(r"^DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?$", cmd, re.IGNORECASE)
    if match:
        if not db_name:
            raise HTTPException(status_code=400, detail="Database name is required context for deleting documents.")
        table_name, where_str = match.groups()
        filter_query = parse_condition(where_str) if where_str else {}
        res = db_grpc.delete_document(db_name=db_name, collection_name=table_name, filter_query=filter_query, owner_id=current_user["id"])
        if hasattr(res, 'error') and res.error:
            raise HTTPException(status_code=500, detail=res.error)
        return {"message": res.message, "deleted_count": res.deleted_count, "operation": "DELETE"}

    # 8. SELECT
    match = re.match(r"^SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?$", cmd, re.IGNORECASE)
    if match:
        if not db_name:
            raise HTTPException(status_code=400, detail="Database name is required context for selecting documents.")
        fields_str, table_name, where_str = match.groups()
        fields_str = fields_str.strip()
        
        # Check for aggregation functions
        upper_fields = fields_str.upper()
        if upper_fields.startswith("COUNT("):
            res = query_grpc.get_count(user_id=current_user["id"], db_name=db_name, table_name=table_name)
            if res.error:
                raise HTTPException(status_code=500, detail=res.error)
            try:
                data_res = json.loads(res.result)
            except Exception:
                data_res = res.result
            return {"data": data_res, "operation": "SELECT COUNT"}
            
        elif upper_fields.startswith("AVG("):
            agg_match = re.search(r"AVG\(\s*(\w+)\s*\)", fields_str, re.IGNORECASE)
            field = agg_match.group(1) if agg_match else ""
            res = query_grpc.get_avg(user_id=current_user["id"], db_name=db_name, table_name=table_name, field=field)
            if res.error:
                raise HTTPException(status_code=500, detail=res.error)
            try:
                data_res = json.loads(res.result)
            except Exception:
                data_res = res.result
            return {"data": data_res, "operation": "SELECT AVG"}
            
        elif upper_fields.startswith("SUM("):
            agg_match = re.search(r"SUM\(\s*(\w+)\s*\)", fields_str, re.IGNORECASE)
            field = agg_match.group(1) if agg_match else ""
            res = query_grpc.get_sum(user_id=current_user["id"], db_name=db_name, table_name=table_name, field=field)
            if res.error:
                raise HTTPException(status_code=500, detail=res.error)
            try:
                data_res = json.loads(res.result)
            except Exception:
                data_res = res.result
            return {"data": data_res, "operation": "SELECT SUM"}
            
        # Standard Select / Filter
        filters = parse_condition(where_str) if where_str else {}
        res = query_grpc.filter_documents(db_name=db_name, collection_name=table_name, filters=filters, owner_id=current_user["id"])
        if res.error:
            raise HTTPException(status_code=500, detail=res.error)
        try:
            docs = json.loads(res.result)
        except Exception:
            docs = res.result
            
        # Perform projection if specific fields are requested
        if fields_str != '*' and isinstance(docs, list):
            requested_cols = [f.strip() for f in fields_str.split(',')]
            projected_docs = []
            for d in docs:
                p_doc = {}
                for col in requested_cols:
                    if col in d:
                        p_doc[col] = d[col]
                if "_id" in d and "_id" not in requested_cols:
                    p_doc["_id"] = d["_id"]
                projected_docs.append(p_doc)
            docs = projected_docs
            
        return {"data": docs, "operation": "SELECT"}

    raise HTTPException(status_code=400, detail="Invalid or unsupported SQL command syntax.")
