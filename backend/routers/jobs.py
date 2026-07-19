from fastapi import APIRouter, Depends
from typing import List
from services.job_recommender import recommend_jobs
from services.job_match import calculate_match
from services.explainable_ai import explain_match
from services.job_market import market_trends
from services.ai_resume_analyzer import analyze_resume as ai_analyze_resume
from utils.skills_data import skills
from schemas.jobs import JobRecommendRequest, JobMatchRequest, JobDescriptionMatchRequest

router = APIRouter(tags=["Jobs"])

@router.post("/recommend-jobs")
def recommend(req: JobRecommendRequest):
    return recommend_jobs(req.skills)

@router.get("/skills")
def get_skills():
    return skills

@router.post("/job-match")
def job_match(req: JobMatchRequest):
    return calculate_match(req.resume_skills, req.job_skills)

@router.post("/explainable-ai")
def explainable_ai(req: JobMatchRequest):
    return explain_match(req.resume_skills, req.job_skills)

@router.get("/market-trends")
def market_analysis():
    return market_trends()

@router.post("/job-description-match")
def job_description_match(req: JobDescriptionMatchRequest):
    resume_result = ai_analyze_resume(req.resume_text)
    resume_skills = resume_result.get("skills_found", [])

    job_result = ai_analyze_resume(req.job_text)
    detected_job_skills = job_result.get("skills_found", [])

    important_keywords = ["python", "sql", "aws", "azure", "gcp", "docker", "kubernetes", "react", "fastapi"]
    job_text_lower = req.job_text.lower()
    for skill in important_keywords:
        if skill in job_text_lower and skill not in detected_job_skills:
            detected_job_skills.append(skill)

    matched_skills = list(set(resume_skills) & set(detected_job_skills))
    missing_skills = list(set(detected_job_skills) - set(resume_skills))
    score = 0
    if detected_job_skills:
        score = round((len(matched_skills) / len(detected_job_skills)) * 100, 2)

    return {
        "match_score": score,
        "resume_skills": resume_skills,
        "job_skills": detected_job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }
