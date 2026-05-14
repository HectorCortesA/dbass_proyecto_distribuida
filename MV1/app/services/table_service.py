# app/services/table_service.py

from app.database.connection import client


def create_table(
    user_id: str,
    db_name: str,
    table_name: str
):

    database_name = f"{user_id}_{db_name}"

    db = client[database_name]

    db.create_collection(table_name)

    return {
        "message": f"Colección '{table_name}' creada"
    }


def list_tables(
    user_id: str,
    db_name: str
):

    database_name = f"{user_id}_{db_name}"

    db = client[database_name]

    collections = db.list_collection_names()

    return {
        "tables": collections
    }


def delete_table(
    user_id: str,
    db_name: str,
    table_name: str
):

    database_name = f"{user_id}_{db_name}"

    db = client[database_name]

    db.drop_collection(table_name)

    return {
        "message": f"Colección '{table_name}' eliminada"
    }