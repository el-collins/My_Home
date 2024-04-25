from fastapi import APIRouter, HTTPException, Depends
from app.models import ReviewResponse
from app.database import review_collection
from app.models import User, ReviewCreate
from app.dependencies import get_current_user
from app.crud import get_user_review
from bson import ObjectId


router = APIRouter(prefix="/api/v1", tags=["reviews"])


@router.post("/reviews/{user_id}/{property_id}")
async def create_review(user_id: str, property_id: str, review: ReviewCreate):
    """
    Creates a new review for a property owned by a user.
    :param user_id: The ID of the user who owns the property.
    :param property_id: The ID of the property being reviewed.
    :param review: The review to be created.
    :return: The newly created review.
    """
    # Convert user_id and property_id to ObjectId
    user_id_obj = str(ObjectId(user_id))
    property_id_obj = str(ObjectId(property_id))

    # Prepare review data
    review_data = review.dict()
    review_data['user_id'] = user_id_obj
    review_data['property_id'] = property_id_obj

    # Insert the review into the database
    result = await review_collection.insert_one(review_data)

    # Check if the insertion was successful
    if result.inserted_id:
        # If successful, add the id to the review data
        review_data['id'] = str(result.inserted_id)
        return ReviewResponse(**review_data)  # Return the newly created review
    else:
        # If insertion failed, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Failed to create review")


@router.get("/reviews/{user_id}")
async def get_reviews(user_id: str):
    """
    Get all reviews for a particular user.
    :param user_id: The ID of the user whose reviews are to be fetched.
    :return: A list of reviews for the specified user.
    """
    user_id_obj = str(ObjectId(user_id))

    reviews = []

    async for review_data in review_collection.find({"user_id": user_id_obj}):
        # Convert ObjectId to str for JSON serialization
        review_data['_id'] = str(review_data['_id'])
        review_data['id'] = review_data.pop('_id')  # Rename _id to id
        review = ReviewResponse(**review_data)
        reviews.append(review)

    return reviews
