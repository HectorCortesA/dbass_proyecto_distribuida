from pydantic import BaseModel
from typing import Dict, Any

class InsertDocumentSchema(BaseModel):
    db_name: str
    collection_name: str
    document: Dict[str, Any]

class UpdateDocumentSchema(BaseModel):
    db_name: str
    collection_name: str
    filter_query: Dict[str, Any]
    new_data: Dict[str, Any]

class DeleteDocumentSchema(BaseModel):
    db_name: str
    collection_name: str
    filter_query: Dict[str, Any]