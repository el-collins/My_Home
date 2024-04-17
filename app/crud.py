from typing import List
from app.database import user_collection, property_collection, wishlist_collection
from app.models import UserResponse, User, Wishlist
from bson import ObjectId  # type: ignore


# Asynchronously retrieves a user from the database using their email address
async def get_user(email: str):
    user = await user_collection.find_one({"email": email})
    return user


# Asynchronously registers a new user in the database
async def register_user(user_data):

    result = await user_collection.insert_one(user_data)
    # Adds the database-generated ID to user data
    user_data["_id"] = result.inserted_id
    return user_data


# Asynchronously retrieves a user from the database using their ID
async def get_user_by_id(user_id: str):
    """Get user by ID."""
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    return User(**user) if user else None


# Asynchronously retrieves all users from the database
async def get_all_users() -> List[UserResponse]:
    """Get all users."""
    users = []
    async for user_data in user_collection.find({}):

        # Convert ObjectId to str for JSON serialization
        user_data["_id"] = str(user_data["_id"])
        user_data["id"] = user_data.pop("_id")  # Rename _id to id
        user = UserResponse(**user_data)
        users.append(user)

    return users


# Asynchronously retrieves all wishlist items for a user
async def get_user_wishlist(user_id: str):
    """
    Get all wishlist items for the user.
    """

    # Finds all wishlist items associated with the user_id
    wishlist_items = []
    async for wishlist_item in wishlist_collection.find({"user_id": user_id}):
        wishlist_item["_id"] = str(wishlist_item["_id"])
        # wishlist_item["id"] = wishlist_item.pop("_id")

        wishlist_items.append(wishlist_item)
    print(wishlist_items)
    return wishlist_items


# Asynchronously adds an item to a user's wishlist
async def add_to_wishlist(wishlist_data):
    # Inserts the wishlist item into the database
    await wishlist_collection.insert_one(dict(wishlist_data))
    # Creates a JSON-serializable response object
    response = {**dict(wishlist_data)}
    return response


# Asynchronously removes an item from a user's wishlist
async def remove_wishlist(user_id: str, property_id: str):
    """
    Remove a property from the user's wishlist.
    """

    # Finds and deletes the wishlist item based on user_id and property_id
    response = await wishlist_collection.delete_one(
        {"user_id": user_id, "property_id": property_id}
    )
    return response.deleted_count


# Asynchronously creates a new property in the database
async def create_property(property_data):

    result = await user_collection.insert_one(property_data.dict())
    # Adds the database-generated ID to property data
    property_data["_id"] = result.inserted_id
    print(result)
    return property_data


# Asynchronously retrieves a property from the database using its ID
async def get_property(property_id: str) -> dict:
    property_data = await property_collection.find_one({"_id": property_id})
    return property_data


# Asynchronously updates a property in the database using its ID and updated data
async def update_property(property_id: str, updated_data: dict) -> dict:
    await property_collection.update_one({"_id": property_id}, {"$set": updated_data})
    return await get_property(property_id)


# Asynchronously deletes a property from the database using its ID
async def delete_property(property_id: str) -> dict:
    await property_collection.delete_one({"_id": property_id})
    return {"message": "Property deleted"}


# async def add_to_wishlist(wishlist_item: Wishlist):
#     await wishlist_collection.insert_one(dict(wishlist_item))
#     response =  {**dict(wishlist_item)}
#     return response
