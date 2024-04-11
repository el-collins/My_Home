from app.database import user_collection, property_collection


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
