from fastapi import APIRouter, Depends, HTTPException
import json
from app.middleware.role_middleware import require_read
from app.schemas.query_schema import DistinctQuerySchema, FilterQuerySchema, AggregateQuerySchema, JoinQuerySchema
from app.grpc_clients.query_client import QueryClient

router = APIRouter(prefix="/query", tags=["Queries"])
query_grpc = QueryClient()

@router.post("/sum")
def get_sum(data: DistinctQuerySchema, current_user: dict = Depends(require_read)):
    response = query_grpc.get_sum(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name,
        field=data.field
    )
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return {"data": json.loads(response.result)}

@router.post("/filter")
def get_filtered_documents(data: FilterQuerySchema, current_user: dict = Depends(require_read)):
    return {"message": "Endpoint preparado para filtros"}

@router.post("/aggregate")
def run_aggregation(data: AggregateQuerySchema, current_user: dict = Depends(require_read)):
    return {"message": "Endpoint preparado para pipeline de agregación"}

@router.post("/distinct")
def get_distinct_values(data: DistinctQuerySchema, current_user: dict = Depends(require_read)):
    return {"message": "Endpoint preparado para valores distintos"}

@router.post("/join")
def perform_inner_join(data: JoinQuerySchema, current_user: dict = Depends(require_read)):
    return {"message": "Endpoint preparado para inner join"}