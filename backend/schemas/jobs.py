from pydantic import BaseModel
from typing import List, Optional

class JobRecommendRequest(BaseModel):
    skills: List[str]

class JobMatchRequest(BaseModel):
    resume_skills: List[str]
    job_skills: List[str]

class JobDescriptionMatchRequest(BaseModel):
    resume_text: str
    job_text: str
