from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import tempfile
import os
from database import get_db
from models import Resume, Notification, User
from core.security import get_current_user
from services.ai_resume_analyzer import analyze_resume as ai_analyze_resume
from services.ats_checker import calculate_ats_score
from services.resume_rewriter import rewrite_resume
from services.career_roadmap import generate_roadmap
from services.skill_gap import find_skill_gap
from services.career_predictor import predict_career
from services.resume_suggestions import generate_ai_suggestions
from services.learning_roadmap import generate_learning_roadmap
from services.multi_resume import compare_candidates
from services.trust_score import calculate_trust_score
from schemas.resume import ResumeScoreRequest, ResumeRewriteRequest, CompareResumesRequest
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from pdfminer.high_level import extract_text
from datetime import datetime

router = APIRouter(tags=["Resume"])

@router.post("/upload-resume/")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Validate MIME type
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT are allowed.")

        # Save PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            content = await file.read()
            if len(content) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File too large. Max size is 5MB.")
            temp.write(content)
            temp_path = temp.name

        # Extract text
        try:
            text = extract_text(temp_path)
        except Exception as e:
            text = str(content, 'utf-8', errors='ignore') # Fallback for non-pdf
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        # Analyze
        ai_result = ai_analyze_resume(text)
        ats = calculate_ats_score(text)
        
        role = ai_result.get("detected_role", "software engineer").lower().strip()
        role_info = generate_roadmap(role)
        expected_skills = role_info.get("skills", [])

        gap = find_skill_gap(ai_result.get("skills_found", []), expected_skills)
        
        career_prediction = predict_career(ai_result.get("skills_found", []))
        ai_suggestions = generate_ai_suggestions(text, ai_result.get("skills_found", []))
        learning_roadmap = generate_learning_roadmap(ai_result.get("skills_found", []))

        # Save to DB
        resume = Resume(
            user_id=current_user.id,
            resume_score=float(ai_result.get("resume_score", 0)),
            ats_score=float(ats.get("ats_score", 0)),
            career_level=ai_result.get("career_level", "Beginner"),
            detected_role=role.title(),
            skills=",".join(ai_result.get("skills_found", [])),
            roadmap="\n".join(expected_skills),
            ai_suggestions="\n".join(ai_suggestions)
        )
        db.add(resume)
        
        # Notify
        db.add(Notification(
            user_id=current_user.id,
            title="Resume Analysis Complete",
            message=f"Analysis for {file.filename} is ready.",
            type="resume"
        ))
        
        db.commit()
        db.refresh(resume)

        return {
            "success": True,
            "resume_id": resume.id,
            "filename": file.filename,
            "analysis": ai_result,
            "ats": ats,
            "skill_gap": gap,
            "career_prediction": career_prediction,
            "learning_roadmap": learning_roadmap,
            "professional_summary": ai_result.get("professional_summary", "")
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume-score")
def get_resume_score(req: ResumeScoreRequest):
    return calculate_ats_score(req.resume_text)

@router.post("/rewrite-resume")
def rewrite(req: ResumeRewriteRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = rewrite_resume(req.resume_text, req.target_role)
    db.add(Notification(
        user_id=current_user.id,
        title="Resume Rewritten",
        message=f"Your resume was rewritten for the role of {req.target_role}.",
        type="resume"
    ))
    db.commit()
    return result

@router.get("/score-trend")
def score_trend(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.asc()).all()
    return [
        {
            "month": r.created_at.strftime("%b"),
            "ats": r.ats_score,
            "resume": r.resume_score
        } for r in resumes
    ]

@router.get("/analyze")
def analyze(text: str):
    return ai_analyze_resume(text)

@router.get("/skill-gap")
def skill_gap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    latest = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.id.desc()).first()
    if not latest:
        return {"missing_skills": []}
    
    role_info = generate_roadmap(latest.detected_role.lower())
    return find_skill_gap(latest.skills.split(",") if latest.skills else [], role_info.get("skills", []))

@router.get("/career-roadmap")
def roadmap(role: str):
    return generate_roadmap(role)

@router.get("/trust-score")
def trust_score(text: str, skills: str):
    return calculate_trust_score(skills.split(","), text)

@router.get("/compare-resumes")
def compare_all():
    return compare_candidates()

@router.post("/compare-two-resumes")
def compare_two(req: CompareResumesRequest):
    r1 = ai_analyze_resume(req.resume1)
    r2 = ai_analyze_resume(req.resume2)
    return {"resume1": r1, "resume2": r2}

@router.get("/download-report")
def download_report(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pdf_file = f"report_{current_user.id}.pdf"
    c = canvas.Canvas(pdf_file)
    c.drawString(100, 750, f"Career Report for {current_user.name}")
    c.save()
    return FileResponse(pdf_file, filename="resume_report.pdf", media_type="application/pdf")
