from pydantic import BaseModel
from typing import Dict, Any, List

class FilterQuerySchema(BaseModel):
    db_name: str
    collection_name: str
    filters: Dict[str, Any] = {}

class AggregateQuerySchema(BaseModel):
    db_name: str
    collection_name: str
    pipeline: List[Dict[str, Any]]

class DistinctQuerySchema(BaseModel):
    db_name: str
    collection_name: str
    field: str

class JoinQuerySchema(BaseModel):
    db_name: str
    collection_name: str
    from_table: str
    local_field: str
    foreign_field: str
    as_name: str