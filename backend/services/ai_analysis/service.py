from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List, Dict
from common.exceptions import ResourceNotFoundException, ValidationException
import os
import json
from datetime import datetime

# Import existing AI services
from services.resume_analyzer import analyze_resume_content
from services.ats_checker import check_ats_compatibility
from services.skill_gap import detect_skill_gaps
from services.nlp_skill_detector import extract_skills_from_text
from services.resume_suggestions import generate_resume_suggestions
from services.resume_rewriter import rewrite_resume_content
from services.job_match import match_jobs_to_resume
from services.career_predictor import predict_career_path
from services.resume_feedback import generate_resume_feedback

class AIAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def analyze_resume_ai(self, resume_id: int) -> Dict:
        """Complete AI analysis pipeline for a resume"""
        from models import Resume, ResumeAnalysis

        # Get resume
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResourceNotFoundException("Resume", f"id {resume_id}")

        # Check if already analyzed
        existing_analysis = self.db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume_id).first()
        if existing_analysis:
            return {
                "message": "Resume already analyzed",
                "analysis_id": existing_analysis.id,
                "status": "already_completed"
            }

        # Read resume file
        if not os.path.exists(resume.file_path):
            raise ValidationException("Resume file not found")

        with open(resume.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            resume_text = f.read()

        # Step 1: Extract text and skills
        extracted_skills = extract_skills_from_text(resume_text)

        # Step 2: Analyze resume content
        content_analysis = analyze_resume_content(resume_text)

        # Step 3: Check ATS compatibility
        ats_score = check_ats_compatibility(resume_text, extracted_skills)

        # Step 4: Detect skill gaps
        skill_gap_analysis = detect_skill_gaps(extracted_skills)

        # Step 5: Generate suggestions
        suggestions = generate_resume_suggestions(content_analysis, ats_score, skill_gap_analysis)

        # Step 6: Generate feedback
        feedback = generate_resume_feedback(content_analysis, ats_score)

        # Step 7: Predict career path
        career_prediction = predict_career_path(extracted_skills)

        # Save analysis results
        analysis = ResumeAnalysis(
            resume_id=resume_id,
            user_id=resume.user_id,
            analysis_date=datetime.now(),
            ats_score=ats_score,
            content_analysis=json.dumps(content_analysis),
            skill_analysis=json.dumps({
                "extracted_skills": extracted_skills,
                "skill_gaps": skill_gap_analysis
            }),
            suggestions=json.dumps(suggestions),
            feedback=feedback,
            career_prediction=json.dumps(career_prediction),
            status="completed"
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        # Update resume with ATS score
        resume.ats_score = ats_score
        resume.analysis_completed = True
        resume.analysis_date = datetime.now()
        self.db.commit()

        return {
            "success": True,
            "message": "Resume analysis completed successfully",
            "analysis_id": analysis.id,
            "ats_score": ats_score,
            "status": "completed"
        }

    def generate_resume_rewrite(self, resume_id: int, target_job: str = None) -> Dict:
        """Generate AI-powered resume rewrite"""
        from models import Resume, ResumeAnalysis

        # Get resume and analysis
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResourceNotFoundException("Resume", f"id {resume_id}")

        analysis = self.db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume_id).first()
        if not analysis:
            raise ValidationException("Resume must be analyzed first")

        # Read resume file
        with open(resume.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            resume_text = f.read()

        # Generate rewrite
        rewritten_resume = rewrite_resume_content(
            original_content=resume_text,
            ats_score=analysis.ats_score,
            target_job=target_job,
            suggestions=json.loads(analysis.suggestions)
        )

        return {
            "success": True,
            "rewritten_resume": rewritten_resume,
            "message": "Resume rewrite generated successfully"
        }

    def get_job_matches(self, resume_id: int, limit: int = 10) -> Dict:
        """Get job matches for a resume using AI matching"""
        from models import Resume, ResumeAnalysis, Job

        # Get resume and analysis
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResourceNotFoundException("Resume", f"id {resume_id}")

        analysis = self.db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume_id).first()
        if not analysis:
            raise ValidationException("Resume must be analyzed first")

        # Get all jobs
        all_jobs = self.db.query(Job).all()

        # Match jobs using AI
        matched_jobs = match_jobs_to_resume(
            resume_text=open(resume.file_path, 'r', encoding='utf-8', errors='ignore').read(),
            extracted_skills=json.loads(analysis.skill_analysis)["extracted_skills"],
            all_jobs=all_jobs,
            limit=limit
        )

        return {
            "success": True,
            "matched_jobs": matched_jobs,
            "count": len(matched_jobs),
            "message": f"Found {len(matched_jobs)} job matches"
        }

    def get_career_insights(self, user_id: int) -> Dict:
        """Get career insights and predictions for a user"""
        from models import Resume, ResumeAnalysis, Education, Experience, Certification

        # Get all resumes for user
        resumes = self.db.query(Resume).filter(Resume.user_id == user_id).all()
        if not resumes:
            raise ResourceNotFoundException("User", f"id {user_id} has no resumes")

        # Get all skills from user's profile
        all_skills = self._get_all_user_skills(user_id)

        # Get career predictions for each resume
        career_insights = []
        for resume in resumes:
            analysis = self.db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).first()
            if analysis:
                career_prediction = json.loads(analysis.career_prediction)
                career_insights.append({
                    "resume_id": resume.id,
                    "resume_title": resume.title,
                    "career_prediction": career_prediction
                })

        # Get overall career prediction
        overall_prediction = predict_career_path(all_skills)

        return {
            "success": True,
            "user_skills": all_skills,
            "career_insights": career_insights,
            "overall_prediction": overall_prediction,
            "message": "Career insights generated successfully"
        }

    def get_skill_development_plan(self, user_id: int, target_role: str) -> Dict:
        """Generate a skill development plan for a target role"""
        from models import Resume, ResumeAnalysis

        # Get user skills
        user_skills = self._get_all_user_skills(user_id)

        # Get target role skills (from job market)
        target_skills = self._get_target_role_skills(target_role)

        # Analyze skill gaps
        skill_gaps = detect_skill_gaps(user_skills, target_skills=target_skills)

        # Generate learning roadmap
        learning_plan = self._generate_learning_roadmap(skill_gaps, target_role)

        return {
            "success": True,
            "current_skills": user_skills,
            "required_skills": target_skills,
            "skill_gaps": skill_gaps,
            "learning_plan": learning_plan,
            "message": "Skill development plan generated successfully"
        }

    def _get_all_user_skills(self, user_id: int) -> List[str]:
        """Get all skills for a user from education, experience, and certifications"""
        from models import Education, Experience, Certification

        skills = set()

        # Get skills from education
        educations = self.db.query(Education).filter(Education.user_id == user_id).all()
        for edu in educations:
            if edu.skills:
                skills.update([s.strip() for s in edu.skills.split(',')])

        # Get skills from experience
        experiences = self.db.query(Experience).filter(Experience.user_id == user_id).all()
        for exp in experiences:
            if exp.skills:
                skills.update([s.strip() for s in exp.skills.split(',')])

        # Get skills from certifications
        certifications = self.db.query(Certification).filter(Certification.user_id == user_id).all()
        for cert in certifications:
            if cert.skills:
                skills.update([s.strip() for s in cert.skills.split(',')])

        return list(skills)

    def _get_target_role_skills(self, target_role: str) -> List[str]:
        """Get skills required for a target role"""
        from models import Job

        # Get skills from jobs matching the target role
        target_jobs = self.db.query(Job).filter(
            Job.title.ilike(f"%{target_role}%") |
            Job.description.ilike(f"%{target_role}%")
        ).all()

        all_skills = []
        for job in target_jobs:
            if job.skills_required:
                all_skills.extend([s.strip() for s in job.skills_required.split(',')])

        # Get most common skills
        skill_counts = {}
        for skill in all_skills:
            if skill:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        # Return top skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        return [skill[0] for skill in top_skills]

    def _generate_learning_roadmap(self, skill_gaps: List[Dict], target_role: str) -> List[Dict]:
        """Generate a learning roadmap based on skill gaps"""
        learning_plan = []

        for gap in skill_gaps:
            skill = gap.get('skill', '')
            importance = gap.get('importance', 'medium')

            # Generate learning resources based on skill type
            resources = self._get_learning_resources(skill, target_role)

            learning_plan.append({
                "skill": skill,
                "importance": importance,
                "learning_resources": resources,
                "estimated_time": self._estimate_learning_time(skill)
            })

        return learning_plan

    def _get_learning_resources(self, skill: str, target_role: str) -> List[Dict]:
        """Get learning resources for a specific skill"""
        # This would be enhanced with actual learning resource APIs
        base_resources = [
            {
                "type": "online_course",
                "platform": "Coursera",
                "url": f"https://www.coursera.org/search?query={skill.replace(' ', '+')}",
                "description": f"Coursera courses for {skill}"
            },
            {
                "type": "online_course",
                "platform": "Udemy",
                "url": f"https://www.udemy.com/courses/search/?q={skill.replace(' ', '+')}",
                "description": f"Udemy courses for {skill}"
            },
            {
                "type": "documentation",
                "platform": "Official Docs",
                "url": f"https://www.google.com/search?q={skill}+official+documentation",
                "description": f"Official documentation for {skill}"
            }
        ]

        # Add role-specific resources
        if "python" in skill.lower():
            base_resources.append({
                "type": "book",
                "title": "Python Crash Course",
                "author": "Eric Matthes",
                "description": "Great book for learning Python"
            })

        if "machine learning" in skill.lower():
            base_resources.append({
                "type": "book",
                "title": "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow",
                "author": "Aurélien Géron",
                "description": "Comprehensive ML book"
            })

        return base_resources

    def _estimate_learning_time(self, skill: str) -> str:
        """Estimate learning time for a skill"""
        # Simple estimation based on skill complexity
        complex_skills = ['machine learning', 'deep learning', 'cloud architecture', 'distributed systems']
        medium_skills = ['python', 'sql', 'docker', 'react', 'node.js']
        basic_skills = ['git', 'linux', 'excel', 'html', 'css']

        if any(cs in skill.lower() for cs in complex_skills):
            return "4-6 weeks"
        elif any(ms in skill.lower() for ms in medium_skills):
            return "2-4 weeks"
        else:
            return "1-2 weeks"