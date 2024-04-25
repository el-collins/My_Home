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


class UserResgister(User):
    wishlist: List[str] = []
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
    # property_id: str
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


# Define an Enum for the available plans
class PlanName(str, Enum):
    basic = "basic"
    standard = "standard"
    premium = "premium"

# Define a model for the pricing plans


class PricingPlan(BaseModel):
    name: PlanName
    price: float
    user_id: Optional[str] = None
    min_houses: Optional[int] = None
    max_houses: Optional[int] = None


# Dummy pricing plans database
pricing_plans_db: Dict[PlanName, float] = {
    PlanName.basic: 0,
    PlanName.standard: 9999.99,
    PlanName.premium: 19999.99
}