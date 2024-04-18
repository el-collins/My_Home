from fastapi import APIRouter, HTTPException, Depends, status, Body, UploadFile, File, Form
from app.database import property_collection
from app.dependencies import get_current_user
from app.models import (
    PropertyBase,
    PropertyUpdate,
    PropertyCollection,
    PropertyResponse,
    PropertyCreate,
    PropertyImage

)
from bson import ObjectId
from pymongo.collection import ReturnDocument
from fastapi import Response
from app.services import savePicture, getResponse, resultVerification
from app.save_picture import save_picture
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["properties"])


UploadImage = f"/image-upload/"


@router.post(
    "/property/",
    response_description="Add new property",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_property(
    name: str = Form(...),
    price: float = Form(...),
    property_type: str = Form(...),
    phone_number: str = Form(...),
    street_address: str = Form(...),
    area: str = Form(...),
    state: str = Form(...),
    number_of_rooms: int = Form(...),
    number_of_toilets: int = Form(...)
):
    """
    Insert a new property record.

    A unique `id` will be created and provided in the response.
    """
    property_data = {
        "name": name,
        "price": price,
        "property_type": property_type,
        "phone_number": phone_number,
        "property_location_details": {
            "street_address": street_address,
            "area": area,
            "state": state
        },
        "property_features": {
            "number_of_rooms": number_of_rooms,
            "number_of_toilets": number_of_toilets
        },
    }
    new_property = await property_collection.insert_one(property_data)
    created_property = await property_collection.find_one({"_id": new_property.inserted_id})
    return created_property
# async def create_property(
#     property: PropertyBase = Body(...)
# ):
#     """
#     Insert a new property record.

#     A unique `id` will be created and provided in the response.
#     """
#     new_property = await property_collection.insert_one(
#         property.model_dump(by_alias=True, exclude=["id"])
#     )
#     created_property = await property_collection.find_one(
#         {"_id": new_property.inserted_id}
#     )
#     return created_property


# @router.get(
#     "/properties/",
#     response_description="List all properties",
#     response_model=PropertyCollection,
#     response_model_by_alias=False,
# )
# async def list_properties():
#     """
#     List all of the properties data in the database.

#     The response is unpaginated and limited to 1000 results.
#     """
#     return PropertyCollection(properties=await property_collection.find().to_list(1000))


# @router.get("/properties_with_images/", response_model=List[PropertyImage])
# async def get_properties_with_images():
#     """
#     Retrieve all properties along with their images.
#     """
#     properties_with_images = []
#     # Assuming property_collection is a MongoDB collection object
#     cursor = property_collection.find({})

#     for property_data in await cursor.to_list(length=100):
#         property_with_image = PropertyImage(**property_data)
#         properties_with_images.append(property_with_image)

#     return properties_with_images

@router.post("/properties_with_images/", response_model=PropertyImage, status_code=status.HTTP_201_CREATED)
async def create_property_with_images(
    name: str = Form(...),
    price: float = Form(...),
    property_type: str = Form(...),
    phone_number: str = Form(...),
    street_address: str = Form(...),
    area: str = Form(...),
    state: str = Form(...),
    number_of_rooms: int = Form(...),
    number_of_toilets: int = Form(...),
    images: List[UploadFile] = File(...)
):
    """
    Create a new property with different images.
    """
    # Save property data to database
    property_data = {
        "name": name,
        "price": price,
        "property_type": property_type,
        "phone_number": phone_number,
        "property_location_details": {
            "street_address": street_address,
            "area": area,
            "state": state
        },
        "property_features": {
            "number_of_rooms": number_of_rooms,
            "number_of_toilets": number_of_toilets
        }
    }
    new_property = await property_collection.insert_one(property_data)
    created_property_id = new_property.inserted_id

    # Save images to file system or cloud storage and get their URLs
    image_urls = []
    for image in images:
        # Save the image to file system or cloud storage
        # Example: image.save("path/to/save/image.jpg")
        # Get the URL of the saved image
        # Example: image_url = "https://example.com/path/to/save/image.jpg"
        # For demonstration, using filename as URL
        image_urls.append(image.filename)

    # Update property with image URLs
    await property_collection.update_one({"_id": created_property_id}, {"$set": {"imageUrls": image_urls}})

    # Retrieve the created property with image URLs
    created_property = await property_collection.find_one({"_id": created_property_id})
    if created_property is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    # Create and return PropertyImage response
    return PropertyImage(**created_property)


@router.get("/properties_with_images/", response_model=List[PropertyImage])
async def get_properties_with_images():
    """
    Retrieve all properties along with their images.
    """
    properties_with_images = []
    cursor = property_collection.find({})

    for property_data in await cursor.to_list(length=100):
        # Extract the imageUrls field from the property data, default to an empty list if not present
        image_urls = property_data.get('imageUrls', [])

        # Create a PropertyImage instance for each property data
        property_with_image = PropertyImage(
            name=property_data.get('name'),
            price=property_data.get('price'),
            property_type=property_data.get('property_type'),
            phone_number=property_data.get('phone_number'),
            property_location_details=property_data.get(
                'property_location_details'),
            property_features=property_data.get('property_features'),
            imageUrls=image_urls
        )

        properties_with_images.append(property_with_image)

    return properties_with_images


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


# @router.patch(
#     "/properties/{id}",
#     response_description="Update a property",
#     response_model=PropertyUpdate,
#     response_model_by_alias=False,
# )
# async def update_property(id: str, property: PropertyUpdate):
#     """
#     Update individual fields of an existing property record.

#     Only the provided fields will be updated.
#     Any missing or `null` fields will be ignored.
#     """
#     property = {
#         k: v for k, v in property.model_dump(by_alias=True).items() if v is not None
#     }

#     if len(property) >= 1:
#         update_result = await property_collection.find_one_and_update(
#             {"_id": ObjectId(id)},
#             {"$set": property},
#             return_document=ReturnDocument.AFTER,
#         )
#         if update_result is not None:
#             return update_result
#         else:
#             raise HTTPException(
#                 status_code=404, detail=f"Property {id} not found")

#     # The update is empty, but we should still return the matching document:
#     if (
#         existing_property := await property_collection.find_one({"_id": id})
#     ) is not None:
#         return existing_property

#     raise HTTPException(status_code=404, detail=f"Property {id} not found")


@router.patch("/property/{property_id}/", response_model=PropertyUpdate)
async def update_property(
    property_id: str,
    property_update: PropertyUpdate
):
    """
    Update a property by ID.
    """
    # Check if property exists
    existing_property = await property_collection.find_one({"_id": property_id})
    if existing_property is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    # Update property fields
    # Exclude fields with None values
    update_data = property_update.dict(exclude_unset=True)
    await property_collection.update_one({"_id": property_id}, {"$set": update_data})

    # Return updated property
    updated_property = await property_collection.find_one({"_id": property_id})
    return updated_property


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
