from fastapi import APIRouter, Depends

# 1. IMPORTACIONES CORREGIDAS PARA MIDDLEWARES
from app.middleware.role_middleware import require_admin
from app.middleware.jwt_middleware import get_current_user

# 2. IMPORTACIONES CORREGIDAS PARA ESQUEMAS (Agregado AssignAccessSchema)
from app.schemas.database_schema import (
    CreateDatabaseSchema,
    DeleteDatabaseSchema,
    AssignAccessSchema
)

# 3. IMPORTACIONES CORREGIDAS PARA SERVICIOS (Agregado assign_database_access)
from app.services.database_service import (
    create_database,
    list_databases,
    delete_database,
    assign_database_access
)

router = APIRouter(
    prefix="/db",
    tags=["Database"]
)

# Crear base de datos (Requiere Admin absoluto)
@router.post("/create")
def create_new_database(
    data: CreateDatabaseSchema,
    current_user: dict = Depends(require_admin)
):
    return create_database(
        db_name=data.db_name,
        user_id=current_user["id"] 
    )

# Listar bases de datos (Cualquier usuario para que los invitados vean sus tablas compartidas)
@router.get("/list")
def get_databases(
    current_user: dict = Depends(get_current_user) # <-- CAMBIADO A get_current_user
):
    return list_databases(
        user_id=current_user["id"] 
    )

# Eliminar base de datos (Requiere Admin absoluto)
@router.delete("/delete")
def remove_database(
    data: DeleteDatabaseSchema,
    current_user: dict = Depends(require_admin)
):
    return delete_database(
        db_name=data.db_name,
        user_id=current_user["id"] 
    )

# Asignar permisos (Valida internamente que quien lo envía sea el dueño)
@router.post("/assign")
def assign_access(
    data: AssignAccessSchema, 
    current_user: dict = Depends(get_current_user)
):
    return assign_database_access(
        db_name=data.db_name, 
        target_email=data.target_email, 
        role=data.role, 
        current_user_id=current_user["id"]
    )