from fastapi import APIRouter, Depends, HTTPException
import json
from app.middleware.jwt_middleware import get_current_user
from app.schemas.query_schema import DistinctQuerySchema, FilterQuerySchema, AggregateQuerySchema, JoinQuerySchema, CountQuerySchema, AvgQuerySchema
from app.grpc_clients.query_client import QueryClient

router = APIRouter(tags=["Queries"])
query_grpc = QueryClient()

@router.post("/sum")
def get_sum(data: DistinctQuerySchema, current_user: dict = Depends(get_current_user)):
    response = query_grpc.get_sum(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name,
        field=data.field
    )
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    try:
        res = json.loads(response.result)
    except Exception:
        res = response.result
    return {"data": res}

@router.post("/filter")
def get_filtered_documents(data: FilterQuerySchema, current_user: dict = Depends(get_current_user)):
    response = query_grpc.filter_documents(
        db_name=data.db_name,
        collection_name=data.collection_name,
        filters=data.filters,
        owner_id=current_user["id"]
    )
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    try:
        res = json.loads(response.result)
    except Exception:
        res = response.result
    return {"data": res}

@router.post("/aggregate")
def run_aggregation(data: AggregateQuerySchema, current_user: dict = Depends(get_current_user)):
    response = query_grpc.aggregate_documents(
        db_name=data.db_name,
        collection_name=data.collection_name,
        pipeline=data.pipeline,
        owner_id=current_user["id"]
    )
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    try:
        res = json.loads(response.result)
    except Exception:
        res = response.result
    return {"data": res}

@router.post("/distinct")
def get_distinct_values(data: DistinctQuerySchema, current_user: dict = Depends(get_current_user)):
    response = query_grpc.distinct_values(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name,
        field=data.field
    )
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    try:
        res = json.loads(response.result)
    except Exception:
        res = response.result
    return {"data": res}

@router.post("/join")
def perform_inner_join(data: JoinQuerySchema, current_user: dict = Depends(get_current_user)):
    response = query_grpc.inner_join(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name,
        from_table=data.from_table,
        local_field=data.local_field,
        foreign_field=data.foreign_field,
        as_name=data.as_name
    )
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    try:
        res = json.loads(response.result)
    except Exception:
        res = response.result
    return {"data": res}

@router.post("/count")
def get_count(data: CountQuerySchema, current_user: dict = Depends(get_current_user)):
    response = query_grpc.get_count(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name
    )
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    try:
        res = json.loads(response.result)
    except Exception:
        res = response.result
    return {"data": res}

@router.post("/avg")
def get_avg(data: AvgQuerySchema, current_user: dict = Depends(get_current_user)):
    response = query_grpc.get_avg(
        user_id=current_user["id"],
        db_name=data.db_name,
        table_name=data.collection_name,
        field=data.field
    )
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    try:
        res = json.loads(response.result)
    except Exception:
        res = response.result
    return {"data": res}