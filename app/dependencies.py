from fastapi import Depends, HTTPException, status  # type: ignore
from app.auth_handler import decode_token, oauth2_scheme
from app.models import TokenData
from app.crud import get_user


# Dependency function to retrieve the current user from the provided access token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user from the provided access token.
    :param token: The access token to extract the user information from.
    :return: The user data if the token is valid, an HTTPException otherwise.
    """
    # Define an HTTPException to be raised if the credentials are invalid

    # Decode the access token using the decode_token function
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token"
        )
    # Extract the user's email from the token payload
    email: str = payload.get("sub")

    # Raise an HTTPException if the email is not present in the payload
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )

    # Create a TokenData instance with the extracted email
    token_data = TokenData(email=email)

    # Retrieve the user from the database using the get_user function
    user = await get_user(email=token_data.email)

    # Raise an HTTPException if the user is not found in the database
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Return the user data
    return user
