"""Authentication endpoints (signup, login, me)"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

from backend.database import get_db
from backend.models.user import User
from backend.auth.password import hash_password, verify_password
from backend.auth.jwt import create_access_token
from backend.auth.dependencies import get_current_user

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api", tags=["auth"])


class SignupRequest(BaseModel):
    """Signup request body"""
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must be at most 128 characters")
        return v


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
@limiter.limit("5/minute")
async def signup(http_request: Request, body: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **email**: Valid email address (unique)
    - **password**: Password (will be hashed)

    Returns access token and user data.
    """

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == body.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Create new user
    hashed_password = hash_password(body.password)
    new_user = User(
        email=body.email.lower(),
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
@limiter.limit("10/minute")
async def login(http_request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    - **email**: User's email address
    - **password**: User's password

    Returns access token and user data.
    """

    # Find user by email
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(body.password, user.password_hash):
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
