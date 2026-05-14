# app/api/v1/collection_routes.py
from fastapi import APIRouter, HTTPException, Depends  # <--- ASEGÚRATE DE QUE ESTÉ AQUÍ
from app.schemas.collection_schema import CreateCollectionSchema
from app.grpc_clients.db_client import DbClient

router = APIRouter(prefix="/collections", tags=["Collections"])
db_grpc = DbClient()

# ... resto de tus rutas
#

# Crear colección
@router.post("/create")
def create_new_collection(
    data: CreateCollectionSchema,
    current_user: dict = Depends(get_current_user)
):
    return create_collection(
        db_name=data.db_name,
        collection_name=data.collection_name,
        owner_id=current_user["id"]
    )

# Listar colecciones
@router.get("/list")
def get_collections(
    db_name: str,
    current_user: dict = Depends(get_current_user)
):
    return list_collections(
        db_name=db_name,
        owner_id=current_user["id"]
    )

# Eliminar colección
@router.delete("/delete")
def remove_collection(
    data: DeleteCollectionSchema,
    current_user: dict = Depends(get_current_user)
):
    return delete_collection(
        db_name=data.db_name,
        collection_name=data.collection_name,
        owner_id=current_user["id"]
    )