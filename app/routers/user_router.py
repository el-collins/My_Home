from typing import Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
import requests
from app.settings import settings
from app.models import User, UserResgister, UserResponse
from fastapi.responses import JSONResponse
from app.crud import (
    add_to_wishlist,
    get_all_users,
    get_user,
    get_user_by_id,
    register_user,
    remove_from_wishlist,
)
from passlib.context import CryptContext  # type: ignore
from app.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db_client, user_collection
from bson import ObjectId

from app.auth_handler import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token
)
from app.utils import (
    get_password_hash,
    create_token,
    verify_token,
    generate_reset_password_email,
    generate_verification_email,
    send_email,
)

router = APIRouter(prefix="/api", tags=["users"])

# Initialize Passlib's CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# POST /signup endpoint to create a new user
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    """Create a new user."""
    try:
        # Check if email already exists
        existing_user = await get_user(
            user.email
        )  # If this doesn't throw an error then the email is already registered
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Hash the user's password using bcrypt
        hashed_password = pwd_context.hash(user.password)

        # generate token
        email_verification_token = create_token(subject=user.email, type_ops="verify")  # noqa

        # Prepare user data for registration
        user_data = user.model_dump()
        user_data["password"] = hashed_password
        user_data["phone_number"] = user_data["phone_number"].split(":")[1]
        user_data["wishlist"] = []
        user_data["is_active"] = False
        # Register the new user
        # new_user =
        await register_user(user_data)

        # send email verification to user
        email_data = generate_verification_email(
            email_to=user.email, email=user.email, token=email_verification_token
        )

        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

        # return new_user
        # Return a success message
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-email/{token}")
async def verify_email(token: str, db: Annotated[OAuth2PasswordRequestForm, Depends(get_db_client)]):
    # verify token
    email = verify_token(token=token)

    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = await get_user(email=email)

    if not user:
        raise HTTPException(
            status_code=500,
            detail="The user with this email does not exist in the system.",
        )

    # Access the ObjectId value properly
    user_id = ObjectId(user["id"])
    await user_collection.update_one({"_id": user_id}, {"$set": {"is_active": True}})

    return JSONResponse(status_code=201, content={"message": "Email verified"})


# GET / endpoint to retrieve all users
@router.get("/")
async def get_all_users_route():
    """Get all users."""
    return await get_all_users()


# GET /me endpoint to retrieve the current user response_model=UserResponse
@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the current user."""
    return current_user


# GET /{user_id} endpoint to retrieve a user by ID
@router.get("/{user_id}", response_model=User)
async def get_user_by_id_route(user_id: Any):
    """Get user by ID."""
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Google OAuth2 Endpoints
@router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }


# @router.get("/auth/google")
# async def auth_google(code: str):
#     token_url = "https://accounts.google.com/o/oauth2/token"
#     data = {
#         "code": code,
#         "client_id": settings.GOOGLE_CLIENT_ID,
#         "client_secret": settings.GOOGLE_CLIENT_SECRET,
#         "redirect_uri": settings.GOOGLE_REDIRECT_URI,
#         "grant_type": "authorization_code",
#     }
#     response = requests.post(token_url, data=data)
#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail="Invalid Google authentication code")
#     access_token = response.json().get("access_token")
#     user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
#     if user_info.status_code != 200:
#         raise HTTPException(status_code=400, detail="Could not retrieve user information")
#     return user_info.json()


@router.get("/auth/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Invalid Google authentication code"
        )
    access_token = response.json().get("access_token")
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if user_info_response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Could not retrieve user information"
        )

    user_info = user_info_response.json()
    # Check if user already exists in the database
    existing_user = await get_user(user_info["email"])
    if not existing_user:
        # Create a new user in the database
        new_user = await register_user(user_info)
        return new_user
    else:
        # Return existing user
        return existing_user


@router.post("/user/wishlist/", status_code=status.HTTP_201_CREATED)
async def add_listing_to_wishlist(
    property_id: str, current_user=Depends(get_current_user)
):
    await add_to_wishlist(str(current_user["id"]), property_id)

    return {"message": "Property added to wishlist"}


@router.delete("/user/wishlist/", status_code=status.HTTP_200_OK)
async def remove_listing_from_wishlist(
    property_id: str, current_user=Depends(get_current_user)
):
    await remove_from_wishlist(str(current_user["id"]), property_id)

    return {"message": "Property removed from wishlist"}
