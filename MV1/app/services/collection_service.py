from app.database.connection import client, permissions_collection
from fastapi import HTTPException

# Función inteligente para evitar el doble prefijo
def get_real_db_name(db_name: str, user_id: str) -> str:
    # 1. Si el nombre YA empieza con el ID del usuario, no lo duplicamos (Evita el ID_ID_Nombre de tu foto)
    if db_name.startswith(f"{user_id}_"):
        return db_name
        
    # 2. Si el frontend mandó el nombre corto (ej. al crear la DB por primera vez), le ponemos el prefijo
    prefixed_name = f"{user_id}_{db_name}"
    if permissions_collection.find_one({"db_name": prefixed_name}):
        return prefixed_name
        
    # 3. Si es una base de datos compartida, el frontend ya manda el nombre completo correcto
    return db_name

def check_db_permission(db_name: str, user_id: str, required_role: str):
    perm = permissions_collection.find_one({"db_name": db_name, "user_id": user_id})
    if not perm:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta base de datos")
    
    if required_role == "escritura" and perm["role"] == "lectura":
        raise HTTPException(status_code=403, detail="Solo tienes permiso de lectura")
    return True

def create_collection(db_name: str, collection_name: str, owner_id: str):
    real_db_name = get_real_db_name(db_name, owner_id)
    check_db_permission(real_db_name, owner_id, "escritura")
    
    db = client[real_db_name]
    db.create_collection(collection_name)
    
    return {"message": f"Colección '{collection_name}' creada exitosamente"}

def list_collections(db_name: str, owner_id: str):
    real_db_name = get_real_db_name(db_name, owner_id)
    check_db_permission(real_db_name, owner_id, "lectura")
    
    db = client[real_db_name]
    collections = db.list_collection_names()
    
    # Filtramos la colección interna de inicialización
    return {"collections": [c for c in collections if c != "init_collection" and c != "init"]}

def delete_collection(db_name: str, collection_name: str, owner_id: str):
    real_db_name = get_real_db_name(db_name, owner_id)
    check_db_permission(real_db_name, owner_id, "escritura")
    
    db = client[real_db_name]
    db.drop_collection(collection_name)
    
    return {"message": f"Colección '{collection_name}' eliminada"}