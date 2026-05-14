from fastapi import APIRouter, Depends, HTTPException
from app.middleware.role_middleware import require_write, require_read
from app.schemas.document_schema import InsertDocumentSchema, UpdateDocumentSchema, DeleteDocumentSchema

router = APIRouter(prefix="/document", tags=["Documents"])

@router.post("/insert")
def insert_new_document(data: InsertDocumentSchema, current_user: dict = Depends(require_write)):
    return {"message": "Endpoint preparado para insertar documento vía gRPC"}

@router.get("/find")
def get_documents(db_name: str, collection_name: str, current_user: dict = Depends(require_read)):
    return {"message": "Endpoint preparado para buscar documentos vía gRPC"}

@router.put("/update")
def update_existing_document(data: UpdateDocumentSchema, current_user: dict = Depends(require_write)):
    return {"message": "Endpoint preparado para actualizar documento vía gRPC"}

@router.delete("/delete")
def remove_document(data: DeleteDocumentSchema, current_user: dict = Depends(require_write)):
    return {"message": "Endpoint preparado para borrar documento vía gRPC"}