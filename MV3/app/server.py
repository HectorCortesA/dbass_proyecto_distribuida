import grpc
from concurrent import futures
import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

# Importas tu código actual de auth_service
from app.services.auth_service import register_user, login_user
from app.auth.schemas import UserRegister, UserLogin

class AuthServiceServicer(pb2_grpc.AuthServiceServicer):
    def Register(self, request, context):
        user_schema = UserRegister(
            username=request.username, email=request.email, 
            password=request.password, role=request.role
        )
        res = register_user(user_schema)
        if "error" in res:
            return pb2.AuthResponse(error=res["error"])
        return pb2.AuthResponse(message=res["message"])

    def Login(self, request, context):
        user_schema = UserLogin(email=request.email, password=request.password)
        res = login_user(user_schema)
        if "error" in res:
            return pb2.AuthResponse(error=res["error"])
        return pb2.AuthResponse(access_token=res["access_token"])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("MV3 Auth Service (gRPC) corriendo en puerto 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()