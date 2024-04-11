from motor.motor_asyncio import AsyncIOMotorClient

import os
from dotenv import load_dotenv


load_dotenv()

# new structure
def get_db_client():
    MONGO_URL = os.getenv("MONGO_URL")
    client = AsyncIOMotorClient(MONGO_URL)
    return client


users_database = get_db_client().Users
user_collection = users_database.users

property_database = get_db_client().Properties
property_collection = property_database.properties

