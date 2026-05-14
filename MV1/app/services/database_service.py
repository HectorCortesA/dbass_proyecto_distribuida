from app.database.connection import client, permissions_collection, users_collection

def create_database(user_id: str, db_name: str):
    # Validar entrada
    if not db_name:
        raise Exception("El nombre de la base de datos es requerido")

    database_name = f"{user_id}_{db_name}"
    db = client[database_name]

    # MongoDB crea la BD solo cuando hay datos
    db["init_collection"].insert_one({
        "initialized": True
    })

    # Guardar al creador como administrador en la colección de permisos
    permissions_collection.update_one(
        {"db_name": database_name, "user_id": user_id},
        {"$set": {"role": "administrador"}},
        upsert=True
    )

    return {
        "message": f"Base de datos '{db_name}' creada correctamente"
    }

def list_databases(user_id: str):
    # Buscar bases de datos a las que el usuario tiene acceso en la colección de permisos
    perms = list(permissions_collection.find({"user_id": user_id}))
    user_databases = [p["db_name"] for p in perms]

    # Retrocompatibilidad: Escanear nombres físicos en el cluster por si hay BDs antiguas
    try:
        all_physical_dbs = client.list_database_names()
        prefix = f"{user_id}_"
        for db in all_physical_dbs:
            if db.startswith(prefix) and db not in user_databases:
                user_databases.append(db)
                # Registrar el permiso faltante automáticamente
                permissions_collection.insert_one({
                    "db_name": db, 
                    "user_id": user_id, 
                    "role": "administrador"
                })
    except Exception as e:
        print(f"Error listando nombres físicos: {e}")

    return {
        "databases": user_databases
    }

def delete_database(user_id: str, db_name: str):
    # Verificamos si el usuario es administrador de esa BD
    perm = permissions_collection.find_one({
        "db_name": db_name, 
        "user_id": user_id, 
        "role": "administrador"
    })
    
    # Intento con prefijo por si el frontend mandó el nombre corto
    if not perm:
        full_name = f"{user_id}_{db_name}"
        perm = permissions_collection.find_one({
            "db_name": full_name, 
            "user_id": user_id, 
            "role": "administrador"
        })
        if perm:
            db_name = full_name

    if not perm:
        raise Exception("No tienes permisos para eliminar esta base de datos o no existe")

    # Eliminar físicamente y limpiar permisos
    client.drop_database(db_name)
    permissions_collection.delete_many({"db_name": db_name})

    return {
        "message": f"Base de datos '{db_name}' eliminada correctamente"
    }

def assign_database_access(db_name: str, target_email: str, role: str, current_user_id: str):
    # 1. Validar que el usuario actual tenga permisos de administrador sobre la BD
    admin_perm = permissions_collection.find_one({
        "db_name": db_name, 
        "user_id": current_user_id, 
        "role": "administrador"
    })
    
    if not admin_perm:
        raise Exception("Acceso denegado: Solo el dueño administrador puede compartir esta BD")
        
    # 2. Buscar al usuario invitado por su correo
    target_user = users_collection.find_one({"email": target_email})
    if not target_user:
        raise Exception("El correo del usuario invitado no está registrado en el sistema")
        
    # 3. Guardar o actualizar el permiso
    permissions_collection.update_one(
        {"db_name": db_name, "user_id": str(target_user["_id"])},
        {"$set": {"role": role}},
        upsert=True
    )
    
    return {"message": f"Acceso de tipo '{role}' asignado correctamente a {target_email}"}