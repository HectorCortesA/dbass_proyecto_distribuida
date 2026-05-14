import grpc
import json
import os

import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc


class DbClient:
    def __init__(self):
        host = os.getenv("DB_GRPC_HOST", "mv1-database:50052")
        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.DatabaseServiceStub(self.channel)

    # --------------------------------------------------
    # BASES DE DATOS
    # --------------------------------------------------

    def create_database(self, user_id, db_name):
        return self.stub.CreateDatabase(
            pb2.CreateDbRequest(user_id=user_id, db_name=db_name)
        )

    def list_databases(self, user_id):
        return self.stub.ListDatabases(pb2.UserRequest(user_id=user_id))

    def delete_database(self, user_id, db_name):
        return self.stub.DeleteDatabase(
            pb2.DeleteDbRequest(user_id=user_id, db_name=db_name)
        )

    def assign_access(self, db_name, target_email, role, current_user_id):
        return self.stub.AssignAccess(
            pb2.AssignAccessRequest(
                db_name=db_name,
                target_email=target_email,
                role=role,
                current_user_id=current_user_id,
            )
        )

    # --------------------------------------------------
    # COLECCIONES
    # --------------------------------------------------

    def create_collection(self, user_id, db_name, collection_name):
        return self.stub.CreateCollection(
            pb2.CollectionRequest(
                user_id=user_id, db_name=db_name, collection_name=collection_name
            )
        )

    def list_collections(self, user_id, db_name):
        return self.stub.ListCollections(
            pb2.CollectionListRequest(user_id=user_id, db_name=db_name)
        )

    def delete_collection(self, user_id, db_name, collection_name):
        return self.stub.DeleteCollection(
            pb2.CollectionRequest(
                user_id=user_id, db_name=db_name, collection_name=collection_name
            )
        )

    # --------------------------------------------------
    # DOCUMENTOS
    # --------------------------------------------------

    def insert_document(self, db_name, collection_name, document, owner_id):
        return self.stub.InsertDocument(
            pb2.InsertDocRequest(
                db_name=db_name,
                collection_name=collection_name,
                document_json=json.dumps(document),
                owner_id=owner_id,
            )
        )

    def find_documents(self, db_name, collection_name, owner_id):
        return self.stub.FindDocuments(
            pb2.FindDocRequest(
                db_name=db_name,
                collection_name=collection_name,
                owner_id=owner_id,
            )
        )

    def update_document(self, db_name, collection_name, filter_query, new_data, owner_id):
        return self.stub.UpdateDocument(
            pb2.UpdateDocRequest(
                db_name=db_name,
                collection_name=collection_name,
                filter_json=json.dumps(filter_query),
                new_data_json=json.dumps(new_data),
                owner_id=owner_id,
            )
        )

    def delete_document(self, db_name, collection_name, filter_query, owner_id):
        return self.stub.DeleteDocument(
            pb2.DeleteDocRequest(
                db_name=db_name,
                collection_name=collection_name,
                filter_json=json.dumps(filter_query),
                owner_id=owner_id,
            )
        )