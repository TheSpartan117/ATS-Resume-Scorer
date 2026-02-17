"""Authentication endpoints (signup, login, me)"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

from database import get_db
from models.user import User
from auth.password import hash_password, verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user


router = APIRouter(prefix="/api", tags=["auth"])


class SignupRequest(BaseModel):
    """Signup request body"""
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Login request body"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User data in response"""
    id: str
    email: str
    isPremium: bool
    createdAt: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response with token"""
    accessToken: str
    user: UserResponse


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **email**: Valid email address (unique)
    - **password**: Password (will be hashed)

    Returns access token and user data.
    """

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(
        email=request.email.lower(),
        password_hash=hashed_password,
        is_premium=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    access_token = create_access_token({"sub": str(new_user.id)})

    user_response = UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        isPremium=new_user.is_premium,
        createdAt=new_user.created_at
    )

    return AuthResponse(accessToken=access_token, user=user_response)


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    - **email**: User's email address
    - **password**: User's password

    Returns access token and user data.
    """

    # Find user by email
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token
    access_token = create_access_token({"sub": str(user.id)})

    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        isPremium=user.is_premium,
        createdAt=user.created_at
    )

    return AuthResponse(accessToken=access_token, user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's data.

    Requires valid JWT token in Authorization header.
    """

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        isPremium=current_user.is_premium,
        createdAt=current_user.created_at
    )
