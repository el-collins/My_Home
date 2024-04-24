from fastapi import APIRouter, HTTPException, Depends, status, Body, UploadFile, File
from app.database import property_collection
from app.dependencies import get_current_user
from app.models import (
    PropertyBase,
    PropertyUpdate,
    PropertyCollection,
    PropertyResponse,

)
from bson import ObjectId
from pymongo.collection import ReturnDocument
from fastapi import Response
from app.services import savePicture, getResponse, resultVerification
from app.save_picture import save_picture
from typing import List
from enum import Enum

router = APIRouter(prefix="/api/v1", tags=["properties"])


# Define an Enum for the available plans


class PlanName(str, Enum):
    basic = "basic"
    standard = "standard"
    premium = "premium"

# Define a model for the pricing plans


class PricingPlan(BaseModel):
    name: PlanName
    price: float
    user_id: str
    min_houses: int = Field(..., gt=0,
                            description="Minimum number of houses allowed")
    max_houses: int = Field(..., gt=0,
                            description="Maximum number of houses allowed")


# Dummy pricing plans database
pricing_plans_db: Dict[PlanName, float] = {
    PlanName.basic: 0,
    PlanName.standard: 9999.99,
    PlanName.premium: 19999.99
}


# Define an Enum for the available plans


class PlanName(str, Enum):
    basic = "basic"
    standard = "standard"
    premium = "premium"

# Define a model for the pricing plans


# Dummy pricing plans database
pricing_plans_db: Dict[PlanName, PricingPlan] = {
    PlanName.basic: PricingPlan(
        name=PlanName.basic,
        price=0.0,
        owner_id="user123",
        min_houses=1,
        max_houses=3
    ),
    PlanName.standard: PricingPlan(
        name=PlanName.standard,
        price=9999.99,
        owner_id="user123",
        min_houses=4,
        max_houses=7
    ),
    PlanName.premium: PricingPlan(
        name=PlanName.premium,
        price=19999.99,
        owner_id="user123",
        min_houses=8,
        max_houses=10
    )
}


UploadImage = f"/image-upload/"


@router.post(
    "/property/",
    response_description="Add new property",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_property(
    property: PropertyBase = Body(...)
):
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
async def update_property(id: str, property: PropertyUpdate):
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
    if (
        existing_property := await property_collection.find_one({"_id": id})
    ) is not None:
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


# @router.post(UploadImage + "{id}", status_code=status.HTTP_204_NO_CONTENT)
# async def uploadPropertyImage(id: str, file: UploadFile = File(...)):
#     """
#     Add house images by `id`cof property ownerd.
#     """
#     result = await resultVerification(id)
#     imageUrl = save_picture(
#         file=file, folderName="properties", fileName=result["name"])
#     done = await savePicture(id, imageUrl)
#     return getResponse(
#         done, errorMessage="An error occurred while saving property image."
#     )


@router.post(UploadImage + "{id}", status_code=status.HTTP_204_NO_CONTENT)
async def uploadPropertyImage(id: str, files: List[UploadFile] = File(...)):
    """
    Add house images by `id` of property owners.
    """
    # Assuming `resultVerification` and `savePicture` functions are defined elsewhere
    result = await resultVerification(id)

    # List to store image URLs
    image_urls = []
    for file in files:
        # Save each picture and get its URL
        imageUrl = save_picture(
            file=file, folderName="properties", fileName=result["name"])
        image_urls.append(imageUrl)

    # Convert PropertyImage instances into dictionaries
    property_images = [{"imageUrl": url} for url in image_urls]

    # Assuming `savePicture` expects a list of dictionaries
    done = await savePicture(id, property_images)

    return getResponse(
        done, errorMessage="An error occurred while saving property image."
    )

# async def uploadPropertyImage(id: str, files: List[UploadFile] = File(...)):
#     """
#     Add house images by `id` of property owners.
#     """
#     # Assuming `resultVerification` and `savePicture` functions are defined elsewhere
#     result = await resultVerification(id)

#     # List to store image URLs
#     image_urls = []
#     for file in files:
#         # Save each picture and get its URL
#         imageUrl = save_picture(
#             file=file, folderName="properties", fileName=result["name"])
#         image_urls.append(imageUrl)

#     # Create PropertyImage instances for each image
#     property_images = [PropertyImage(imageUrl=url) for url in image_urls]

#     # Assuming `savePicture` returns a boolean indicating success
#     done = await savePicture(id, property_images)

#     return getResponse(
#         done, errorMessage="An error occurred while saving property image."
#     )


# @router.post(UploadImage + "{id}", status_code=status.HTTP_204_NO_CONTENT)
# async def uploadPropertyImage(id: str, images: MultiplePropertyImages):
#     """
#     Add house images by `id` of property owners.
#     """
#     # Assuming `resultVerification` and `savePicture` functions are defined elsewhere
#     result = await resultVerification(id)

#     # Extract image URLs from the model
#     image_urls = [image.imageUrl for image in images.images]

#     # Assuming `savePicture` returns a boolean indicating success
#     done = await savePicture(id, image_urls)

#     return getResponse(
#         done, errorMessage="An error occurred while saving property image."
#     )


# @router.post("/properties/")
# async def create_properties(
#     current_user=Depends(get_current_user),
#     name: str = Form(...),
#     price: float = Form(...),
#     property_type: str = Form(...),
#     phone_number: str = Form(...),
#     property_location_details: str = Form(...),
#     property_features: str = Form(...),
#     images: List[UploadFile] = File(...),
#     plan: PlanName = Depends(get_user_plan)
# ):
#     """
#     FORMATS:
#     property location details:
#     {
#         "street_address": "123 Main St",
#         "area": "Downtown",
#         "state": "NY"
#     }

#     property features:
#     {
#         "number_of_rooms": 3,
#         "number_of_toilets": 2,
#         "running_water": true,
#         "electricity": true,
#         "POP_available": true
#     }


#     """
    # Check if the user's plan allows adding more houses
    # if plan == PlanName.basic and await get_user_houses_count(current_user["id"]) >= 3:
    #     raise HTTPException(
    #         status_code=400, detail="Upgrade to standard plan to add more than 3 houses")
    # elif plan == PlanName.standard and await get_user_houses_count(current_user["id"]) >= 7:
    #     raise HTTPException(
    #         status_code=400, detail="Upgrade to premium plan to add more than 7 houses")

    # property_location_details = PropertyLocationDetails.parse_raw(
    #     property_location_details
    # )
    # property_features = PropertyFeatures.parse_raw(property_features)
    # property = Property(
    #     name=name,
    #     price=price,
    #     property_type=property_type,
    #     phone_number=phone_number,
    #     property_location_details=property_location_details,
    #     property_features=property_features,
    # )
    # # Save images to S3 and get their keys
    # image_keys = []
    # for image in images:
    #     image_key = f"images/{image.filename}"
    #     s3.upload_fileobj(image.file, BUCKET_NAME, image_key)
    #     image_keys.append(image_key)
    # # Save property details and image keys to MongoDB
    # property_dict = property.dict()
    # property_dict["images"] = image_keys
    # property_dict["owner_id"] = str(current_user["id"])
    # result = await property_collection2.insert_one(property_dict)
    # property_id = str(result.inserted_id)
    # await property_collection2.update_one(
    #     {"_id": result.inserted_id}, {"$set": {"id": property_id}}
    # )
    # return {"id": property_id}
