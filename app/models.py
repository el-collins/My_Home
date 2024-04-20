from pydantic import BaseModel, Field, EmailStr, StringConstraints, validator  # type: ignore
from typing import List, Annotated
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore


class User(BaseModel):
    name: str
    email: EmailStr = Field(..., min_length=6)
    password: Annotated[str, StringConstraints(min_length=8)]
    phone_number: PhoneNumber = Field(
        description="user phone number", title="phone number")

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


class UserResgister(User):
    wishlist: List[str] = []


class UserResponse(User):
    id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    # The email of the user associated with the token
    email: EmailStr


class UserLogin(BaseModel):
    # The email of the user to log in
    email: EmailStr
    # The password of the user to log in
    password: str


class Wishlist(BaseModel):
    user_id: str
    property_id: str


class Reviews(BaseModel):
    """
    Container for a single review record.
    """
    username: str = Field(description="Name of the reviewer")
    message: str = Field(min_length=5)


class ReviewResponse(Reviews):
    id: str


class ForgetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str


class PropertyLocationDetails(BaseModel):
    street_address: str
    area: str
    state: str


class PropertyFeatures(BaseModel):
    number_of_rooms: int
    number_of_toilets: int
    running_water: bool
    POP_available: bool


class Property(BaseModel):
    name: str
    price: float
    property_type: str
    phone_number: str
    property_location_details: PropertyLocationDetails
    property_features: PropertyFeatures
