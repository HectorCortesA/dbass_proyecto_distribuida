from pymongo import MongoClient

from app.config import (
    MONGO_URL,
    DATABASE_NAME
)

client = MongoClient(MONGO_URL)

db = client[DATABASE_NAME]

users_collection = db["users"]
permissions_collection = db["permissions"]