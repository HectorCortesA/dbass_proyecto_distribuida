import grpc
import os
import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

class QueryClient:
    def __init__(self):
        # Apunta al contenedor MV2
        host = os.getenv("QUERY_GRPC_HOST", "mv2_query:50053")
        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.QueryServiceStub(self.channel)

    def get_sum(self, user_id, db_name, table_name, field):
        # Llama a la agregación que disparará MPI en la MV2
        request = pb2.QueryRequest(
            user_id=user_id,
            db_name=db_name,
            table_name=table_name,
            field=field
        )
        return self.stub.AggregateSum(request)