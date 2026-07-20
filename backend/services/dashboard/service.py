from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List, Dict
from common.exceptions import ResourceNotFoundException, ValidationException
from datetime import datetime, timedelta

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_candidate_dashboard_stats(self, user_id: int) -> Dict:
        """Get dashboard statistics for candidate"""
        from models import Resume, Job, Interview, Education, Experience, Certification

        # Get resume count and latest ATS score
        latest_resume = self.db.query(Resume).filter(Resume.user_id == user_id) \
            .order_by(Resume.upload_date.desc()).first()

        resume_score = latest_resume.ats_score if latest_resume else 0
        resume_count = self.db.query(Resume).filter(Resume.user_id == user_id).count()

        # Get job matches and applications
        job_matches = self.db.query(Job).filter(Job.user_id == user_id).count()
        upcoming_interviews = self.db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.interview_date >= datetime.now().date()
        ).count()

        # Get profile completion percentage
        profile_completion = self._calculate_profile_completion(user_id)

        # Get skill coverage
        skill_coverage = self._calculate_skill_coverage(user_id)

        return {
            "resume_score": resume_score,
            "ats_compatibility": min(resume_score * 1.1, 100),  # Cap at 100
            "job_matches": job_matches,
            "upcoming_interviews": upcoming_interviews,
            "profile_completion": profile_completion,
            "skill_coverage": skill_coverage,
            "resume_count": resume_count
        }

    def get_recruiter_dashboard_stats(self, user_id: int) -> Dict:
        """Get dashboard statistics for recruiter"""
        from models import Job, Interview, Resume

        # Get active candidates (resumes uploaded in last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_candidates = self.db.query(Resume).filter(
            Resume.upload_date >= thirty_days_ago
        ).count()

        # Get shortlisted candidates
        shortlisted = self.db.query(Interview).filter(
            Interview.status == "shortlisted"
        ).count()

        # Get open roles and urgent jobs
        open_roles = self.db.query(Job).filter(
            Job.user_id == user_id,
            Job.status == "open"
        ).count()

        urgent_jobs = self.db.query(Job).filter(
            Job.user_id == user_id,
            Job.status == "open",
            Job.expiration_date <= datetime.now() + timedelta(days=7)
        ).count()

        # Get average match score
        interviews = self.db.query(Interview).filter(Interview.user_id == user_id).all()
        avg_match_score = sum([i.score for i in interviews if i.score]) / len([i.score for i in interviews if i.score]) if interviews else 0

        return {
            "active_candidates": active_candidates,
            "shortlisted": shortlisted,
            "open_roles": open_roles,
            "urgent_jobs": urgent_jobs,
            "avg_match_score": round(avg_match_score, 1) if avg_match_score else 0
        }

    def get_recent_activity(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent activity for dashboard"""
        from models import Resume, Job, Interview, Education, Experience, Certification

        # Get recent resumes
        recent_resumes = self.db.query(Resume).filter(Resume.user_id == user_id) \
            .order_by(Resume.upload_date.desc()).limit(limit).all()

        # Get recent jobs
        recent_jobs = self.db.query(Job).filter(Job.user_id == user_id) \
            .order_by(Job.posted_date.desc()).limit(limit).all()

        # Get recent interviews
        recent_interviews = self.db.query(Interview).filter(Interview.user_id == user_id) \
            .order_by(Interview.interview_date.desc()).limit(limit).all()

        # Combine and sort by date
        activities = []

        for resume in recent_resumes:
            activities.append({
                "type": "resume",
                "action": "uploaded",
                "title": resume.title,
                "date": resume.upload_date,
                "id": resume.id
            })

        for job in recent_jobs:
            activities.append({
                "type": "job",
                "action": "posted",
                "title": job.title,
                "date": job.posted_date,
                "id": job.id
            })

        for interview in recent_interviews:
            activities.append({
                "type": "interview",
                "action": "scheduled",
                "title": interview.title,
                "date": interview.interview_date,
                "id": interview.id
            })

        # Sort by date descending
        activities.sort(key=lambda x: x["date"], reverse=True)

        return activities[:limit]

    def get_skill_distribution(self, user_id: int) -> List[Dict]:
        """Get skill distribution for dashboard"""
        from models import Education, Experience, Certification

        # Get skills from education
        education_skills = []
        educations = self.db.query(Education).filter(Education.user_id == user_id).all()
        for edu in educations:
            if edu.skills:
                education_skills.extend(edu.skills.split(','))

        # Get skills from experience
        experience_skills = []
        experiences = self.db.query(Experience).filter(Experience.user_id == user_id).all()
        for exp in experiences:
            if exp.skills:
                experience_skills.extend(exp.skills.split(','))

        # Get skills from certifications
        certification_skills = []
        certifications = self.db.query(Certification).filter(Certification.user_id == user_id).all()
        for cert in certifications:
            if cert.skills:
                certification_skills.extend(cert.skills.split(','))

        # Combine and count skills
        all_skills = education_skills + experience_skills + certification_skills
        skill_counts = {}

        for skill in all_skills:
            skill = skill.strip()
            if skill:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        # Get top skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:6]

        return [{
            "name": skill[0],
            "value": skill[1]
        } for skill in top_skills]

    def get_job_match_trend(self, user_id: int) -> List[Dict]:
        """Get job match trend for last 6 months"""
        from models import Job

        # Get job matches by month
        six_months_ago = datetime.now() - timedelta(days=180)
        jobs = self.db.query(Job).filter(
            Job.user_id == user_id,
            Job.posted_date >= six_months_ago
        ).all()

        # Group by month
        monthly_matches = {}
        for job in jobs:
            month = job.posted_date.strftime("%Y-%m")
            monthly_matches[month] = monthly_matches.get(month, 0) + 1

        # Fill in missing months
        trend_data = []
        current_date = six_months_ago
        while current_date <= datetime.now():
            month = current_date.strftime("%Y-%m")
            count = monthly_matches.get(month, 0)
            trend_data.append({
                "month": current_date.strftime("%b %Y"),
                "matches": count
            })
            current_date += timedelta(days=30)

        return trend_data

    def _calculate_profile_completion(self, user_id: int) -> float:
        """Calculate profile completion percentage"""
        from models import User

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return 0

        # Calculate completion based on filled fields
        fields_filled = 0
        total_fields = 10  # Adjust based on your user model

        if user.name: fields_filled += 1
        if user.email: fields_filled += 1
        if user.phone: fields_filled += 1
        if user.gender: fields_filled += 1
        if user.country: fields_filled += 1
        if user.state: fields_filled += 1
        if user.city: fields_filled += 1
        if user.github: fields_filled += 1
        if user.linkedin: fields_filled += 1
        if user.profile_image: fields_filled += 1

        return round((fields_filled / total_fields) * 100, 1)

    def _calculate_skill_coverage(self, user_id: int) -> float:
        """Calculate skill coverage percentage"""
        from models import Job

        # Get user skills from profile, education, experience, etc.
        user_skills = self._get_all_user_skills(user_id)

        if not user_skills:
            return 0

        # Get required skills from job market
        market_skills = self._get_market_skills()

        if not market_skills:
            return 100

        # Calculate coverage
        covered_skills = len(set(user_skills) & set(market_skills))
        coverage = (covered_skills / len(market_skills)) * 100

        return round(coverage, 1)

    def _get_all_user_skills(self, user_id: int) -> List[str]:
        """Get all skills for a user"""
        from models import Education, Experience, Certification

        skills = []

        # Get skills from education
        educations = self.db.query(Education).filter(Education.user_id == user_id).all()
        for edu in educations:
            if edu.skills:
                skills.extend([s.strip() for s in edu.skills.split(',')])

        # Get skills from experience
        experiences = self.db.query(Experience).filter(Experience.user_id == user_id).all()
        for exp in experiences:
            if exp.skills:
                skills.extend([s.strip() for s in exp.skills.split(',')])

        # Get skills from certifications
        certifications = self.db.query(Certification).filter(Certification.user_id == user_id).all()
        for cert in certifications:
            if cert.skills:
                skills.extend([s.strip() for s in cert.skills.split(',')])

        return list(set(skills))  # Remove duplicates

    def _get_market_skills(self) -> List[str]:
        """Get in-demand skills from job market"""
        from models import Job

        # Get skills from recent job postings
        recent_jobs = self.db.query(Job).filter(
            Job.posted_date >= datetime.now() - timedelta(days=90)
        ).all()

        market_skills = []
        for job in recent_jobs:
            if job.skills_required:
                market_skills.extend([s.strip() for s in job.skills_required.split(',')])

        # Get most common skills
        skill_counts = {}
        for skill in market_skills:
            if skill:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        # Return top 50 skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:50]
        return [skill[0] for skill in top_skills]