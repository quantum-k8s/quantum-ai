from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from services.auth.service import AuthService
from services.user_profile.service import UserProfileService

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency injection for AuthService"""
    return AuthService(db)

def get_user_profile_service(db: Session = Depends(get_db)) -> UserProfileService:
    """Dependency injection for UserProfileService"""
    return UserProfileService(db)

def get_education_service(db: Session = Depends(get_db)):
    """Dependency injection for EducationService"""
    from services.education.service import EducationService
    return EducationService(db)

def get_experience_service(db: Session = Depends(get_db)):
    """Dependency injection for ExperienceService"""
    from services.experience.service import ExperienceService
    return ExperienceService(db)

def get_certification_service(db: Session = Depends(get_db)):
    """Dependency injection for CertificationService"""
    from services.certification.service import CertificationService
    return CertificationService(db)

def get_jobs_service(db: Session = Depends(get_db)):
    """Dependency injection for JobService"""
    from services.jobs.service import JobService
    return JobService(db)

def get_notifications_service(db: Session = Depends(get_db)):
    """Dependency injection for NotificationService"""
    from services.notifications.service import NotificationService
    return NotificationService(db)

def get_interview_service(db: Session = Depends(get_db)):
    """Dependency injection for InterviewService"""
    from services.interview.service import InterviewService
    return InterviewService(db)

def get_resume_service(db: Session = Depends(get_db)):
    """Dependency injection for ResumeService"""
    from services.resume.service import ResumeService
    return ResumeService(db)

def get_dashboard_service(db: Session = Depends(get_db)):
    """Dependency injection for DashboardService"""
    from services.dashboard.service import DashboardService
    return DashboardService(db)

def get_ai_analysis_service(db: Session = Depends(get_db)):
    """Dependency injection for AIAnalysisService"""
    from services.ai_analysis.service import AIAnalysisService
    return AIAnalysisService(db)

# Add more dependency providers as needed for other services
