import grpc
import os
import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

class DbClient:
    def __init__(self):
        # Apunta al contenedor MV1
        host = os.getenv("DB_GRPC_HOST", "mv1_database:50052")
        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.DatabaseServiceStub(self.channel)

    def create_database(self, user_id, db_name):
        request = pb2.CreateDbRequest(
            user_id=user_id, 
            db_name=db_name
        )
        return self.stub.CreateDatabase(request)

    # Nota: A medida que agregues más funciones a tu dbaas.proto 
    # (como crear colecciones o insertar documentos), las irás definiendo aquí.
    # Ejemplo de cómo se vería en el futuro:
    #
    # def create_collection(self, user_id, db_name, collection_name):
    #     request = pb2.CreateCollectionRequest(...)
    #     return self.stub.CreateCollection(request)