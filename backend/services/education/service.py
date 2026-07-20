from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Education
from schemas.education import EducationCreate, EducationUpdate
from typing import Optional, List
from common.exceptions import ResourceNotFoundException, ValidationException

class EducationService:
    def __init__(self, db: Session):
        self.db = db

    def get_education_by_id(self, education_id: int) -> dict:
        """Get education by ID"""
        education = self.db.query(Education).filter(Education.id == education_id).first()
        if not education:
            raise ResourceNotFoundException("Education", f"id {education_id}")

        return {
            "id": education.id,
            "user_id": education.user_id,
            "institution": education.institution,
            "degree": education.degree,
            "field_of_study": education.field_of_study,
            "start_date": education.start_date,
            "end_date": education.end_date,
            "grade": education.grade,
            "description": education.description
        }

    def get_educations_by_user(self, user_id: int) -> List[dict]:
        """Get all educations for a user"""
        educations = self.db.query(Education).filter(Education.user_id == user_id).all()
        return [{
            "id": edu.id,
            "user_id": edu.user_id,
            "institution": edu.institution,
            "degree": edu.degree,
            "field_of_study": edu.field_of_study,
            "start_date": edu.start_date,
            "end_date": edu.end_date,
            "grade": edu.grade,
            "description": edu.description
        } for edu in educations]

    def create_education(self, education_data: EducationCreate) -> dict:
        """Create a new education entry"""
        db_education = Education(**education_data.dict())
        self.db.add(db_education)
        self.db.commit()
        self.db.refresh(db_education)

        return {
            "success": True,
            "message": "Education created successfully",
            "id": db_education.id
        }

    def update_education(self, education_id: int, data: EducationUpdate) -> dict:
        """Update education entry"""
        education = self.db.query(Education).filter(Education.id == education_id).first()
        if not education:
            raise ResourceNotFoundException("Education", f"id {education_id}")

        # Update fields if provided
        if data.institution is not None:
            education.institution = data.institution
        if data.degree is not None:
            education.degree = data.degree
        if data.field_of_study is not None:
            education.field_of_study = data.field_of_study
        if data.start_date is not None:
            education.start_date = data.start_date
        if data.end_date is not None:
            education.end_date = data.end_date
        if data.grade is not None:
            education.grade = data.grade
        if data.description is not None:
            education.description = data.description

        self.db.commit()
        return {"success": True, "message": "Education updated successfully"}

    def delete_education(self, education_id: int) -> dict:
        """Delete education entry"""
        education = self.db.query(Education).filter(Education.id == education_id).first()
        if not education:
            raise ResourceNotFoundException("Education", f"id {education_id}")

        self.db.delete(education)
        self.db.commit()
        return {"success": True, "message": "Education deleted successfully"}