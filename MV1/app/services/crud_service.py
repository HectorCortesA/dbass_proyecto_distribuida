# app/services/crud_service.py

from app.database.connection import client
from bson import ObjectId


def insert_data(
    user_id: str,
    db_name: str,
    table_name: str,
    data: dict
):

    database_name = f"{user_id}_{db_name}"

    db = client[database_name]

    collection = db[table_name]

    result = collection.insert_one(data)

    return {
        "message": "Documento insertado",
        "id": str(result.inserted_id)
    }


def find_data(
    user_id: str,
    db_name: str,
    table_name: str,
    filters: dict = {}
):

    database_name = f"{user_id}_{db_name}"

    db = client[database_name]

    collection = db[table_name]

    documents = list(collection.find(filters))

    for doc in documents:
        doc["_id"] = str(doc["_id"])

    return {
        "data": documents
    }


def update_data(
    user_id: str,
    db_name: str,
    table_name: str,
    document_id: str,
    data: dict
):

    database_name = f"{user_id}_{db_name}"

    db = client[database_name]

    collection = db[table_name]

    result = collection.update_one(
        {
            "_id": ObjectId(document_id)
        },
        {
            "$set": data
        }
    )

    return {
        "message": "Documento actualizado",
        "modified_count": result.modified_count
    }


def delete_data(
    user_id: str,
    db_name: str,
    table_name: str,
    document_id: str
):

    database_name = f"{user_id}_{db_name}"

    db = client[database_name]

    collection = db[table_name]

    result = collection.delete_one(
        {
            "_id": ObjectId(document_id)
        }
    )

    return {
        "message": "Documento eliminado",
        "deleted_count": result.deleted_count
    }