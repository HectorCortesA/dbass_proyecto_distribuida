from fastapi import APIRouter, Depends, HTTPException
from app.middleware.role_middleware import require_admin
from app.middleware.jwt_middleware import get_current_user
from app.schemas.database_schema import CreateDatabaseSchema, DeleteDatabaseSchema, AssignAccessSchema
from app.grpc_clients.db_client import DbClient

router = APIRouter(prefix="/db", tags=["Database"])
db_grpc = DbClient()

@router.post("/create")
def create_new_database(data: CreateDatabaseSchema, current_user: dict = Depends(require_admin)):
    response = db_grpc.create_database(user_id=current_user["id"], db_name=data.db_name)
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return {"message": response.message}

@router.get("/list")
def get_databases(current_user: dict = Depends(get_current_user)):
    return {"message": "Endpoint preparado para listar BD vía gRPC"}

@router.delete("/delete")
def remove_database(data: DeleteDatabaseSchema, current_user: dict = Depends(require_admin)):
    return {"message": "Endpoint preparado para borrar BD vía gRPC"}

@router.post("/assign")
def assign_access(data: AssignAccessSchema, current_user: dict = Depends(get_current_user)):
    return {"message": "Endpoint preparado para asignar acceso vía gRPC"}