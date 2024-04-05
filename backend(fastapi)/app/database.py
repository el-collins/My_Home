from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import settings

def get_db_client():
    return AsyncIOMotorClient(settings.mongodb_url)

# Additional database utility functions would go here...