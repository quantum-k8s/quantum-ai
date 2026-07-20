from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import User
from schemas.user_profile import UserProfileUpdate
from typing import Optional
from common.exceptions import UserNotFoundException, ValidationException

class UserProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: int) -> dict:
        """Get user profile by ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException(user_id)

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "gender": user.gender,
            "country": user.country,
            "state": user.state,
            "city": user.city,
            "github": user.github,
            "linkedin": user.linkedin,
            "profile_image": user.profile_image,
            "dob": user.dob,
            "role": user.role
        }

    def update_profile(self, user_id: int, data: UserProfileUpdate) -> dict:
        """Update user profile"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException(user_id)

        # Update fields if provided
        if data.name is not None:
            user.name = data.name
        if data.phone is not None:
            user.phone = data.phone
        if data.gender is not None:
            user.gender = data.gender
        if data.country is not None:
            user.country = data.country
        if data.state is not None:
            user.state = data.state
        if data.city is not None:
            user.city = data.city
        if data.github is not None:
            user.github = data.github
        if data.linkedin is not None:
            user.linkedin = data.linkedin
        if data.profile_image is not None:
            user.profile_image = data.profile_image
        if hasattr(data, 'dob') and data.dob is not None:
            user.dob = data.dob

        self.db.commit()
        return {"success": True, "message": "Profile updated successfully"}