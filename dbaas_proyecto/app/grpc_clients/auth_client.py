import grpc
import os

import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc


class AuthClient:
    def __init__(self):

        # Lee la IP y el puerto de la MV3 desde las variables de entorno. 
        # Si no existe, usa "mv3_auth:50051" por defecto (nombre del contenedor en Docker).
        # Tiene que tener guion medio (-) aquí también
        host = os.getenv("AUTH_GRPC_HOST", "mv3-auth:50051")
        
        # Abre el canal de comunicación gRPC

        host = os.getenv("AUTH_GRPC_HOST", "mv3-auth:50051")

        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.AuthServiceStub(self.channel)

    def register(self, username, email, password, role):
        request = pb2.RegisterRequest(
            username=username, email=email, password=password, role=role
        )
        return self.stub.Register(request)

    def login(self, email, password):
        request = pb2.LoginRequest(email=email, password=password)
        return self.stub.Login(request)

    def get_all_users(self):
        return self.stub.GetAllUsers(pb2.EmptyRequest())