from app.utils import verify_password
from typing import List
from app.database import user_collection, wishlist_collection
from app.models import UserResponse, User
from bson import ObjectId  # type: ignore


# Asynchronously retrieves a user from the database using their email address


async def get_user(email: str):
    user = await user_collection.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        user["id"] = user.pop("_id")  # Rename _id to id
    return user


def authenticate(* email: str, password: str) -> User | None:
    db_user = get_user(email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user


# Asynchronously registers a new user in the database
async def register_user(user_data):
    result = await user_collection.insert_one(user_data)
    # Adds the database-generated ID to user data
    user_data["_id"] = str(result.inserted_id)
    # user_data["id"] = user_data.pop("_id")  # Rename _id to id
    # return user_data


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
    return wishlist_items




async def add_to_wishlist(user_id: str, property_id: str):
    # Convert user_id
    user_id = ObjectId(user_id)

    # Add property_id to the user's wishlist
    await user_collection.update_one(
        {"_id": user_id}, {"$push": {"wishlist": property_id}}
    )

    # Return the updated user
    # user = await user_collection.find_one({"_id": user_id})
    # user["_id"] = str(user["_id"])
    # return user


# Asynchronously removes an item from a user's wishlist
async def remove_from_wishlist(user_id: str, property_id: str):
    # Convert user_id
    user_id = ObjectId(user_id)

    # Remove property_id from the user's wishlist
    await user_collection.update_one(
        {"_id": user_id}, {"$pull": {"wishlist": property_id}}
    )

