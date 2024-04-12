from fastapi import APIRouter, Depends, HTTPException, status
from app.crud import add_to_wishlist, remove_wishlist
from app.dependencies import get_current_user
from app.models import User


router = APIRouter(prefix="/wishlist", tags=["wishlist"])


# Endpoint to add a property to the user's wishlist
@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_listing_to_wishlist(property_id: str, current_user: User = Depends(get_current_user)):
        wishlist_data = {"user_id": str(current_user["_id"]), "property_id": property_id}        
        wishlist = await add_to_wishlist(wishlist_data)

        
        return {
            "message": "Property added to wishlist",
            "wishlist": wishlist
        }


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(property_id: str, current_user: User = Depends(get_current_user)):
    """
    Remove a property from the user's wishlist.
    """
    try:
        # Call the function to remove the property from the wishlist
        deleted_count = await remove_wishlist(str(current_user["_id"]), property_id)
        if deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist item not found")
        return
    except Exception as e:
        # If an error occurs, raise an HTTPException with a status code of 400 and the error message
        raise HTTPException(status_code=400, detail=str(e))
    


