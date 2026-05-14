from pydantic import BaseModel

class CreateDatabaseSchema(BaseModel):
    db_name: str

class DeleteDatabaseSchema(BaseModel):
    db_name: str

class AssignAccessSchema(BaseModel):
    db_name: str
    target_email: str
    role: str