from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# =========================================================
# USER CREATE
# Used when creating/registering a user
# =========================================================

class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )


# =========================================================
# USER RESPONSE
# Used when sending user data back to frontend
# =========================================================

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    primary_skills: Optional[str] = None
    specialization: Optional[str] = None
    experience: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =========================================================
# PROFILE UPDATE
# Used when updating logged-in user's profile
# =========================================================

class ProfileUpdate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    email: EmailStr

    role: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    primary_skills: Optional[str] = Field(
        default=None,
        max_length=1000
    )

    specialization: Optional[str] = Field(
        default=None,
        max_length=150
    )

    experience: Optional[str] = Field(
        default=None,
        max_length=150
    )