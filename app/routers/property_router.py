from fastapi import APIRouter, HTTPException, Depends, status, Body
from app.database import property_collection
from app.dependencies import get_current_user
from app.models import PropertyBase, PropertyUpdate, PropertyCollection, PropertyResponse
from bson import ObjectId
from pymongo.collection import ReturnDocument
from fastapi import Response


router = APIRouter(prefix="/api/v1", tags=["properties"])


@router.post(
    "/property/",
    response_description="Add new property",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_property(property: PropertyBase = Body(...)):
    """
    Insert a new property record.

    A unique `id` will be created and provided in the response.
    """
    new_property = await property_collection.insert_one(
        property.model_dump(by_alias=True, exclude=["id"])
    )
    created_property = await property_collection.find_one(
        {"_id": new_property.inserted_id}

    )
    return created_property


@router.get(
    "/properties/",
    response_description="List all properties",
    response_model=PropertyCollection,
    response_model_by_alias=False,
)
async def list_properties():
    """
    List all of the properties data in the database.

    The response is unpaginated and limited to 1000 results.
    """
    return PropertyCollection(properties=await property_collection.find().to_list(1000))


@router.get(
    "/properties/{id}",
    response_description="Get a single property",
    response_model=PropertyBase,
    response_model_by_alias=False,
)
async def show_property(id: str):
    """
    Get the record for a specific property, looked up by `id`.
    """
    if (
        property := await property_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return property

    raise HTTPException(status_code=404, detail=f"Property {id} not found")


@router.patch(
    "/properties/{id}",
    response_description="Update a property",
    response_model=PropertyUpdate,
    response_model_by_alias=False,
)
async def update_property(id: str, property: PropertyUpdate = Body(...)):
    """
    Update individual fields of an existing property record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.
    """
    property = {
        k: v for k, v in property.model_dump(by_alias=True).items() if v is not None
    }

    if len(property) >= 1:
        update_result = await property_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": property},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(
                status_code=404, detail=f"Property {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_property := await property_collection.find_one({"_id": id})) is not None:
        return existing_property

    raise HTTPException(status_code=404, detail=f"Property {id} not found")


@router.delete("/properties/{id}", response_description="Delete a property")
async def delete_property(id: str):
    """
    Remove a single property record from the database.
    """
    delete_result = await property_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Property {id} not found")
