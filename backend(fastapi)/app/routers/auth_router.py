from fastapi import APIRouter, Depends, HTTPException, status
from app.auth_handler import AuthHandler
from app.models import UserAuth, Token

router = APIRouter(prefix="/auth", tags=["auth"])

auth_handler = AuthHandler()

@router.post("/login", response_model=Token)
async def login(user_auth: UserAuth, db=Depends(dependencies.get_db)):
    user = await auth_handler.authenticate_user(db, user_auth.username, user_auth.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = auth_handler.encode_token(user.username)
    return {"access_token": token, "token_type": "bearer"}

# Additional authentication-related endpoints would go here...