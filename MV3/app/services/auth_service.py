from app.database.connection import users_collection
from app.auth.security import (
    get_password_hash,  # Usando el nombre común en tu proyecto anterior
    verify_password,
    create_access_token
)
from app.auth.schemas import UserRegister, UserLogin

def register_user(user_data: UserRegister):
    """
    Registra un nuevo usuario en la base de datos centralizada.
    """
    # 1. Verificar si el usuario ya existe
    existing_user = users_collection.find_one({
        "email": user_data.email
    })

    if existing_user:
        return {"error": "El correo electrónico ya está registrado"}

    # 2. Validar longitud de contraseña para bcrypt (máximo 72 bytes)
    if len(user_data.password.encode('utf-8')) > 72:
        return {"error": "La contraseña es demasiado larga (máximo 72 caracteres)"}

    # 3. Crear el nuevo usuario con la contraseña hasheada
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "role": user_data.role if user_data.role else "usuario" # Rol por defecto
    }

    # 4. Insertar en MongoDB
    users_collection.insert_one(new_user)

    return {"message": "Usuario registrado exitosamente"}


def login_user(user_data: UserLogin):
    """
    Valida credenciales y genera un token JWT.
    """
    # 1. Buscar el usuario por email
    db_user = users_collection.find_one({
        "email": user_data.email
    })

    if not db_user:
        return {"error": "Usuario no encontrado"}

    # 2. Verificar la contraseña
    is_valid = verify_password(user_data.password, db_user["password"])

    if not is_valid:
        return {"error": "Contraseña incorrecta"}

    # 3. Crear el payload del token
    # Convertimos el ObjectId de Mongo a string para el JWT
    token_data = {
        "id": str(db_user["_id"]),
        "email": db_user["email"],
        "role": db_user.get("role", "usuario")
    }

    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login exitoso"
    }