from sqlalchemy.orm import Session
from models import User
from typing import Optional

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        db_user = User(**user_data)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        return self.db.query(User).filter(User.email == email).first() is not None

    def update_user(self, user: User) -> User:
        """Update user in database"""
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> bool:
        """Delete user from database"""
        self.db.delete(user)
        self.db.commit()
        return True

    def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
