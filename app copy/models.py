from pydantic import BaseModel, Field, EmailStr, StringConstraints, validator  # type: ignore
from typing import List, Annotated
from pydantic_extra_types.phone_numbers import PhoneNumber  # type: ignore
from enum import Enum
from typing import Dict, Optional


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


class PlanBase(BaseModel):
    name: str
    price: float
    min_house: int
    max_house: int


pricing_plans_db = [
    {
        "name": "Basic",
        "price": 0.00,
        "description": "Basic plan description",
        "min_house": 1,
        "max_house": 2,
    },
    {
        "name": "Standard",
        "price": 10000.00,
        "description": "Standard plan description",
        "min_house": 3,
        "max_house": 7,
    },
    {
        "name": "Premium",
        "price": 30000.00,
        "description": "Premium plan description",
        "min_house": 7,
        "max_house": 12,
    },
]


class PlanResponse(PlanBase):
    id: str


class UserRegister(User):
    wishlist: List[str] = []
    plan: Optional[dict] = Field(default=pricing_plans_db[0]["name"])
    is_active: bool = Field(
        default=False, description="Is the user active", title="Is Active")


class UserResponse(User):
    id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    # The email of the user associated with the token
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr  # The email of the user to log in
    password: str  # The password of the user to log in


class Wishlist(BaseModel):
    user_id: str
    property_id: str


class Review(BaseModel):
    user_id: str
    property_id: str
    rating: float
    comment: str

    class Config:
        orm_mode = True


class ReviewCreate(BaseModel):
    rating: float
    comment: str


class ReviewResponse(Review):
    id: str


class UserReviews(BaseModel):
    user_id: str
    property_id: str
    reviews: List[ReviewResponse]


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


# Forget password
class Message(BaseModel):
    message: str


class NewPassword(BaseModel):
    token: str
    new_password: str
