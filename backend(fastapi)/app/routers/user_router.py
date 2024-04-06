from fastapi import APIRouter, Depends
from app import crud, dependencies
from app.models import UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserPublic)
async def create_user(user: UserCreate, db=Depends(dependencies.get_db)):
    return await crud.create_user(db, user)

@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: str, db=Depends(dependencies.get_db)):
    return await crud.get_user(db, user_id)

# Additional user-related endpoints would go here...