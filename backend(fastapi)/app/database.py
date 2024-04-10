from motor.motor_asyncio import AsyncIOMotorClient
from app.models import PropertyCreate
# from app.settings import settings
import uuid

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

property_database = get_db_client().Properties
property_collection = property_database.properties


async def get_user(email: str):
    user = await user_collection.find_one({"email": email})
    return user


async def register_user(user_data):
    try:
        result = await user_collection.insert_one(user_data)
        # Add the database-generated ID to user data
        user_data["_id"] = result.inserted_id
        return user_data
    except Exception as e:
        raise ValueError("Failed to register user") from e


async def create_property(property_data: PropertyCreate):
    return {"property_details": property_data}


async def get_property(property_id: str) -> dict:
    property_data = await property_collection.find_one({"_id": property_id})
    return property_data


async def update_property(property_id: str, updated_data: dict) -> dict:
    await property_collection.update_one({"_id": property_id}, {"$set": updated_data})
    return await get_property(property_id)


async def delete_property(property_id: str) -> dict:
    await property_collection.delete_one({"_id": property_id})
    return {"message": "Property deleted"}
