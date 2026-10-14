
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.database import get_db
from database.models import User, UserSettings

from schemas.user import UserCreate, UserResponse
from schemas.auth import LoginRequest, LoginResponse
from utils.dependencies import get_current_user
from utils.security import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# =========================================================
# REGISTER USER
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password before storing
    password_hash = hash_password(
        user_data.password
    )

    try:
        # Create new user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash
        )

        db.add(new_user)

        # Obtain the user ID without committing
        db.flush()

        # Automatically create default user settings
        default_settings = UserSettings(
            user_id=new_user.id
        )

        db.add(default_settings)

        # Commit both records in one transaction
        db.commit()

        # Refresh user data from database
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        # Undo the failed transaction
        db.rollback()

        # Check whether another request registered
        # the same email concurrently
        existing_user = (
            db.query(User)
            .filter(User.email == user_data.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Other database integrity problems
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create account"
        )


# =========================================================
# LOGIN USER
# =========================================================

@router.post(
    "/login",
    response_model=LoginResponse
)
def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    # User doesn't exist
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email
        }
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
        email=user.email
    )


# =========================================================
# CURRENT LOGGED-IN USER
# Protected route
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
