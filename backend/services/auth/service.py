from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import get_password_hash, verify_password, create_access_token
from models import User
from schemas.auth import UserCreate, UserLogin, Token, UserResponse
from typing import Optional
from .repository import AuthRepository
from common.exceptions import UserAlreadyExistsException, InvalidCredentialsException, UserNotFoundException

class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepository(db)

    def signup(self, user_in: UserCreate) -> UserResponse:
        """Create a new user account"""
        # Check if user already exists
        if self.repository.user_exists(user_in.email):
            raise UserAlreadyExistsException(user_in.email)

        # Hash password (truncate if too long for bcrypt)
        password = str(user_in.password)[:72] if len(str(user_in.password)) > 72 else str(user_in.password)
        hashed_password = get_password_hash(password)

        # Create user data
        user_data = {
            "email": user_in.email,
            "password": hashed_password,
            "name": user_in.name,
            "dob": user_in.dob,
            "gender": user_in.gender,
            "country": user_in.country,
            "state": user_in.state,
            "city": user_in.city,
            "role": user_in.role,
            "phone": user_in.phone,
            "github": user_in.github,
            "linkedin": user_in.linkedin,
            "profile_image": user_in.profile_image,
            "verified": True
        }

        # Create user through repository
        db_user = self.repository.create_user(user_data)

        return db_user

    def login(self, user_in: UserLogin) -> Token:
        """Authenticate user and return access token"""
        user = self.repository.get_user_by_email(user_in.email)
        if not user or not verify_password(user_in.password, user.password):
            raise InvalidCredentialsException()

        # Generate access token
        access_token = create_access_token(subject=user.email)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        from core.security import get_current_user as get_current_user_from_token
        return get_current_user_from_token(self.db, token)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.repository.get_user_by_email(email)

    def update_user(self, user_id: int, user_data: dict) -> User:
        """Update user information"""
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)

        for key, value in user_data.items():
            if hasattr(user, key) and key != 'id':
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)

        self.db.delete(user)
        self.db.commit()
        return True

    def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination"""
        return self.repository.get_all_users(skip, limit)
