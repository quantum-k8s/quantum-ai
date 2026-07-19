from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, User
from core.security import get_current_user
from services.job_recommender import recommend_jobs

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    latest = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.id.desc()).first()
    if latest is None:
        return {"success": False}
    return {
        "success": True,
        "resumeScore": latest.resume_score,
        "atsScore": latest.ats_score,
        "careerLevel": latest.career_level,
        "role": latest.detected_role,
        "skills": latest.skills.split(",") if latest.skills else [],
        "roadmap": latest.roadmap.split("\n") if latest.roadmap else [],
        "suggestions": latest.ai_suggestions.split("\n") if latest.ai_suggestions else []
    }

@router.get("/candidate-dashboard")
def candidate_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    latest = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.id.desc()).first()
    if not latest:
        return {
            "stats": {"resumeScore": 0, "atsScore": 0, "jobMatches": 0, "skillCoverage": 0},
            "aiInsights": [],
            "jobMatches": [],
            "recentActivity": [],
            "recentUploads": [],
            "interviews": []
        }

    skills = latest.skills.split(",") if latest.skills else []
    recommended = recommend_jobs(skills)
    matches = []
    for i, job in enumerate(recommended[:4]):
        matches.append({
            "id": i + 1,
            "logo": job["companies"][0][:2].upper() if job.get("companies") else "AI",
            "role": job["role"],
            "company": ", ".join(job["companies"]) if job.get("companies") else "Unknown",
            "location": "Remote",
            "match": job["match"]
        })

    return {
        "stats": {
            "resumeScore": latest.resume_score,
            "atsScore": latest.ats_score,
            "jobMatches": len(matches),
            "skillCoverage": min(len(skills) * 10, 100)
        },
        "aiInsights": [
            {"title": "Detected Role", "detail": latest.detected_role, "tone": "success"},
            {"title": "Career Level", "detail": latest.career_level, "tone": "accent"}
        ],
        "jobMatches": matches,
        "recentActivity": [
            {"id": 1, "actor": "Resume", "action": "uploaded successfully", "time": "Just now", "tone": "success"}
        ],
        "recentUploads": [
            {"id": latest.id, "name": latest.detected_role + " Resume", "size": f"{len(skills)} Skills", "when": "Latest", "score": latest.resume_score}
        ],
        "interviews": []
    }
