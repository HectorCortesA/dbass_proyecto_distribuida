from fastapi import APIRouter, Depends, HTTPException
from app.middleware.role_middleware import require_read
from app.schemas.query_schema import DistinctQuerySchema # Asegúrate que el schema sea correcto
from app.grpc_clients.query_client import QueryClient

router = APIRouter(prefix="/query", tags=["Queries"])
query_grpc = QueryClient()

@router.post("/sum")
def get_sum(
    data: DistinctQuerySchema, 
    current_user: dict = Depends(require_read)
):
    # Esta llamada dispara el proceso MPI en la MV2
    response = query_grpc.get_sum(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name,
        field=data.field
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
        
    import json
    return {"data": json.loads(response.result)}