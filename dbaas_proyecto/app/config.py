from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

DATABASE_NAME = os.getenv("DATABASE_NAME")

JWT_SECRET = os.getenv("JWT_SECRET")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

JWT_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES")
)