from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from app.models import Token, UserLogin
from app.auth_handler import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token

# Initialize the APIRouter with a prefix of "/auth" and a tag of "auth"
router = APIRouter(prefix="/auth", tags=["auth"])


# Route for user login
@router.post("/login/", response_model=Token)
async def login_user_route(form_data: UserLogin):
    """
    Authenticates a user using the provided email and password, and returns a new access token.
    :param form_data: The UserLogin data containing the user's email and password.
    :return: The access token and token type if the authentication is successful, an HTTPException otherwise.
    """
    user = await authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
