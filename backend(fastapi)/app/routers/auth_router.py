from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models import TokenData, Token, UserLogin
from app.database import get_user
from app.settings import settings
from passlib.context import CryptContext
from jose import JWTError, jwt

# Initialize the APIRouter with a prefix of "/auth" and a tag of "auth"
router = APIRouter(prefix="/auth", tags=["auth"])

# Initialize Passlib's CryptContext with the "bcrypt" scheme and auto-deprecation
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Define the secret key, algorithm, and access token expiration time in minutes
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# Initialize an OAuth2PasswordBearer object with the location of the token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to verify a plaintext password against a hashed password
def verify_password(plain_password, hashed_password):
    """
    Verifies if a plaintext password matches a hashed password using the initialized CryptContext.
    :param plain_password: The plaintext password to verify.
    :param hashed_password: The hashed password to compare against.
    :return: True if the plaintext password matches the hashed password, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# Function to authenticate a user using an email and password
async def authenticate_user(email: str, password: str):
    """
    Authenticates a user by retrieving the user from the database using the provided email and verifying the password.
    :param email: The user's email address.
    :param password: The user's plaintext password.
    :return: The user data if the authentication is successful, None otherwise.
    """
    user = await get_user(email)
    if not user or not verify_password(password, user["password"]):
        return None
    return user


# Function to create a new access token with the provided data and expiration time
def create_access_token(data: dict, expires_delta: Annotated[timedelta, None] = None):
    """
    Creates a new access token with the provided data and expiration time.
    :param data: The data to include in the token.
    :param expires_delta: The expiration time for the token. If not provided, a default expiration time of 15 minutes is used.
    :return: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify JWT token and extract user information
def decode_token(token: str):
    """
    Decodes a JWT token and extracts the user information.
    :param token: The JWT token to decode.
    :return: The decoded token payload if the token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # return payload.get("sub")
        return payload
    except JWTError:
        return None


# Dependency function to retrieve the current user from the provided access token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user from the provided access token.
    :param token: The access token to extract the user information from.
    :return: The user data if the token is valid, an HTTPException otherwise.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception

        token_data = TokenData(email=email)
    except JWTError:
        raise credential_exception

    user = await get_user(email=token_data.email)
    if user is None:
        raise credential_exception

    return user



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
