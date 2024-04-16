from fastapi import APIRouter, Depends, HTTPException, status
from app.crud import add_to_wishlist, get_user_wishlist, remove_wishlist
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


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
async def add_listing_to_wishlist(property_id: str, current_user: User = Depends(get_current_user)):
    """
    This endpoint allows users to add a property to their wishlist.

    :param property_id: The ID of the property to be added to the wishlist
    :param current_user: The current user, obtained using the get_current_user dependency
    :return: A message indicating success and the updated wishlist
    """
    # Create a dictionary containing the user ID and property ID
    wishlist_data = {"user_id": str(current_user["_id"]), "property_id": property_id}
    
    # Call the add_to_wishlist function to add the property to the user's wishlist
    wishlist = await add_to_wishlist(wishlist_data)
    
    return {
        "message": "Property added to wishlist",
        "wishlist": wishlist
    }

# Define the endpoint to remove a property from the user's wishlist
@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(property_id: str, current_user: User = Depends(get_current_user)):
    """
    This endpoint allows users to remove a property from their wishlist.

    :param property_id: The ID of the property to be removed from the wishlist
    :param current_user: The current user, obtained using the get_current_user dependency
    """
    try:
        # Call the remove_wishlist function to remove the property from the user's wishlist
        deleted_count = await remove_wishlist(str(current_user["_id"]), property_id)
        
        # If the deleted_count is 0, raise an HTTPException with a status code of 404
        if deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist item not found")
        
        # If the property is successfully removed, return nothing (status code 204)
    except Exception as e:
        # If an error occurs, raise an HTTPException with a status code of 400 and the error message
        raise HTTPException(status_code=400, detail=str(e))