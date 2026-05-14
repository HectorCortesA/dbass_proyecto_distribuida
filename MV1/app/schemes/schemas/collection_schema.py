from pydantic import BaseModel

class CreateCollectionSchema(BaseModel):
    db_name: str
    collection_name: str

class DeleteCollectionSchema(BaseModel):
    db_name: str
    collection_name: str