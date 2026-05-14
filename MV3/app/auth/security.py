from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# =========================
# Configuración de bcrypt
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =========================
# Configuración JWT
# =========================

SECRET_KEY = "mi_clave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =========================
# Hash de contraseña
# =========================

def hash_password(password: str):

    return pwd_context.hash(password)

# =========================
# Verificar contraseña
# =========================

def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# =========================
# Crear token JWT
# =========================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt