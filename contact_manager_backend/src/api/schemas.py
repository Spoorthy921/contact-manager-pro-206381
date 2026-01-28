from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error message.")


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., min_length=8, description="User password (min 8 chars).")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., description="User password.")


class AuthResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field("bearer", description="Token type. Always 'bearer'.")


class UserMeResponse(BaseModel):
    id: uuid.UUID = Field(..., description="User id.")
    email: EmailStr = Field(..., description="User email.")


class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, description="Contact name.")
    phone: Optional[str] = Field(None, description="Phone number.")
    email: Optional[EmailStr] = Field(None, description="Email address.")
    address: Optional[str] = Field(None, description="Postal address.")


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Contact name.")
    phone: Optional[str] = Field(None, description="Phone number.")
    email: Optional[EmailStr] = Field(None, description="Email address.")
    address: Optional[str] = Field(None, description="Postal address.")


class ContactOut(ContactBase):
    id: uuid.UUID = Field(..., description="Contact id.")

    class Config:
        from_attributes = True
