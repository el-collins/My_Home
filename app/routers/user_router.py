from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User
from app.crud import get_all_users, get_user, get_user_by_id, register_user
from passlib.context import CryptContext # type: ignore
from app.dependencies import get_current_user



router = APIRouter(prefix="/users", tags=["users"])

# Initialize Passlib's CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    """Create a new user."""
    try:
           # Check if email already exists
        existing_user = await get_user(
            user.email
        )  # If this doesn't throw an error then the email is already registered
        if existing_user:
             raise HTTPException(status_code=400, detail="Email already exists")
        
        hashed_password = pwd_context.hash(user.password)
        user_data = user.model_dump()
        user_data["password"] = hashed_password
        user_data["phone_number"] = user_data["phone_number"].split(':')[1]
        new_user = await register_user(user_data)

        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_all_users_route():
    """Get all users."""
    return await get_all_users()


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=User)
async def get_user_by_id_route(user_id: Any):
    """Get user by ID."""
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
