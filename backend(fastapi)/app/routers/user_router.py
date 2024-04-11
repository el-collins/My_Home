from fastapi import APIRouter, HTTPException
# from app import crud, dependencies
from app.models import User
from app.crud import get_user, register_user
from passlib.context import CryptContext # type: ignore



router = APIRouter(prefix="/users", tags=["users"])

# Initialize Passlib's CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=User)
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
        user_data = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
                        "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        new_user = await register_user(user_data)

        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.get("/{user_id}", response_model=UserPublic)
# async def get_user(user_id: str, db=Depends(dependencies.get_db)):
#     return await crud.get_user(db, user_id)

