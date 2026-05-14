from fastapi import HTTPException, Depends
from app.middleware.jwt_middleware import get_current_user

def require_admin(current_user: dict = Depends(get_current_user)):
    """Solo el administrador puede acceder"""
    if current_user.get("role") != "administrador":
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: Requiere rol de administrador"
        )
    return current_user

def require_write(current_user: dict = Depends(get_current_user)):
    """Administradores y usuarios de escritura pueden acceder"""
    role = current_user.get("role")
    if role not in ["administrador", "usuario de escritura"]:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: Requiere permisos de escritura"
        )
    return current_user

def require_read(current_user: dict = Depends(get_current_user)):
    """Cualquier usuario autenticado con un rol válido puede leer"""
    role = current_user.get("role")
    if role not in ["administrador", "usuario de escritura", "usuario de lectura"]:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: Requiere permisos de lectura"
        )
    return current_user