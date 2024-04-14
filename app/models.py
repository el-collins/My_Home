from pydantic import BaseModel, Field, EmailStr, StringConstraints, validator, ConfigDict  # type: ignore
from typing import List, Annotated
from datetime import datetime
from typing import Optional
from app.database import PyObjectId
from bson import ObjectId
from phonenumbers import PhoneNumber
from enum import Enum


class User(BaseModel):
    # name: Annotated[str, StringConstraints(pattern=r"^[A-Za-z](?:\s[A-Za-z]+)*$")]
    # id: str
    username: str
    email: EmailStr = Field(..., min_length=6)
    password: Annotated[str, StringConstraints(min_length=8)]
    # created_at: datetime = Field(default_factory=datetime.now)
    # updated_at: datetime = Field(default_factory=datetime.now)

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


class UserResponse(User):
    id: str


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


# # Listing models

class PropertyFeatures(BaseModel):
    number_of_rooms: int
    number_of_toilets: int
    running_water: Optional[bool] = True
    POP_available: Optional[bool] = True


class PropertyLocation (BaseModel):
    street_address: str
    town: str
    state: str


class PropertyBase(BaseModel):
    """
    Container for a single property record.
    """

    name: str
    price: float
    property_type: str
    user_phone: PhoneNumber
    property_location_details: PropertyLocation
    property_features: PropertyFeatures
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class PropertyCreate(PropertyBase):
    owner_id: int
    is_available: Optional[bool] = True


class PropertyResponse(PropertyBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)


class PropertyUpdate(PropertyBase):
    """
    A set of optional updates to be made to a document in the database.
    """
    name: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
    is_available: Optional[bool]


class PropertyCollection(BaseModel):
    """
    A container holding a list of `PropertyBase` instances.

    """

    properties: List[PropertyBase]


class WishlistItem(BaseModel):
    user_id: str
    property_id: str
