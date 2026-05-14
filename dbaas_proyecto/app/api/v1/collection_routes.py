from fastapi import APIRouter, Depends, HTTPException
from app.middleware.jwt_middleware import get_current_user
from app.schemas.collection_schema import CreateCollectionSchema, DeleteCollectionSchema
from app.grpc_clients.db_client import DbClient

router = APIRouter(tags=["Collections"])
db_grpc = DbClient()

@router.post("/create")
def create_new_collection(data: CreateCollectionSchema, current_user: dict = Depends(get_current_user)):
    response = db_grpc.create_collection(
        user_id=current_user["id"],
        db_name=data.db_name,
        collection_name=data.collection_name
    )
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return {"message": response.message}

@router.get("/list")
def get_collections(db_name: str, current_user: dict = Depends(get_current_user)):
    response = db_grpc.list_collections(
        user_id=current_user["id"],
        db_name=db_name
    )
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return {"collections": list(response.collections)}

@router.delete("/delete")
def remove_collection(data: DeleteCollectionSchema, current_user: dict = Depends(get_current_user)):
    response = db_grpc.delete_collection(
        user_id=current_user["id"],
        db_name=data.db_name,
        collection_name=data.collection_name
    )
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return {"message": response.message}