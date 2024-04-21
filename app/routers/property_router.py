from pydantic import BaseModel
from app.models import Property, PropertyFeatures, PropertyLocationDetails
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException  # type: ignore
from typing import List
from app.database import property_collection
from app.dependencies import get_current_user
from botocore.client import Config
import boto3  # type: ignore
from botocore.exceptions import NoCredentialsError

router = APIRouter()


class UpdatePropertyModel(BaseModel):
    name: str = None
    price: float = None
    property_type: str = None
    phone_number: str = None
    property_location_details: str = None
    property_features: str = None
    images: List[UploadFile] = []


ACCESS_KEY = "AKIA47CRU4UEBPPE6H76"
SECRET_KEY = "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"
BUCKET_NAME = "myhome1"


s3 = boto3.client(
    "s3",
    region_name="eu-north-1",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
)


# CREATE A PROPERTY
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
        property["images"] = [get_image_url(key) for key in property["images"]]
        properties.append(property)
    return properties


def get_image_url(key: str):
    url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET_NAME, "Key": key}, ExpiresIn=3600
    )
    return url


# GET A USER'S PROPERTIES
@router.get("/users/me/properties")
async def get_user_properties(current_user=Depends(get_current_user)):
    user_id = str(current_user["id"])

    properties = []
    async for property in property_collection.find({"owner_id": user_id}):
        property["_id"] = str(property["_id"])  # Convert ObjectId to string
        property["images"] = [get_image_url(key) for key in property["images"]]
        properties.append(property)
    if not properties:
        raise HTTPException(status_code=404, detail="No properties found for this user")
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
        s3.delete_object(Bucket=BUCKET_NAME, Key=image_key)

    # Delete property from MongoDB
    await property_collection.delete_one({"id": property_id, "owner_id": user_id})

    return {"message": "Property and associated images deleted successfully"}


def upload_image_to_s3(image: UploadFile):
    s3 = boto3.client("s3")

    try:
        s3.upload_fileobj(image.file, "your-bucket-name", image.filename)
    except NoCredentialsError:
        return {"error": "No AWS credentials found"}
    except Exception as e:
        return {"error": str(e)}

    return image.filename


# UPDATE A USER'S PROPERTY
@router.put("/users/me/properties/{property_id}")
async def update_property(
    property_id: str,
    property: UpdatePropertyModel,
    current_user=Depends(get_current_user),
):
    user_id = str(current_user["id"])
    property_dict = property.dict(exclude_unset=True)

    # If images are included in the update, upload them to S3 and add their keys to the property_dict
    if "images" in property_dict:
        image_keys = [
            upload_image_to_s3(image.file) for image in property_dict["images"]
        ]
        property_dict["images"] = image_keys

    result = await property_collection.update_one(
        {"_id": property_id, "owner_id": user_id}, {"$set": property_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Property updated successfully"}
