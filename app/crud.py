from typing import List
from app.database import user_collection, property_collection, wishlist_collection
from app.models import UserResponse, WishlistItem, User
from bson import ObjectId

# get user with the email form the database
async def get_user(email: str):
    user = await user_collection.find_one({"email": email})
    return user

# register user to the database
async def register_user(user_data):
    try:
        result = await user_collection.insert_one(user_data)
        # Add the database-generated ID to user data
        user_data["_id"] = result.inserted_id
        return user_data
    except Exception as e:
        raise ValueError("Failed to register user") from e





async def get_user_by_id(user_id: str):
    """Get user by ID."""
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    return User(**user) if user else None

async def get_all_users() -> List[UserResponse]:
    """Get all users."""
    users = []
    async for user_data in user_collection.find({}):
        user_data['_id'] = str(user_data['_id'])  # Convert ObjectId to str for JSON serialization
        user_data['id'] = user_data.pop('_id')  # Rename _id to id
        user = UserResponse(**user_data)
        users.append(user)
    
    return users




async def create_property(property_data):
    print(property_collection)
    try:
        result = await user_collection.insert_one(property_data.dict())
        # Add the database-generated ID to user data
        property_data["_id"] = result.inserted_id
        print(result)
        return property_data
    except Exception as e:
        raise ValueError("Failed to register property") from e

    # return {"property_details": property_data}


async def get_property(property_id: str) -> dict:
    property_data = await property_collection.find_one({"_id": property_id})
    return property_data


async def update_property(property_id: str, updated_data: dict) -> dict:
    await property_collection.update_one({"_id": property_id}, {"$set": updated_data})
    return await get_property(property_id)


async def delete_property(property_id: str) -> dict:
    await property_collection.delete_one({"_id": property_id})
    return {"message": "Property deleted"}



async def add_to_wishlist(wishlist_item: WishlistItem):
    try:
        result = await wishlist_collection.insert_one(wishlist_item.dict())
        return {**wishlist_item.dict(), "_id": str(result.inserted_id)}
    except Exception as e:
        raise ValueError("Failed to register property") from e