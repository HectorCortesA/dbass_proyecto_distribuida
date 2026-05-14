# app/middleware/jwt_middleware.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

# Importamos las configuraciones de JWT desde tu archivo de seguridad
from app.auth.security import SECRET_KEY, ALGORITHM

# Instanciamos el esquema de seguridad (Bearer Token)
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Decodificamos el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extraemos los datos que guardaste al hacer el login
        user_id: str = payload.get("id")
        user_role: str = payload.get("role")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
            
        # Retornamos el diccionario que leerán tus rutas y el role_middleware
        return {
            "id": user_id,
            "role": user_role
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado o inválido"
        )