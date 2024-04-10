import motor.motor_asyncio
from bson import ObjectId

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
database = client.properties

property_collection = database.get_collection("properties")


async def create_property(property_data: dict) -> dict:
    result = await property_collection.insert_one(property_data)
    return {"id": str(result.inserted_id)}


async def get_property(property_id: str) -> dict:
    property_data = await property_collection.find_one({"_id": ObjectId(property_id)})
    return property_data


async def update_property(property_id: str, updated_data: dict) -> dict:
    await property_collection.update_one({"_id": ObjectId(property_id)}, {"$set": updated_data})
    return await get_property(property_id)


async def delete_property(property_id: str) -> dict:
    await property_collection.delete_one({"_id": ObjectId(property_id)})
    return {"message": "Property deleted"}
