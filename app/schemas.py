from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from pydantic import ConfigDict

class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72)


class ReportCreate(BaseModel):
    title: str = Field(min_length=3, max_length=140)
    category: str = Field(min_length=2, max_length=60)
    location: str = Field(min_length=2, max_length=180)
    description: str = Field(min_length=10)


class ReportUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=140)
    category: str | None = Field(default=None, min_length=2, max_length=60)
    location: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, min_length=10)
    status: str | None = Field(default=None, max_length=30)


class ReportResponse(BaseModel):
    id: int
    user_id: int
    title: str
    category: str
    location: str
    description: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ReportResponse]

class RefreshTokenRequest(BaseModel):
    refresh_token: str