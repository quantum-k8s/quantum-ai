from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Job
from schemas.jobs import JobCreate, JobUpdate
from typing import Optional, List
from common.exceptions import ResourceNotFoundException, ValidationException

class JobService:
    def __init__(self, db: Session):
        self.db = db

    def get_job_by_id(self, job_id: int) -> dict:
        """Get job by ID"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ResourceNotFoundException("Job", f"id {job_id}")

        return {
            "id": job.id,
            "user_id": job.user_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "requirements": job.requirements,
            "salary": job.salary,
            "job_type": job.job_type,
            "posted_date": job.posted_date,
            "expiration_date": job.expiration_date,
            "status": job.status,
            "skills_required": job.skills_required
        }

    def get_jobs_by_user(self, user_id: int) -> List[dict]:
        """Get all jobs for a user"""
        jobs = self.db.query(Job).filter(Job.user_id == user_id).all()
        return [{
            "id": job.id,
            "user_id": job.user_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "requirements": job.requirements,
            "salary": job.salary,
            "job_type": job.job_type,
            "posted_date": job.posted_date,
            "expiration_date": job.expiration_date,
            "status": job.status,
            "skills_required": job.skills_required
        } for job in jobs]

    def get_all_jobs(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all jobs with pagination"""
        jobs = self.db.query(Job).offset(skip).limit(limit).all()
        return [{
            "id": job.id,
            "user_id": job.user_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "requirements": job.requirements,
            "salary": job.salary,
            "job_type": job.job_type,
            "posted_date": job.posted_date,
            "expiration_date": job.expiration_date,
            "status": job.status,
            "skills_required": job.skills_required
        } for job in jobs]

    def create_job(self, job_data: JobCreate) -> dict:
        """Create a new job posting"""
        db_job = Job(**job_data.dict())
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)

        return {
            "success": True,
            "message": "Job created successfully",
            "id": db_job.id
        }

    def update_job(self, job_id: int, data: JobUpdate) -> dict:
        """Update job posting"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ResourceNotFoundException("Job", f"id {job_id}")

        # Update fields if provided
        if data.title is not None:
            job.title = data.title
        if data.company is not None:
            job.company = data.company
        if data.location is not None:
            job.location = data.location
        if data.description is not None:
            job.description = data.description
        if data.requirements is not None:
            job.requirements = data.requirements
        if data.salary is not None:
            job.salary = data.salary
        if data.job_type is not None:
            job.job_type = data.job_type
        if data.posted_date is not None:
            job.posted_date = data.posted_date
        if data.expiration_date is not None:
            job.expiration_date = data.expiration_date
        if data.status is not None:
            job.status = data.status
        if data.skills_required is not None:
            job.skills_required = data.skills_required

        self.db.commit()
        return {"success": True, "message": "Job updated successfully"}

    def delete_job(self, job_id: int) -> dict:
        """Delete job posting"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ResourceNotFoundException("Job", f"id {job_id}")

        self.db.delete(job)
        self.db.commit()
        return {"success": True, "message": "Job deleted successfully"}

    def search_jobs(self, query: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Search jobs by title, company, or skills"""
        jobs = self.db.query(Job).filter(
            Job.title.ilike(f"%{query}%") |
            Job.company.ilike(f"%{query}%") |
            Job.skills_required.ilike(f"%{query}%")
        ).offset(skip).limit(limit).all()

        return [{
            "id": job.id,
            "user_id": job.user_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "requirements": job.requirements,
            "salary": job.salary,
            "job_type": job.job_type,
            "posted_date": job.posted_date,
            "expiration_date": job.expiration_date,
            "status": job.status,
            "skills_required": job.skills_required
        } for job in jobs]