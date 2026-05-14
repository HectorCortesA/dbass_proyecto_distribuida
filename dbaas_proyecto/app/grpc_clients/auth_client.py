import grpc
import os
import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

class AuthClient:
    def __init__(self):
        # host debe ser el nombre del servicio en docker-compose
        host = os.getenv("AUTH_GRPC_HOST", "mv3-auth:50051")
        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.AuthServiceStub(self.channel)

    def register(self, username, email, password, role):
        request = pb2.RegisterRequest(username=username, email=email, password=password, role=role)
        return self.stub.Register(request)

    def login(self, email, password):
        request = pb2.LoginRequest(email=email, password=password)
        return self.stub.Login(request)