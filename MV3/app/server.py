import grpc
from concurrent import futures

import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

from app.services.auth_service import register_user, login_user
from app.auth.schemas import UserRegister, UserLogin
from app.database.connection import users_collection


class AuthServiceServicer(pb2_grpc.AuthServiceServicer):

    def Register(self, request, context):
        user_schema = UserRegister(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role,
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

    def GetAllUsers(self, request, context):
        try:
            users = list(
                users_collection.find({}, {"_id": 0, "email": 1, "username": 1})
            )
            user_protos = [
                pb2.UserInfo(username=u.get("username", ""), email=u.get("email", ""))
                for u in users
            ]
            return pb2.UsersResponse(users=user_protos)
        except Exception as e:
            return pb2.UsersResponse(error=str(e))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("MV3 Auth Service (gRPC) corriendo en puerto 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()