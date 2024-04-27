from app.models import Property, PropertyFeatures, PropertyLocationDetails
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException  # type: ignore
from typing import List, Optional
from app.database import property_collection, review_collection
from app.dependencies import get_current_user, get_user_houses_count, get_db_client, get_user_plan
from botocore.client import Config
import boto3  # type: ignore
from bson import ObjectId
from app.settings import settings
from app.crud import get_reviews_for_property

router = APIRouter()


ACCESS_KEY = "AKIA47CRU4UEBPPE6H76"
SECRET_KEY = "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"
BUCKET_NAME = "myhome1"


s3 = boto3.client(
    "s3",
    region_name="eu-north-1",
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)


# CREATE PROPERTY
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

    # if 'plan' not in current_user:
    # todo and a plan key with a value of 'Basic'

    all_properties_cursor = property_collection.find()
    all_properties = await all_properties_cursor.to_list(length=None)

    user_properties = [
        x for x in all_properties if x['owner_id'] == str(current_user["id"])]

    # Define plan limits
    plan_limits = {
        'Basic': 2,
        'Standard': 7,
        'Premium': 12
    }

    # Check if user has reached the limit for their plan
    for plan, limit in plan_limits.items():
        if len(user_properties) >= limit and ('plan' not in current_user or current_user['plan'] == plan):
            raise HTTPException(
                status_code=400,
                detail=f"You have reached the limit of {
                    limit} properties per user. Upgrade to a higher plan."
            )

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
    result = await property_collection.insert_one(property_dict)
    property_id = str(result.inserted_id)
    await property_collection.update_one(
        {"_id": result.inserted_id}, {"$set": {"id": property_id}}
    )
    return {"id": property_id}


# GET ALL PROPERTIES

@router.get("/properties/")
async def get_properties():
    properties = []
    async for property in property_collection.find():
        property["_id"] = str(property["_id"])  # Convert ObjectId to string

        # Check if the 'images' field exists in the property document
        if "images" in property:
            property["images"] = [get_image_url(
                key) for key in property["images"]]
        else:
            # Set empty list if 'images' field is missing
            property["images"] = []

        # Fetch the associated review for the property
        review = await review_collection.find_one({"property_id": property["_id"]})
        if review:
            property["review_id"] = str(review["_id"])
        else:
            property["review_id"] = None

        properties.append(property)
    return properties


def get_image_url(key: str):
    url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": settings.BUCKET_NAME, "Key": key}, ExpiresIn=3600
    )
    return url


# GET A USER'S PROPERTIES
@router.get("/users/me/properties")
async def get_properties(review_id: Optional[str] = None):
    properties = []
    async for property in property_collection.find():
        property["_id"] = str(property["_id"])  # Convert ObjectId to string
        property["images"] = [get_image_url(key) for key in property["images"]]

        if review_id:
            reviews = await get_reviews_for_property(property["_id"])
            property["review_id"] = next(
                (review.id for review in reviews if review.property_id == property["_id"]), None)
        else:
            property["review_id"] = None

        properties.append(property)
    return properties


# DELETE A USER'S PROPERTY
@router.delete("/users/me/properties/{property_id}")
async def delete_property(property_id: str, current_user=Depends(get_current_user)):
    user_id = str(current_user["id"])
    property = await property_collection.find_one(
        {"id": property_id, "owner_id": user_id}
    )
    if property is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # Delete images from S3 bucket
    for image_key in property["images"]:
        s3.delete_object(Bucket=settings.BUCKET_NAME, Key=image_key)
    # Delete property from MongoDB

    await property_collection.delete_one({"id": property_id, "owner_id": user_id})

    return {"message": "Property and associated images deleted successfully"}


# UPDATE A USER'S PROPERTY
@router.put("/properties/{property_id}")
async def update_property(
    property_id: str,
    current_user=Depends(get_current_user),
    name: str = Form(None),
    price: float = Form(None),
    property_type: str = Form(None),
    phone_number: str = Form(None),
    property_location_details: str = Form(None),
    property_features: str = Form(None),
    images: Optional[List[UploadFile]] = File(None),
):
    """
    FORMATS:
    name: str,
    price: float,
    property_type: str,
    phone_number: str,

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
    property_dict = {}
    print(images)
    if name is not None:
        property_dict["name"] = name
    if price is not None:
        property_dict["price"] = price
    if property_type is not None:
        property_dict["property_type"] = property_type
    if phone_number is not None:
        property_dict["phone_number"] = phone_number
    if property_location_details is not None:
        property_dict["property_location_details"] = PropertyLocationDetails.parse_raw(
            property_location_details)
    if property_features is not None:
        property_dict["property_features"] = PropertyFeatures.parse_raw(
            property_features)

    # if images is not None:
    if images and len(images) > 0:  # Change this line
        image_keys = []
        for image in images:
            image_key = f"properties images/{str(current_user['id'])}/{
                property_id}/{image.filename}"
            s3.upload_fileobj(image.file, settings.BUCKET_NAME, image_key)
            image_keys.append(image_key)
        property_dict["images"] = image_keys

    result = await property_collection.update_one(
        {"_id": ObjectId(property_id), "owner_id": str(current_user["id"])},
        {"$set": property_dict},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Property not found")

    return {"message": "Property updated successfully"}
