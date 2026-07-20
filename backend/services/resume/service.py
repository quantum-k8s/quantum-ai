from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from models import Resume
from schemas.resume import ResumeCreate, ResumeUpdate
from typing import Optional, List
from common.exceptions import ResourceNotFoundException, ValidationException
import os
import uuid
from datetime import datetime

class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    def get_resume_by_id(self, resume_id: int) -> dict:
        """Get resume by ID"""
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResourceNotFoundException("Resume", f"id {resume_id}")

        return {
            "id": resume.id,
            "user_id": resume.user_id,
            "title": resume.title,
            "file_path": resume.file_path,
            "file_name": resume.file_name,
            "file_type": resume.file_type,
            "file_size": resume.file_size,
            "upload_date": resume.upload_date,
            "status": resume.status,
            "ats_score": resume.ats_score,
            "analysis_completed": resume.analysis_completed,
            "analysis_date": resume.analysis_date
        }

    def get_resumes_by_user(self, user_id: int) -> List[dict]:
        """Get all resumes for a user"""
        resumes = self.db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.upload_date.desc()).all()
        return [{
            "id": resume.id,
            "user_id": resume.user_id,
            "title": resume.title,
            "file_path": resume.file_path,
            "file_name": resume.file_name,
            "file_type": resume.file_type,
            "file_size": resume.file_size,
            "upload_date": resume.upload_date,
            "status": resume.status,
            "ats_score": resume.ats_score,
            "analysis_completed": resume.analysis_completed,
            "analysis_date": resume.analysis_date
        } for resume in resumes]

    def upload_resume(self, user_id: int, file: UploadFile) -> dict:
        """Upload a new resume file"""
        # Validate file type
        if not file.content_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            raise ValidationException("Invalid file type. Only PDF and Word documents are allowed.")

        # Validate file size (5MB limit)
        file_size_mb = len(file.file.read()) / (1024 * 1024)
        file.file.seek(0)  # Reset file pointer

        if file_size_mb > 5:
            raise ValidationException("File size exceeds 5MB limit.")

        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"resume_{uuid.uuid4().hex}{file_ext}"

        # Create upload directory if it doesn't exist
        upload_dir = "uploads/resumes"
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Create resume record
        db_resume = Resume(
            user_id=user_id,
            title=file.filename,
            file_path=file_path,
            file_name=unique_filename,
            file_type=file.content_type,
            file_size=file_size_mb,
            upload_date=datetime.now(),
            status="uploaded",
            ats_score=0,
            analysis_completed=False
        )

        self.db.add(db_resume)
        self.db.commit()
        self.db.refresh(db_resume)

        return {
            "success": True,
            "message": "Resume uploaded successfully",
            "id": db_resume.id,
            "file_path": db_resume.file_path
        }

    def update_resume_metadata(self, resume_id: int, data: ResumeUpdate) -> dict:
        """Update resume metadata"""
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResourceNotFoundException("Resume", f"id {resume_id}")

        # Update fields if provided
        if data.title is not None:
            resume.title = data.title
        if data.status is not None:
            resume.status = data.status

        self.db.commit()
        return {"success": True, "message": "Resume metadata updated successfully"}

    def delete_resume(self, resume_id: int) -> dict:
        """Delete resume"""
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResourceNotFoundException("Resume", f"id {resume_id}")

        # Delete file if it exists
        if os.path.exists(resume.file_path):
            try:
                os.remove(resume.file_path)
            except OSError:
                pass  # Ignore file deletion errors

        self.db.delete(resume)
        self.db.commit()
        return {"success": True, "message": "Resume deleted successfully"}

    def update_ats_score(self, resume_id: int, score: float) -> dict:
        """Update ATS score for a resume"""
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResourceNotFoundException("Resume", f"id {resume_id}")

        resume.ats_score = score
        resume.analysis_completed = True
        resume.analysis_date = datetime.now()

        self.db.commit()
        return {"success": True, "message": "ATS score updated successfully"}

    def get_resume_analysis_status(self, resume_id: int) -> dict:
        """Get analysis status for a resume"""
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResourceNotFoundException("Resume", f"id {resume_id}")

        return {
            "analysis_completed": resume.analysis_completed,
            "ats_score": resume.ats_score,
            "analysis_date": resume.analysis_date
        }