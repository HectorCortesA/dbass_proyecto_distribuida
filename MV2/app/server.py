import grpc
import json
import subprocess
from concurrent import futures

import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

from app.services.query_service import (
    filter_documents,
    aggregate_documents,
    aggregate_distinct,
    aggregate_inner_join,
)


class QueryServiceServicer(pb2_grpc.QueryServiceServicer):

    def AggregateSum(self, request, context):
        """Suma distribuida via MPI."""
        try:
            comando = [
                "mpirun", "--allow-run-as-root", "-n", "4",
                "python", "app/mpi_worker.py",
                request.user_id, request.db_name,
                request.table_name, request.field,
            ]
            result = subprocess.run(
                comando, capture_output=True, text=True, check=True
            )
            return pb2.QueryResponse(result=result.stdout.strip())
        except subprocess.CalledProcessError as e:
            return pb2.QueryResponse(error=f"Fallo MPI: {e.stderr}")
        except Exception as e:
            return pb2.QueryResponse(error=str(e))

    def FilterDocuments(self, request, context):
        try:
            filters = json.loads(request.filters_json) if request.filters_json else {}
            result = filter_documents(
                db_name=request.db_name,
                collection_name=request.collection_name,
                filters=filters,
                owner_id=request.owner_id,
            )
            return pb2.QueryResponse(result=json.dumps(result["data"]))
        except Exception as e:
            return pb2.QueryResponse(error=str(e))

    def AggregateDocuments(self, request, context):
        try:
            pipeline = json.loads(request.pipeline_json) if request.pipeline_json else []
            result = aggregate_documents(
                db_name=request.db_name,
                collection_name=request.collection_name,
                pipeline=pipeline,
                owner_id=request.owner_id,
            )
            return pb2.QueryResponse(result=json.dumps(result["data"]))
        except Exception as e:
            return pb2.QueryResponse(error=str(e))

    def DistinctValues(self, request, context):
        try:
            result = aggregate_distinct(
                user_id=request.user_id,
                db_name=request.db_name,
                table_name=request.table_name,
                field=request.field,
            )
            return pb2.QueryResponse(result=json.dumps(result["data"]))
        except Exception as e:
            return pb2.QueryResponse(error=str(e))

    def InnerJoin(self, request, context):
        try:
            result = aggregate_inner_join(
                user_id=request.user_id,
                db_name=request.db_name,
                table_name=request.table_name,
                from_table=request.from_table,
                local_field=request.local_field,
                foreign_field=request.foreign_field,
                as_name=request.as_name,
            )
            return pb2.QueryResponse(result=json.dumps(result["data"]))
        except Exception as e:
            return pb2.QueryResponse(error=str(e))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_QueryServiceServicer_to_server(QueryServiceServicer(), server)
    server.add_insecure_port("[::]:50053")
    print("MV2 Query Service (gRPC) corriendo en puerto 50053")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()