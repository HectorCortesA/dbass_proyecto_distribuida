# app/services/query_service.py

from app.database.connection import client
from bson import ObjectId
from mpi4py import MPI
import math

def get_mpi_info():
    """Obtiene el comunicador, el rango (ID del proceso) y el tamaño (total de procesos)"""
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    return comm, rank, size

def count_documents(user_id: str, db_name: str, table_name: str, filters: dict = {}):
    comm, rank, size = get_mpi_info()
    chunks = None

    if rank == 0:
        database_name = f"{user_id}_{db_name}"
        db = client[database_name]
        collection = db[table_name]
        
        # 1. Extraer los documentos crudos
        documents = list(collection.find(filters, {"_id": 1}))
        
        # 2. Dividir los documentos en chunks para cada proceso
        chunk_size = math.ceil(len(documents) / size) if size > 0 else 0
        chunks = [documents[i:i + chunk_size] for i in range(0, len(documents), chunk_size)]
        
        # Rellenar con listas vacías si hay más procesos que chunks
        while len(chunks) < size:
            chunks.append([])

    # 3. Scatter: Repartir los chunks a todos los nodos
    local_data = comm.scatter(chunks, root=0)

    # 4. Cálculo local: Cada nodo cuenta cuántos documentos le tocaron
    local_count = len(local_data)

    # 5. Reduce: El maestro suma todos los conteos locales
    total_count = comm.reduce(local_count, op=MPI.SUM, root=0)

    if rank == 0:
        return {"count": total_count}
    return None

def aggregate_sum(user_id: str, db_name: str, table_name: str, field: str):
    comm, rank, size = get_mpi_info()
    chunks = None

    if rank == 0:
        database_name = f"{user_id}_{db_name}"
        db = client[database_name]
        collection = db[table_name]
        
        # 1. Extraer los documentos y filtrar solo el campo a sumar
        documents = list(collection.find({}, {field: 1, "_id": 0}))
        values = [doc[field] for doc in documents if field in doc and isinstance(doc[field], (int, float))]
        
        # 2. Dividir los valores numéricos en chunks
        chunk_size = math.ceil(len(values) / size) if size > 0 else 0
        chunks = [values[i:i + chunk_size] for i in range(0, len(values), chunk_size)]
        
        while len(chunks) < size:
            chunks.append([])

    # 3. Scatter: Enviar los valores a los nodos
    local_data = comm.scatter(chunks, root=0)

    # 4. Cálculo local: Cada nodo suma su fragmento
    local_sum = sum(local_data)

    # 5. Reduce: El maestro consolida la suma total
    total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)

    if rank == 0:
        return {"data": [{"_id": None, "total": total_sum}]}
    return None

def aggregate_avg(user_id: str, db_name: str, table_name: str, field: str):
    comm, rank, size = get_mpi_info()
    chunks = None

    if rank == 0:
        database_name = f"{user_id}_{db_name}"
        db = client[database_name]
        collection = db[table_name]
        
        # 1. Extraer documentos numéricos
        documents = list(collection.find({}, {field: 1, "_id": 0}))
        values = [doc[field] for doc in documents if field in doc and isinstance(doc[field], (int, float))]
        
        # 2. Preparar los chunks
        chunk_size = math.ceil(len(values) / size) if size > 0 else 0
        chunks = [values[i:i + chunk_size] for i in range(0, len(values), chunk_size)]
        
        while len(chunks) < size:
            chunks.append([])

    # 3. Scatter
    local_data = comm.scatter(chunks, root=0)

    # 4. Cálculo local: Para el promedio necesitamos tanto la suma como la cantidad de elementos locales
    local_sum = sum(local_data)
    local_count = len(local_data)

    # 5. Reduce: Consolidar ambas variables en el maestro
    total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)
    total_count = comm.reduce(local_count, op=MPI.SUM, root=0)

    if rank == 0:
        avg = (total_sum / total_count) if total_count > 0 else 0
        return {"data": [{"_id": None, "average": avg}]}
    return None

def sort_documents(user_id: str, db_name: str, table_name: str, field: str, order: int = 1):
    database_name = f"{user_id}_{db_name}"
    db = client[database_name]
    collection = db[table_name]
    documents = list(collection.find().sort(field, order))
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return {"data": documents}

def limit_documents(user_id: str, db_name: str, table_name: str, limit: int):
    database_name = f"{user_id}_{db_name}"
    db = client[database_name]
    collection = db[table_name]
    documents = list(collection.find().limit(limit))
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return {"data": documents}

# --- Funciones restauradas ---

def aggregate_distinct(user_id: str, db_name: str, table_name: str, field: str):
    database_name = f"{user_id}_{db_name}"
    db = client[database_name]
    collection = db[table_name]
    result = collection.distinct(field)
    return {"data": result}

def aggregate_inner_join(user_id: str, db_name: str, table_name: str, from_table: str, local_field: str, foreign_field: str, as_name: str):
    database_name = f"{user_id}_{db_name}"
    db = client[database_name]
    collection = db[table_name]

    pipeline = [
        {
            "$lookup": {
                "from": from_table,
                "localField": local_field,
                "foreignField": foreign_field,
                "as": as_name
            }
        },
        {
            "$unwind": f"${as_name}"
        }
    ]

    documents = list(collection.aggregate(pipeline))

    for doc in documents:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        if as_name in doc and "_id" in doc[as_name]:
            doc[as_name]["_id"] = str(doc[as_name]["_id"])

    return {"data": documents}

def filter_documents(db_name: str, collection_name: str, filters: dict, owner_id: str):
    database_name = f"{owner_id}_{db_name}"
    db = client[database_name]
    
    if "_id" in filters and isinstance(filters["_id"], str):
        filters["_id"] = ObjectId(filters["_id"])
        
    documents = list(db[collection_name].find(filters))
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return {"data": documents}

def aggregate_documents(db_name: str, collection_name: str, pipeline: list, owner_id: str):
    database_name = f"{owner_id}_{db_name}"
    db = client[database_name]
    documents = list(db[collection_name].aggregate(pipeline))
    for doc in documents:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return {"data": documents}