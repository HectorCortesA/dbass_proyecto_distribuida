import grpc
import json
from concurrent import futures

import app.proto_generated.dbaas_pb2 as pb2
import app.proto_generated.dbaas_pb2_grpc as pb2_grpc

from app.rabbitmq.producer import (
    publish_db_creation_task,
    publish_table_creation_task,
    publish_insert_task,
)
from app.services.database_service import (
    list_databases,
    delete_database,
    assign_database_access,
)
from app.services.collection_service import (
    create_collection,
    list_collections,
    delete_collection,
)
from app.services.document_service import (
    insert_document,
    find_documents,
    update_document,
    delete_document,
)


class DatabaseServiceServicer(pb2_grpc.DatabaseServiceServicer):

    # --------------------------------------------------
    # BASES DE DATOS
    # --------------------------------------------------

    def CreateDatabase(self, request, context):
        success = publish_db_creation_task(request.user_id, request.db_name)
        if success:
            return pb2.DbResponse(message="Creación de BD encolada exitosamente")
        return pb2.DbResponse(error="Fallo al encolar la tarea en RabbitMQ")

    def ListDatabases(self, request, context):
        try:
            result = list_databases(request.user_id)
            return pb2.ListDbResponse(databases=result["databases"])
        except Exception as e:
            return pb2.ListDbResponse(error=str(e))

    def DeleteDatabase(self, request, context):
        try:
            result = delete_database(request.user_id, request.db_name)
            return pb2.DbResponse(message=result["message"])
        except Exception as e:
            return pb2.DbResponse(error=str(e))

    def AssignAccess(self, request, context):
        try:
            result = assign_database_access(
                db_name=request.db_name,
                target_email=request.target_email,
                role=request.role,
                current_user_id=request.current_user_id,
            )
            return pb2.DbResponse(message=result["message"])
        except Exception as e:
            return pb2.DbResponse(error=str(e))

    # --------------------------------------------------
    # COLECCIONES
    # --------------------------------------------------

    def CreateCollection(self, request, context):
        success = publish_table_creation_task(
            user_id=request.user_id,
            db_name=request.db_name,
            collection_name=request.collection_name,
        )
        if success:
            return pb2.DbResponse(message="Creación de colección encolada exitosamente")
        return pb2.DbResponse(error="Fallo al encolar la creación de colección en RabbitMQ")

    def ListCollections(self, request, context):
        try:
            result = list_collections(
                db_name=request.db_name,
                owner_id=request.user_id,
            )
            return pb2.CollectionListResponse(collections=result["collections"])
        except Exception as e:
            return pb2.CollectionListResponse(error=str(e))

    def DeleteCollection(self, request, context):
        try:
            result = delete_collection(
                db_name=request.db_name,
                collection_name=request.collection_name,
                owner_id=request.user_id,
            )
            return pb2.DbResponse(message=result["message"])
        except Exception as e:
            return pb2.DbResponse(error=str(e))

    # --------------------------------------------------
    # DOCUMENTOS
    # --------------------------------------------------

    def InsertDocument(self, request, context):
        try:
            document = json.loads(request.document_json)
            success = publish_insert_task(
                db_name=request.db_name,
                collection_name=request.collection_name,
                document=document,
                owner_id=request.owner_id,
            )
            if success:
                return pb2.DocResponse(message="Inserción de documento encolada exitosamente", id="async-enqueued")
            return pb2.DocResponse(error="Fallo al encolar la inserción en RabbitMQ")
        except Exception as e:
            return pb2.DocResponse(error=str(e))

    def FindDocuments(self, request, context):
        try:
            result = find_documents(
                db_name=request.db_name,
                collection_name=request.collection_name,
                owner_id=request.owner_id,
            )
            return pb2.DocsResponse(data_json=json.dumps(result["data"]))
        except Exception as e:
            return pb2.DocsResponse(error=str(e))

    def UpdateDocument(self, request, context):
        try:
            filter_query = json.loads(request.filter_json)
            new_data = json.loads(request.new_data_json)
            result = update_document(
                db_name=request.db_name,
                collection_name=request.collection_name,
                filter_query=filter_query,
                new_data=new_data,
                owner_id=request.owner_id,
            )
            return pb2.DocResponse(
                message=result["message"],
                modified_count=str(result.get("modified_count", 0)),
            )
        except Exception as e:
            return pb2.DocResponse(error=str(e))

    def DeleteDocument(self, request, context):
        try:
            filter_query = json.loads(request.filter_json)
            result = delete_document(
                db_name=request.db_name,
                collection_name=request.collection_name,
                filter_query=filter_query,
                owner_id=request.owner_id,
            )
            return pb2.DocResponse(
                message=result["message"],
                deleted_count=str(result.get("deleted_count", 0)),
            )
        except Exception as e:
            return pb2.DocResponse(error=str(e))


import threading
from app.rabbitmq.worker import start_worker

def serve():
    # Arrancar el worker de RabbitMQ en un hilo en segundo plano
    worker_thread = threading.Thread(target=start_worker, daemon=True)
    worker_thread.start()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseServiceServicer(), server)
    server.add_insecure_port("[::]:50052")
    print("MV1 Database Service (gRPC) corriendo en puerto 50052")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()