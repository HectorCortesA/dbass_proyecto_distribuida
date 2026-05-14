from pydantic import BaseModel
from typing import Optional

class SqlQuerySchema(BaseModel):
    command: str
    db_name: Optional[str] = ""
