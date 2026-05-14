from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import (
    auth_routes,
    db_routes,
    collection_routes,
    document_routes,
    query_routes
)

app = FastAPI(title="DBaaS API Gateway Corregido")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================
# REGISTRO DE RUTAS (Soporte Dual para Auth)
# =================================================

# 1. Registramos para el frontend viejo (/Authentication)
app.include_router(auth_routes.router, prefix="/Authentication", tags=["Authentication"])

# 2. Registramos para el frontend nuevo (/auth) -> ESTO QUITA EL ERROR 404
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])

# Resto de rutas
app.include_router(db_routes.router, prefix="/db", tags=["Database"])
app.include_router(collection_routes.router, prefix="/collection", tags=["Collections"])
app.include_router(document_routes.router, prefix="/document", tags=["Documents"])
app.include_router(query_routes.router, prefix="/query", tags=["Queries"])

@app.get("/")
def home():
    return {"message": "API Gateway Operativo con soporte /auth y /Authentication"}