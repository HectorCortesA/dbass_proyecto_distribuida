import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb_core:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "dbaas_db")
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))