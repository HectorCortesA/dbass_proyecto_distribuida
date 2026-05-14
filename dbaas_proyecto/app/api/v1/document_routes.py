import json
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.jwt_middleware import get_current_user
from app.schemas.document_schema import InsertDocumentSchema, UpdateDocumentSchema, DeleteDocumentSchema
from app.grpc_clients.db_client import DbClient

router = APIRouter(tags=["Documents"])
db_grpc = DbClient()

@router.post("/insert")
def insert_new_document(data: InsertDocumentSchema, current_user: dict = Depends(get_current_user)):
    response = db_grpc.insert_document(
        db_name=data.db_name,
        collection_name=data.collection_name,
        document=data.document,
        owner_id=current_user["id"]
    )
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return {"message": response.message, "id": response.id}

@router.get("/find")
def get_documents(db_name: str, collection_name: str, current_user: dict = Depends(get_current_user)):
    response = db_grpc.find_documents(
        db_name=db_name,
        collection_name=collection_name,
        owner_id=current_user["id"]
    )
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    try:
        data = json.loads(response.data_json)
    except Exception:
        data = []
    return {"data": data}

@router.put("/update")
def update_existing_document(data: UpdateDocumentSchema, current_user: dict = Depends(get_current_user)):
    response = db_grpc.update_document(
        db_name=data.db_name,
        collection_name=data.collection_name,
        filter_query=data.filter_query,
        new_data=data.new_data,
        owner_id=current_user["id"]
    )
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return {"message": response.message, "modified_count": response.modified_count}

@router.delete("/delete")
def remove_document(data: DeleteDocumentSchema, current_user: dict = Depends(get_current_user)):
    response = db_grpc.delete_document(
        db_name=data.db_name,
        collection_name=data.collection_name,
        filter_query=data.filter_query,
        owner_id=current_user["id"]
    )
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return {"message": response.message, "deleted_count": response.deleted_count}