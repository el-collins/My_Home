from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
from typing import Annotated
import bson
import os
from dotenv import load_dotenv  # type: ignore
from pydantic import (BeforeValidator)


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


wishlist_database = get_db_client().Wishlist
wishlist_collection = property_database.wishlists


PyObjectId = Annotated[str, BeforeValidator(str)]
ObjectId = Annotated[
    bson.ObjectId,
    BeforeValidator(lambda x: bson.ObjectId(x) if isinstance(x, str) else x),
    # PlainSerializer(lambda x: f"{x}", return_type=str),
    # WithJsonSchema({"type": "string"}, mode="validation"),
    # WithJsonSchema({"type": "string"}, mode="serialization"),
]
