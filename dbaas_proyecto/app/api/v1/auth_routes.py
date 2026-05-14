from fastapi import APIRouter, HTTPException
from app.auth.schemas import UserRegister, UserLogin
from app.grpc_clients.auth_client import AuthClient

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