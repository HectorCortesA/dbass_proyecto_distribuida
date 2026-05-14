# app/services/document_service.py

from app.database.connection import client, permissions_collection
from bson import ObjectId
from fastapi import HTTPException

# NUEVA FUNCIÓN: Verifica si el usuario tiene permiso (ya sea como admin o invitado)
def check_db_permission(db_name: str, user_id: str, required_role: str):
    perm = permissions_collection.find_one({"db_name": db_name, "user_id": user_id})
    
    if not perm:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta base de datos")
    
    # Si requiere escritura (para Insertar/Actualizar/Borrar), pero el usuario es solo lectura, bloqueamos
    if required_role == "escritura" and perm["role"] == "lectura":
        raise HTTPException(status_code=403, detail="Solo tienes permiso de lectura en esta base de datos")
    
    return True

def insert_document(db_name: str, collection_name: str, document: dict, owner_id: str):
    # Validamos permisos de escritura
    check_db_permission(db_name, owner_id, "escritura")
    
    # CAMBIO CRÍTICO: Usamos db_name directamente
    db = client[db_name]
    result = db[collection_name].insert_one(document)
    
    return {
        "message": "Documento insertado",
        "id": str(result.inserted_id)
    }

def find_documents(db_name: str, collection_name: str, owner_id: str):
    # Validamos permisos de lectura (ambos roles pueden leer)
    check_db_permission(db_name, owner_id, "lectura")
    
    # CAMBIO CRÍTICO: Usamos db_name directamente
    db = client[db_name]
    documents = list(db[collection_name].find({}))
    for doc in documents:
        doc["_id"] = str(doc["_id"])
        
    return {"data": documents}

def update_document(db_name: str, collection_name: str, filter_query: dict, new_data: dict, owner_id: str):
    # Validamos permisos de escritura
    check_db_permission(db_name, owner_id, "escritura")
    
    # CAMBIO CRÍTICO: Usamos db_name directamente
    db = client[db_name]
    
    if "_id" in filter_query and isinstance(filter_query["_id"], str):
        filter_query["_id"] = ObjectId(filter_query["_id"])

    result = db[collection_name].update_many(filter_query, {"$set": new_data})
    
    return {
        "message": "Documento(s) actualizado(s)",
        "modified_count": result.modified_count
    }

def delete_document(db_name: str, collection_name: str, filter_query: dict, owner_id: str):
    # Validamos permisos de escritura
    check_db_permission(db_name, owner_id, "escritura")
    
    # CAMBIO CRÍTICO: Usamos db_name directamente
    db = client[db_name]
    
    if "_id" in filter_query and isinstance(filter_query["_id"], str):
        filter_query["_id"] = ObjectId(filter_query["_id"])

    result = db[collection_name].delete_many(filter_query)
    
    return {
        "message": "Documento(s) eliminado(s)",
        "deleted_count": result.deleted_count
    }