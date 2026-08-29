from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "inspector"  # 'admin', 'inspector', 'supervisor'
    badge_number: Optional[str] = None
    phone_number: Optional[str] = None
    jurisdiction_district: Optional[str] = None
    jurisdiction_state: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    badge_number: Optional[str] = None
    phone_number: Optional[str] = None
    jurisdiction_district: Optional[str] = None
    jurisdiction_state: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
