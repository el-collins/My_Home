from pydantic import BaseModel
from app.models import Property, PropertyFeatures, PropertyLocationDetails
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException  # type: ignore
from typing import List, Optional
from app.database import property_collection
from app.dependencies import get_current_user

from botocore.client import Config
import boto3  # type: ignore
from bson import ObjectId
from app.settings import settings

router = APIRouter(tags=["properties"])


s3 = boto3.client(
    "s3",
    region_name="eu-north-1",
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)


@router.post("/properties/")
async def create_properties(
    current_user=Depends(get_current_user),
    name: str = Form(...),
    price: float = Form(...),
    property_type: str = Form(...),
    phone_number: str = Form(...),
    property_location_details: str = Form(...),
    property_features: str = Form(...),
    images: List[UploadFile] = File(...),
):
    """
    FORMATS:
    property location details:
    {
        "street_address": "123 Main St",
        "area": "Downtown",
        "state": "NY"
    }

    property features:
    {
        "number_of_rooms": 3,
        "number_of_toilets": 2,
        "running_water": true,
        "electricity": true,
        "POP_available": true
    }


    """
    property_location_details = PropertyLocationDetails.parse_raw(
        property_location_details
    )
    property_features = PropertyFeatures.parse_raw(property_features)
    property = Property(
        name=name,
        price=price,
        property_type=property_type,
        phone_number=phone_number,
        property_location_details=property_location_details,
        property_features=property_features,
    )
    # Save images to S3 and get their keys
    image_keys = []
    for image in images:
        image_key = f"images/{image.filename}"
        s3.upload_fileobj(image.file, BUCKET_NAME, image_key)
        image_keys.append(image_key)
    # Save property details and image keys to MongoDB
    property_dict = property.dict()
    property_dict["images"] = image_keys
    property_dict["owner_id"] = str(current_user["id"])
    result = await property_collection2.insert_one(property_dict)
    property_id = str(result.inserted_id)
    await property_collection2.update_one(
        {"_id": result.inserted_id}, {"$set": {"id": property_id}}
    )
    return {"id": property_id}


@router.get("/properties/")
async def get_properties():
    properties = []
    async for property in property_collection2.find():
        property["_id"] = str(property["_id"])  # Convert ObjectId to string
        property["images"] = [get_image_url(key) for key in property["images"]]
        properties.append(property)
    return properties


def get_image_url(key: str):
    url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET_NAME, "Key": key}, ExpiresIn=3600
    )
    return url


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
#     # Check if the user's plan allows adding more houses
#     if plan == PlanName.basic and await get_user_houses_count(current_user["id"]) >= 3:
#         raise HTTPException(
#             status_code=400, detail="Upgrade to standard plan to add more than 3 houses")
#     elif plan == PlanName.standard and await get_user_houses_count(current_user["id"]) >= 7:
#         raise HTTPException(
#             status_code=400, detail="Upgrade to premium plan to add more than 7 houses")

#     property_location_details = PropertyLocationDetails.parse_raw(
#         property_location_details
#     )
#     property_features = PropertyFeatures.parse_raw(property_features)
#     property = Property(
#         name=name,
#         price=price,
#         property_type=property_type,
#         phone_number=phone_number,
#         property_location_details=property_location_details,
#         property_features=property_features,
#     )
#     # Save images to S3 and get their keys
#     image_keys = []
#     for image in images:
#         image_key = f"images/{image.filename}"
#         s3.upload_fileobj(image.file, BUCKET_NAME, image_key)
#         image_keys.append(image_key)
#     # Save property details and image keys to MongoDB
#     property_dict = property.dict()
#     property_dict["images"] = image_keys
#     property_dict["owner_id"] = str(current_user["id"])
#     result = await property_collection2.insert_one(property_dict)
#     property_id = str(result.inserted_id)
#     await property_collection2.update_one(
#         {"_id": result.inserted_id}, {"$set": {"id": property_id}}
#     )
#     return {"id": property_id}
