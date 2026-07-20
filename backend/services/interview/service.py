from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Interview
from schemas.interview import InterviewCreate, InterviewUpdate
from typing import Optional, List
from common.exceptions import ResourceNotFoundException, ValidationException

class InterviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_interview_by_id(self, interview_id: int) -> dict:
        """Get interview by ID"""
        interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ResourceNotFoundException("Interview", f"id {interview_id}")

        return {
            "id": interview.id,
            "user_id": interview.user_id,
            "job_id": interview.job_id,
            "title": interview.title,
            "description": interview.description,
            "interview_date": interview.interview_date,
            "interview_time": interview.interview_time,
            "location": interview.location,
            "interview_type": interview.interview_type,
            "status": interview.status,
            "notes": interview.notes,
            "feedback": interview.feedback,
            "score": interview.score
        }

    def get_interviews_by_user(self, user_id: int) -> List[dict]:
        """Get all interviews for a user"""
        interviews = self.db.query(Interview).filter(Interview.user_id == user_id).all()
        return [{
            "id": interview.id,
            "user_id": interview.user_id,
            "job_id": interview.job_id,
            "title": interview.title,
            "description": interview.description,
            "interview_date": interview.interview_date,
            "interview_time": interview.interview_time,
            "location": interview.location,
            "interview_type": interview.interview_type,
            "status": interview.status,
            "notes": interview.notes,
            "feedback": interview.feedback,
            "score": interview.score
        } for interview in interviews]

    def create_interview(self, interview_data: InterviewCreate) -> dict:
        """Create a new interview"""
        db_interview = Interview(**interview_data.dict())
        self.db.add(db_interview)
        self.db.commit()
        self.db.refresh(db_interview)

        return {
            "success": True,
            "message": "Interview created successfully",
            "id": db_interview.id
        }

    def update_interview(self, interview_id: int, data: InterviewUpdate) -> dict:
        """Update interview"""
        interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ResourceNotFoundException("Interview", f"id {interview_id}")

        # Update fields if provided
        if data.job_id is not None:
            interview.job_id = data.job_id
        if data.title is not None:
            interview.title = data.title
        if data.description is not None:
            interview.description = data.description
        if data.interview_date is not None:
            interview.interview_date = data.interview_date
        if data.interview_time is not None:
            interview.interview_time = data.interview_time
        if data.location is not None:
            interview.location = data.location
        if data.interview_type is not None:
            interview.interview_type = data.interview_type
        if data.status is not None:
            interview.status = data.status
        if data.notes is not None:
            interview.notes = data.notes
        if data.feedback is not None:
            interview.feedback = data.feedback
        if data.score is not None:
            interview.score = data.score

        self.db.commit()
        return {"success": True, "message": "Interview updated successfully"}

    def delete_interview(self, interview_id: int) -> dict:
        """Delete interview"""
        interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ResourceNotFoundException("Interview", f"id {interview_id}")

        self.db.delete(interview)
        self.db.commit()
        return {"success": True, "message": "Interview deleted successfully"}

    def get_upcoming_interviews(self, user_id: int) -> List[dict]:
        """Get upcoming interviews for a user"""
        from datetime import datetime
        today = datetime.now().date()

        interviews = self.db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.interview_date >= today
        ).order_by(Interview.interview_date.asc()).all()

        return [{
            "id": interview.id,
            "user_id": interview.user_id,
            "job_id": interview.job_id,
            "title": interview.title,
            "description": interview.description,
            "interview_date": interview.interview_date,
            "interview_time": interview.interview_time,
            "location": interview.location,
            "interview_type": interview.interview_type,
            "status": interview.status,
            "notes": interview.notes,
            "feedback": interview.feedback,
            "score": interview.score
        } for interview in interviews]

    def get_past_interviews(self, user_id: int) -> List[dict]:
        """Get past interviews for a user"""
        from datetime import datetime
        today = datetime.now().date()

        interviews = self.db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.interview_date < today
        ).order_by(Interview.interview_date.desc()).all()

        return [{
            "id": interview.id,
            "user_id": interview.user_id,
            "job_id": interview.job_id,
            "title": interview.title,
            "description": interview.description,
            "interview_date": interview.interview_date,
            "interview_time": interview.interview_time,
            "location": interview.location,
            "interview_type": interview.interview_type,
            "status": interview.status,
            "notes": interview.notes,
            "feedback": interview.feedback,
            "score": interview.score
        } for interview in interviews]