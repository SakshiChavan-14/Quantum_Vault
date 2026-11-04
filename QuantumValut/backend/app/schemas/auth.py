import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    avatar_url: str | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
