from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class RoleEnum(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    name: str
    username: Optional[str] = None
    role: RoleEnum = RoleEnum.STUDENT
    college_name: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[int] = None
    bio: Optional[str] = ""
    avatar_url: Optional[str] = None
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    college_name: Optional[str] = None
    department: Optional[str] = None
    graduation_year: Optional[int] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    student_id: str
    created_at: datetime
    streak_days: int = 1
    total_points: int = 0
    problems_solved: int = 0
    questions_solved: int = 0
    overall_accuracy: float = 0.0
    coding_problems_solved: int = 0
    battles_won: int = 0
    followers_count: int = 0
    following_count: int = 0
    is_active: bool = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
