import grpc
from concurrent import futures
import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

# Importamos el productor asíncrono
from app.rabbitmq.producer import publish_db_creation_task

class DatabaseServiceServicer(pb2_grpc.DatabaseServiceServicer):
    def CreateDatabase(self, request, context):
        # En lugar de crearlo secuencial, enviamos a RabbitMQ
        success = publish_db_creation_task(request.user_id, request.db_name)
        if success:
            return pb2.DbResponse(message="Creación de BD encolada exitosamente")
        return pb2.DbResponse(error="Fallo al encolar la tarea en RabbitMQ")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    print("MV1 Database Service (gRPC) corriendo en puerto 50052")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()