from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from app.auth_handler import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token

# Initialize the APIRouter with a prefix of "/auth" and a tag of "auth"
router = APIRouter(prefix="/auth", tags=["login"])


# Route for user login
@router.post("/login/")
async def login_user_route(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticates a user using the provided email and password, and returns a new access token.
    :param form_data: The UserLogin data containing the user's email and password.
    :return: The access token and token type if the authentication is successful, an HTTPException otherwise.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = (create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    ))
    return {"access_token": access_token, "token_type": "bearer"}
