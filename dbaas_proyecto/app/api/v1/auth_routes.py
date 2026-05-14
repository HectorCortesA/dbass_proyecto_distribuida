from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth_schema import UserRegister, UserLogin 
from app.grpc_clients.auth_client import AuthClient
from app.middleware.jwt_middleware import get_current_user

router = APIRouter()
auth_grpc = AuthClient()

@router.post("/register")
def register(user: UserRegister):
    response = auth_grpc.register(
        username=user.username,
        email=user.email,
        password=user.password,
        role=user.role
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error)
    return {"message": response.message}

@router.post("/login")
def login(user: UserLogin):
    response = auth_grpc.login(email=user.email, password=user.password)
    if response.error:
        raise HTTPException(status_code=401, detail=response.error)
    return {"access_token": response.access_token, "token_type": "bearer"}

@router.get("/users")
def get_all_users(current_user: dict = Depends(get_current_user)):
    response = auth_grpc.get_all_users()
    if response.error:
        raise HTTPException(status_code=500, detail=response.error)
    users = [{"username": u.username, "email": u.email} for u in response.users]
    return {"users": users}