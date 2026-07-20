from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import Certification
from schemas.certification import CertificationCreate, CertificationUpdate
from typing import Optional, List
from common.exceptions import ResourceNotFoundException, ValidationException

class CertificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_certification_by_id(self, certification_id: int) -> dict:
        """Get certification by ID"""
        certification = self.db.query(Certification).filter(Certification.id == certification_id).first()
        if not certification:
            raise ResourceNotFoundException("Certification", f"id {certification_id}")

        return {
            "id": certification.id,
            "user_id": certification.user_id,
            "name": certification.name,
            "organization": certification.organization,
            "issue_date": certification.issue_date,
            "expiration_date": certification.expiration_date,
            "credential_id": certification.credential_id,
            "credential_url": certification.credential_url,
            "skills": certification.skills
        }

    def get_certifications_by_user(self, user_id: int) -> List[dict]:
        """Get all certifications for a user"""
        certifications = self.db.query(Certification).filter(Certification.user_id == user_id).all()
        return [{
            "id": cert.id,
            "user_id": cert.user_id,
            "name": cert.name,
            "organization": cert.organization,
            "issue_date": cert.issue_date,
            "expiration_date": cert.expiration_date,
            "credential_id": cert.credential_id,
            "credential_url": cert.credential_url,
            "skills": cert.skills
        } for cert in certifications]

    def create_certification(self, certification_data: CertificationCreate) -> dict:
        """Create a new certification entry"""
        db_certification = Certification(**certification_data.dict())
        self.db.add(db_certification)
        self.db.commit()
        self.db.refresh(db_certification)

        return {
            "success": True,
            "message": "Certification created successfully",
            "id": db_certification.id
        }

    def update_certification(self, certification_id: int, data: CertificationUpdate) -> dict:
        """Update certification entry"""
        certification = self.db.query(Certification).filter(Certification.id == certification_id).first()
        if not certification:
            raise ResourceNotFoundException("Certification", f"id {certification_id}")

        # Update fields if provided
        if data.name is not None:
            certification.name = data.name
        if data.organization is not None:
            certification.organization = data.organization
        if data.issue_date is not None:
            certification.issue_date = data.issue_date
        if data.expiration_date is not None:
            certification.expiration_date = data.expiration_date
        if data.credential_id is not None:
            certification.credential_id = data.credential_id
        if data.credential_url is not None:
            certification.credential_url = data.credential_url
        if data.skills is not None:
            certification.skills = data.skills

        self.db.commit()
        return {"success": True, "message": "Certification updated successfully"}

    def delete_certification(self, certification_id: int) -> dict:
        """Delete certification entry"""
        certification = self.db.query(Certification).filter(Certification.id == certification_id).first()
        if not certification:
            raise ResourceNotFoundException("Certification", f"id {certification_id}")

        self.db.delete(certification)
        self.db.commit()
        return {"success": True, "message": "Certification deleted successfully"}