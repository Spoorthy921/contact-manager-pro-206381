from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import create_access_token, hash_password, verify_password, get_current_user
from ..db import get_db
from ..models import User

router = APIRouter()


@router.post(
    "/register",
    response_model=schemas.AuthResponse,
    responses={400: {"model": schemas.ErrorResponse}},
    summary="Register a new user",
    description="Creates a new user with email/password and returns a JWT access token.",
    operation_id="auth_register",
)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)) -> schemas.AuthResponse:
    """Register a user if email is not already taken."""
    existing = db.scalar(select(User).where(User.email == str(payload.email)))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=str(payload.email), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user_id=user.id)
    return schemas.AuthResponse(access_token=token)


@router.post(
    "/login",
    response_model=schemas.AuthResponse,
    responses={401: {"model": schemas.ErrorResponse}},
    summary="Login",
    description="Validates email/password and returns a JWT access token.",
    operation_id="auth_login",
)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)) -> schemas.AuthResponse:
    """Login a user and return a JWT."""
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(user_id=user.id)
    return schemas.AuthResponse(access_token=token)


@router.get(
    "/me",
    response_model=schemas.UserMeResponse,
    summary="Current user",
    description="Returns the current authenticated user.",
    operation_id="auth_me",
)
def me(current_user: User = Depends(get_current_user)) -> schemas.UserMeResponse:
    """Return current user profile."""
    return schemas.UserMeResponse(id=current_user.id, email=current_user.email)
