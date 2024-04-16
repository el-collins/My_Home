from fastapi import APIRouter, Depends, HTTPException, status
from app.crud import add_to_wishlist, get_user_wishlist, remove_wishlist
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/wishlist", tags=["wishlist"])






#wishlist_router.py

# Define the endpoint to retrieve all wishlist items for the user
@router.get("/")
async def get_wishlist(current_user: User = Depends(get_current_user)):
    """
    This endpoint allows users to retrieve all items from their wishlist.

    :param current_user: The current user, obtained using the get_current_user dependency
    :return: A list of all items in the user's wishlist
    """
    try:
        # Call the get_user_wishlist function to retrieve all wishlist items for the user
        wishlist_items = await get_user_wishlist(str(current_user["_id"]))
        return wishlist_items
    except Exception as e:
        # If an error occurs, raise an HTTPException with a status code of 400 and the error message
        raise HTTPException(status_code=400, detail=str(e))



# Define the endpoint to add a property to the user's wishlist
@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_to_wishlist_route(wishlist_item: WishlistItem):
    try:
        # Check if the property exists
        property = await property_collection.find_one({"_id": wishlist_item.property_id})
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")

         # Check if the property is already in the user's wishlist
        existing_wishlist_item = await wishlist_collection.find_one({
            "user_id": wishlist_item.user_id,
            "property_id": wishlist_item.property_id
        })
        if existing_wishlist_item:
            raise HTTPException(
                status_code=400, detail="Property already in wishlist")

        result = await add_to_wishlist(wishlist_item)
        return result
    except (Exception, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


# # Endpoint to retrieve a user's wishlist
# @app.get("/wishlist/{user_id}")
# async def get_wishlist(user_id: str):
#     wishlist = []
#     async for item in db.wishlist.find({"user_id": user_id}):
#         wishlist.append(item)
#     return wishlist

# # Endpoint to remove a property from the user's wishlist
# @app.delete("/wishlist/")
# async def remove_from_wishlist(wishlist_item: WishlistItem):
#     # Find and delete the wishlist item
#     result = await db.wishlist.delete_one({
#         "user_id": wishlist_item.user_id,
#         "property_id": wishlist_item.property_id
#     })
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Wishlist item not found")
#     return {"message": "Wishlist item deleted successfully"}
