from fastapi import APIRouter, HTTPException
from app.models import Reviews, ReviewResponse
from app.database import review_collection


router = APIRouter(prefix="/api/v1", tags=["reviews"])


@router.post("/reviews")
async def create_review(review: Reviews):
    """
    Creates a new review for a property.
    :param review: The review to be created.
    :return: The newly created review.
    """
    review_data = review.model_dump()

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


@router.get("/reviews")
async def get_all_reviews():
    """
    Get all reviews.
    returns: A list of all reviews.
    """
    reviews = []

    async for review_data in review_collection.find({}):

        # Convert ObjectId to str for JSON serialization
        review_data['_id'] = str(review_data['_id'])
        review_data['id'] = review_data.pop('_id')  # Rename _id to id
        review = ReviewResponse(**review_data)
        reviews.append(review)

    return reviews
