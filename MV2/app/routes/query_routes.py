from fastapi import APIRouter, Depends
from app.middleware.role_middleware import require_read
from app.schemas.query_schema import (
    DistinctQuerySchema, 
    JoinQuerySchema, 
    FilterQuerySchema, 
    AggregateQuerySchema
)
from app.services.query_service import (
    aggregate_distinct, 
    aggregate_inner_join, 
    filter_documents, 
    aggregate_documents
)

# Aquí definimos el router que faltaba
router = APIRouter(prefix="/query", tags=["Queries"])

@router.post("/filter")
def get_filtered_documents(
    data: FilterQuerySchema, 
    current_user: dict = Depends(require_read)
):
    return filter_documents(
        db_name=data.db_name, 
        collection_name=data.collection_name, 
        filters=data.filters, 
        owner_id=current_user["id"]
    )

@router.post("/aggregate")
def run_aggregation(
    data: AggregateQuerySchema, 
    current_user: dict = Depends(require_read)
):
    return aggregate_documents(
        db_name=data.db_name, 
        collection_name=data.collection_name, 
        pipeline=data.pipeline, 
        owner_id=current_user["id"]
    )

@router.post("/distinct")
def get_distinct_values(
    data: DistinctQuerySchema,
    current_user: dict = Depends(require_read)
):
    # Nota: Pasamos el id del usuario como user_id para coincidir con tu servicio
    return aggregate_distinct(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name,
        field=data.field
    )

@router.post("/join")
def perform_inner_join(
    data: JoinQuerySchema,
    current_user: dict = Depends(require_read)
):
    return aggregate_inner_join(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name,
        from_table=data.from_table,
        local_field=data.local_field,
        foreign_field=data.foreign_field,
        as_name=data.as_name
    )