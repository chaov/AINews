from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


database = Database()


async def connect_to_mongodb():
    database.client = AsyncIOMotorClient(settings.MONGODB_URL)
    database.db = database.client[settings.MONGODB_DB_NAME]
    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongodb_connection():
    if database.client:
        database.client.close()
        print("Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    return database.db
