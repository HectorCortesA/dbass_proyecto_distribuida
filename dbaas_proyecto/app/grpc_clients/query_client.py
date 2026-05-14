import grpc
import json
import os

import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc


class QueryClient:
    def __init__(self):
        host = os.getenv("QUERY_GRPC_HOST", "mv2-query:50053")
        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.QueryServiceStub(self.channel)

    def get_sum(self, user_id, db_name, table_name, field):
        return self.stub.AggregateSum(
            pb2.QueryRequest(
                user_id=user_id, db_name=db_name,
                table_name=table_name, field=field,
            )
        )

    def get_count(self, user_id, db_name, table_name):
        return self.stub.AggregateSum(
            pb2.QueryRequest(
                user_id=user_id, db_name=db_name,
                table_name=table_name, field="COUNT",
            )
        )

    def get_avg(self, user_id, db_name, table_name, field):
        return self.stub.AggregateSum(
            pb2.QueryRequest(
                user_id=user_id, db_name=db_name,
                table_name=table_name, field=f"AVG:{field}",
            )
        )

    def filter_documents(self, db_name, collection_name, filters, owner_id):
        return self.stub.FilterDocuments(
            pb2.FilterRequest(
                db_name=db_name,
                collection_name=collection_name,
                filters_json=json.dumps(filters),
                owner_id=owner_id,
            )
        )

    def aggregate_documents(self, db_name, collection_name, pipeline, owner_id):
        return self.stub.AggregateDocuments(
            pb2.AggregateRequest(
                db_name=db_name,
                collection_name=collection_name,
                pipeline_json=json.dumps(pipeline),
                owner_id=owner_id,
            )
        )

    def distinct_values(self, user_id, db_name, table_name, field):
        return self.stub.DistinctValues(
            pb2.QueryRequest(
                user_id=user_id, db_name=db_name,
                table_name=table_name, field=field,
            )
        )

    def inner_join(self, user_id, db_name, table_name, from_table,
                   local_field, foreign_field, as_name):
        return self.stub.InnerJoin(
            pb2.JoinRequest(
                user_id=user_id, db_name=db_name,
                table_name=table_name, from_table=from_table,
                local_field=local_field, foreign_field=foreign_field,
                as_name=as_name,
            )
        )