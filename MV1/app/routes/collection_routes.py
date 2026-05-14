from fastapi import APIRouter, Depends
from app.middleware.jwt_middleware import get_current_user
from app.schemas.collection_schema import (
    CreateCollectionSchema,
    DeleteCollectionSchema
)
from app.services.collection_service import (
    create_collection,
    list_collections,
    delete_collection
)

router = APIRouter(
    prefix="/collection",
    tags=["Collections"]
)

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