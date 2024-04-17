from fastapi import APIRouter
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
    return review


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
        reviews = ReviewResponse(**review_data)
        reviews.append(reviews)

    return reviews
