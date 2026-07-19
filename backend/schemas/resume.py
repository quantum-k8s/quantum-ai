from pydantic import BaseModel
from typing import List, Optional, Any

class ResumeScoreRequest(BaseModel):
    resume_text: str

class ResumeRewriteRequest(BaseModel):
    resume_text: str
    target_role: str

class CompareResumesRequest(BaseModel):
    resume1: str
    resume2: str

class AnalyzeRequest(BaseModel):
    text: str

class RoadmapRequest(BaseModel):
    role: str
