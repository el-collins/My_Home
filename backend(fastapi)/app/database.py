from motor.motor_asyncio import AsyncIOMotorClient
# from app.settings import settings

import os
from dotenv import load_dotenv


load_dotenv()


# old structure
# def connectToDB():
#     MONGO_URL = os.getenv("MONGO_URL")
#     client = AsyncIOMotorClient(MONGO_URL)
#     database = client.Users
#     user_collection = database.users
#     print("Successfully connected")
#     return user_collection
# user_collection = connectToDB()

# new structure
def get_db_client():
    MONGO_URL = os.getenv("MONGO_URL")
    client = AsyncIOMotorClient(MONGO_URL)
    return client

users_database = get_db_client().Users
user_collection = users_database.users

async def get_user(email: str):
    user = await user_collection.find_one({"email": email})
    return user



async def register_user(user_data):
    try:
        result = await user_collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id  # Add the database-generated ID to user data
        return user_data
    except Exception as e:
        raise ValueError("Failed to register user") from e

