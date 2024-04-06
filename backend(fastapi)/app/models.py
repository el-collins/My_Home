from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# User models
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: str

# Listing models
class ListingBase(BaseModel):
    title: str
    description: str
    price: float

class ListingCreate(ListingBase):
    pass

class ListingPublic(ListingBase):
    id: str
    owner_id: str

# Reservation models
class ReservationBase(BaseModel):
    listing_id: str
    start_date: datetime
    end_date: datetime

class ReservationCreate(ReservationBase):
    user_id: str

class ReservationPublic(ReservationBase):
    id: str

# Auth models
class UserAuth(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Additional models would go here...