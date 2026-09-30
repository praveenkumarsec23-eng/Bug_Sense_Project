from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User

from schemas.user import UserResponse, ProfileUpdate
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"]
)


# =========================================================
# GET CURRENT USER PROFILE
# =========================================================

@router.get(
    "",
    response_model=UserResponse
)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================================================
# UPDATE CURRENT USER PROFILE
# =========================================================

@router.put(
    "",
    response_model=UserResponse
)
def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # Clean incoming values
    # -----------------------------------------------------

    name = profile_data.name.strip()
    email = str(profile_data.email).strip()
    role = profile_data.role.strip()

    primary_skills = (
        profile_data.primary_skills.strip()
        if profile_data.primary_skills
        else None
    )

    specialization = (
        profile_data.specialization.strip()
        if profile_data.specialization
        else None
    )

    experience = (
        profile_data.experience.strip()
        if profile_data.experience
        else None
    )


    # -----------------------------------------------------
    # Validate required fields
    # -----------------------------------------------------

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role cannot be empty"
        )


    # -----------------------------------------------------
    # Check email uniqueness
    # -----------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            User.email == email,
            User.id != current_user.id
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use"
        )


    # -----------------------------------------------------
    # Update current user
    # -----------------------------------------------------

    current_user.name = name
    current_user.email = email
    current_user.role = role

    current_user.primary_skills = primary_skills
    current_user.specialization = specialization
    current_user.experience = experience

    # Real persistent Last Updated timestamp
    current_user.updated_at = datetime.utcnow()


    # -----------------------------------------------------
    # Save changes
    # -----------------------------------------------------

    db.commit()
    db.refresh(current_user)

    return current_user