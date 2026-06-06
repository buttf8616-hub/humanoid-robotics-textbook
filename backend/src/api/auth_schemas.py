"""Pydantic schemas for authentication endpoints."""
from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(..., description="User email address")
    name: str = Field(..., min_length=2, description="Full name")
    code_id: str = Field(..., min_length=1, description="PIAIC student code (e.g. PIAIC12345)")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    software_background: str = Field(default="", description="Student's software/programming background")
    hardware_background: str = Field(default="", description="Student's hardware/electronics background")


class SigninRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class UserInfo(BaseModel):
    id: int
    email: str
    name: str
    code_id: str
    software_background: str = ""
    hardware_background: str = ""


class AuthResponse(BaseModel):
    token: str
    user: UserInfo
