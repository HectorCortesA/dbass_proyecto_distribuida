from fastapi import APIRouter, Depends, HTTPException
from app.middleware.jwt_middleware import get_current_user
from app.schemas.collection_schema import CreateCollectionSchema, DeleteCollectionSchema
from app.grpc_clients.db_client import DbClient

router = APIRouter(prefix="/collection", tags=["Collections"])
db_grpc = DbClient()

@router.post("/create")
def create_new_collection(data: CreateCollectionSchema, current_user: dict = Depends(get_current_user)):
    # Aquí irá la llamada a gRPC cuando agregues la función a tu archivo .proto
    return {"message": f"Endpoint preparado para crear colección {data.collection_name}"}

@router.get("/list")
def get_collections(db_name: str, current_user: dict = Depends(get_current_user)):
    return {"message": "Endpoint preparado para listar colecciones"}

@router.delete("/delete")
def remove_collection(data: DeleteCollectionSchema, current_user: dict = Depends(get_current_user)):
    return {"message": "Endpoint preparado para eliminar colección"}