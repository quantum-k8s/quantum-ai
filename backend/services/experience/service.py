from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Experience
from schemas.experience import ExperienceCreate, ExperienceUpdate
from typing import Optional, List
from common.exceptions import ResourceNotFoundException, ValidationException

class ExperienceService:
    def __init__(self, db: Session):
        self.db = db

    def get_experience_by_id(self, experience_id: int) -> dict:
        """Get experience by ID"""
        experience = self.db.query(Experience).filter(Experience.id == experience_id).first()
        if not experience:
            raise ResourceNotFoundException("Experience", f"id {experience_id}")

        return {
            "id": experience.id,
            "user_id": experience.user_id,
            "company": experience.company,
            "title": experience.title,
            "start_date": experience.start_date,
            "end_date": experience.end_date,
            "description": experience.description,
            "location": experience.location,
            "skills": experience.skills
        }

    def get_experiences_by_user(self, user_id: int) -> List[dict]:
        """Get all experiences for a user"""
        experiences = self.db.query(Experience).filter(Experience.user_id == user_id).all()
        return [{
            "id": exp.id,
            "user_id": exp.user_id,
            "company": exp.company,
            "title": exp.title,
            "start_date": exp.start_date,
            "end_date": exp.end_date,
            "description": exp.description,
            "location": exp.location,
            "skills": exp.skills
        } for exp in experiences]

    def create_experience(self, experience_data: ExperienceCreate) -> dict:
        """Create a new experience entry"""
        db_experience = Experience(**experience_data.dict())
        self.db.add(db_experience)
        self.db.commit()
        self.db.refresh(db_experience)

        return {
            "success": True,
            "message": "Experience created successfully",
            "id": db_experience.id
        }

    def update_experience(self, experience_id: int, data: ExperienceUpdate) -> dict:
        """Update experience entry"""
        experience = self.db.query(Experience).filter(Experience.id == experience_id).first()
        if not experience:
            raise ResourceNotFoundException("Experience", f"id {experience_id}")

        # Update fields if provided
        if data.company is not None:
            experience.company = data.company
        if data.title is not None:
            experience.title = data.title
        if data.start_date is not None:
            experience.start_date = data.start_date
        if data.end_date is not None:
            experience.end_date = data.end_date
        if data.description is not None:
            experience.description = data.description
        if data.location is not None:
            experience.location = data.location
        if data.skills is not None:
            experience.skills = data.skills

        self.db.commit()
        return {"success": True, "message": "Experience updated successfully"}

    def delete_experience(self, experience_id: int) -> dict:
        """Delete experience entry"""
        experience = self.db.query(Experience).filter(Experience.id == experience_id).first()
        if not experience:
            raise ResourceNotFoundException("Experience", f"id {experience_id}")

        self.db.delete(experience)
        self.db.commit()
        return {"success": True, "message": "Experience deleted successfully"}