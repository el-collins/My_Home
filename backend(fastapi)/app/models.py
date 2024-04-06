from pydantic import BaseModel, Field, EmailStr, StringConstraints, validator
from typing import Annotated
from datetime import datetime


# User models
class User(BaseModel):
    # name: Annotated[str, StringConstraints(pattern=r"^[A-Za-z](?:\s[A-Za-z]+)*$")]
    # id: str
    username: str
    email: EmailStr = Field(..., min_length=6)
    password: Annotated[str, StringConstraints(min_length=8)]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator("password")
    # Custom validator for password complexity requirements
    def validate_password(cls, value):
        # Check if password is at least 8 characters long
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Check if password contains a number
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must include a number")
        # Check if password contains an uppercase letter
        if not any(char.isupper() for char in value):
            raise ValueError("Password must include an uppercase letter")
        # Check if password contains a lowercase letter
        if not any(char.islower() for char in value):
            raise ValueError("Password must include a lowercase letter")
        # Hash the password using passlib
        return value

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    # The email of the user associated with the token
    email: EmailStr


# Auth model
# class UserAuth(BaseModel):
#     username: str
#     password: str

class UserLogin(BaseModel):
    # The email of the user to log in
    email: EmailStr
    # The password of the user to log in
    password: str


# class UserBase(BaseModel):
#     username: str
#     email: str

# class UserCreate(UserBase):
#     password: str

# class UserPublic(UserBase):
#     id: str

# # Listing models
# class ListingBase(BaseModel):
#     title: str
#     description: str
#     price: float

# class ListingCreate(ListingBase):
#     pass

# class ListingPublic(ListingBase):
#     id: str
#     owner_id: str

# # Reservation models
# class ReservationBase(BaseModel):
#     listing_id: str
#     start_date: datetime
#     end_date: datetime

# class ReservationCreate(ReservationBase):
#     user_id: str

# class ReservationPublic(ReservationBase):
#     id: str


