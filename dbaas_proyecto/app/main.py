from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importación de los routers de la API v1
# Se utiliza 'db_routes' siguiendo tu corrección de nombre de archivo
from app.api.v1 import (
    auth_routes,
    db_routes,
    collection_routes,
    document_routes,
    query_routes,
    sql_routes
)

app = FastAPI(
    title="DBaaS API Gateway",
    description="Punto de entrada único para la arquitectura de microservicios distribuida",
    version="1.0.0"
)

# =================================================
# 1. Configuración de CORS
# =================================================
# Mantenemos la configuración que tenías en tu monolito original
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================
# 2. Inclusión de Routers (Endpoints del Gateway)
# =================================================

# Rutas de Autenticación (Redirige a MV3)
app.include_router(
    auth_routes.router, 
    prefix="/auth", 
    tags=["Authentication"]
)

# Rutas de Base de Datos (Redirige a MV1)
app.include_router(
    db_routes.router, 
    prefix="/db", 
    tags=["Database"]
)

# Rutas de Colecciones (Redirige a MV1)
app.include_router(
    collection_routes.router, 
    prefix="/collection", 
    tags=["Collections"]
)

# Rutas de Documentos / CRUD (Redirige a MV1)
app.include_router(
    document_routes.router, 
    prefix="/document", 
    tags=["Documents"]
)

# Rutas de Consultas y MPI (Redirige a MV2)
app.include_router(
    query_routes.router, 
    prefix="/query", 
    tags=["Queries"]
)

# Interfaz SQL-like abstracta
app.include_router(
    sql_routes.router, 
    prefix="/sql", 
    tags=["SQL Interface"]
)

# =================================================
# 3. Endpoint de Verificación (Health Check)
# =================================================
@app.get("/")
def home():
    """
    Indica que el Gateway está operativo.
    """
    return {
        "message": "DBaaS API Gateway Running",
        "status": "Online"
    }