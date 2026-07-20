from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    profile_image: Optional[str] = None
