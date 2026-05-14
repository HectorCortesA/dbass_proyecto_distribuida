from app.database.connection import (
    users_collection
)

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)

def register_user(user):

    existing_user = users_collection.find_one({
        "email": user.email
    })

    if existing_user:

        return {
            "error": "Usuario ya existe"
        }

    new_user = {

        "username": user.username,

        "email": user.email,

        "password": hash_password(
            user.password
        ),

        "role": user.role
    }

    users_collection.insert_one(
        new_user
    )

    return {
        "message": "Usuario creado"
    }


def login_user(user):

    db_user = users_collection.find_one({
        "email": user.email
    })

    if not db_user:

        return {
            "error": "Usuario no encontrado"
        }

    valid_password = verify_password(
        user.password,
        db_user["password"]
    )

    if not valid_password:

        return {
            "error": "Contraseña incorrecta"
        }

    token = create_access_token({

        "id": str(db_user["_id"]),

        "email": db_user["email"],

        "role": db_user["role"]

    })

    return {

        "access_token": token,

        "token_type": "bearer"
    }