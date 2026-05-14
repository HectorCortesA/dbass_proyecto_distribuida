from fastapi import APIRouter, Depends, HTTPException
from app.middleware.role_middleware import require_admin
from app.schemas.database_schema import CreateDatabaseSchema, DeleteDatabaseSchema
from app.grpc_clients.db_client import DbClient

router = APIRouter(prefix="/db", tags=["Database"])
db_grpc = DbClient()

@router.post("/create")
def create_new_database(
    data: CreateDatabaseSchema,
    current_user: dict = Depends(require_admin)
):
    # Llamada al microservicio en la MV1 vía gRPC
    response = db_grpc.create_database(
        user_id=current_user["id"], 
        db_name=data.db_name
    )
    
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
        
    return {"message": response.message}

# Repetir el patrón para /delete y /list usando llamadas gRPC