from app.database.connection import client, permissions_collection, users_collection
from fastapi import HTTPException

def create_database(user_id: str, db_name: str):
    database_name = f"{user_id}_{db_name}"
    db = client[database_name]

    db["init_collection"].insert_one({
        "initialized": True
    })

    # NUEVO: Guardar al creador como administrador
    permissions_collection.insert_one({
        "db_name": database_name,
        "user_id": user_id,
        "role": "administrador"
    })

    return {
        "message": f"Base de datos '{db_name}' creada correctamente"
    }

def list_databases(user_id: str):
    # NUEVO: Buscar bases de datos a las que el usuario tiene acceso
    perms = list(permissions_collection.find({"user_id": user_id}))
    
    # Devolvemos el nombre físico real (ej. "tuId_ventas")
    user_databases = [p["db_name"] for p in perms]

    # Retrocompatibilidad: Si tenías bases de datos creadas antes de esta actualización
    databases = client.list_database_names()
    prefix = f"{user_id}_"
    for db in databases:
        if db.startswith(prefix) and db not in user_databases:
            user_databases.append(db)
            permissions_collection.insert_one({
                "db_name": db, "user_id": user_id, "role": "administrador"
            })

    return {
        "databases": user_databases
    }

def delete_database(user_id: str, db_name: str):
    # Como el frontend ahora envía el nombre físico completo (ej. "tuId_ventas"), 
    # validamos que exista en la tabla de permisos como administrador
    perm = permissions_collection.find_one({
        "db_name": db_name, "user_id": user_id, "role": "administrador"
    })
    
    # Fallback por si el frontend mandó el nombre sin prefijo
    if not perm:
        db_name = f"{user_id}_{db_name}"
        perm = permissions_collection.find_one({
            "db_name": db_name, "user_id": user_id, "role": "administrador"
        })

    if not perm:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar esta base de datos")

    client.drop_database(db_name)
    permissions_collection.delete_many({"db_name": db_name})

    return {
        "message": f"Base de datos eliminada"
    }

def assign_database_access(db_name: str, target_email: str, role: str, current_user_id: str):
    # 1. Validar que quien asigna sea el dueño (administrador)
    if not db_name.startswith(f"{current_user_id}_"):
        db_name = f"{current_user_id}_{db_name}"

    admin_perm = permissions_collection.find_one({
        "db_name": db_name, "user_id": current_user_id, "role": "administrador"
    })
    if not admin_perm:
        raise HTTPException(status_code=403, detail="Solo el administrador puede compartir esta BD")
        
    # 2. Buscar al usuario invitado
    target_user = users_collection.find_one({"email": target_email})
    if not target_user:
        raise HTTPException(status_code=404, detail="El correo del usuario no existe")
        
    # 3. Guardar el permiso
    permissions_collection.update_one(
        {"db_name": db_name, "user_id": str(target_user["_id"])},
        {"$set": {"role": role}},
        upsert=True
    )
    return {"message": f"Acceso asignado correctamente a {target_email}"}