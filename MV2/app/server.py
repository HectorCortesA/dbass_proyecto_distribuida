import grpc
from concurrent import futures
import subprocess, json
import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

class QueryServiceServicer(pb2_grpc.QueryServiceServicer):
    def AggregateSum(self, request, context):
        try:
            comando = [
                "mpirun", "--allow-run-as-root", "-n", "4", 
                "python", "app/mpi_worker.py",
                request.user_id, request.db_name, request.table_name, request.field
            ]
            result = subprocess.run(comando, capture_output=True, text=True, check=True)
            return pb2.QueryResponse(result=result.stdout.strip())
        except subprocess.CalledProcessError as e:
            return pb2.QueryResponse(error=f"Fallo MPI: {e.stderr}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_QueryServiceServicer_to_server(QueryServiceServicer(), server)
    server.add_insecure_port('[::]:50053')
    print("MV2 Query Service (gRPC) corriendo en puerto 50053")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()