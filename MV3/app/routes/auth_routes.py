from fastapi import APIRouter

# NUEVO: Importamos la colección de usuarios para que get_all_users funcione
from app.database.connection import users_collection 

from app.auth.schemas import (
    UserRegister,
    UserLogin
)

from app.services.auth_service import (
    register_user,
    login_user
)

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    return register_user(user)

@router.post("/login")
def login(user: UserLogin):
    return login_user(user)

@router.get("/users")
def get_all_users():
    try:
        # Buscamos todos los usuarios, devolviendo solo email y username
        users = list(users_collection.find({}, {"_id": 0, "email": 1, "username": 1}))
        return {"users": users}
    except Exception as e:
        # Si algo falla en Mongo, mandamos la lista vacía para no romper el Frontend
        return {"users": []}