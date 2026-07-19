from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Certification
from pydantic import BaseModel

router = APIRouter(tags=["Certification"])

class CertificationCreate(BaseModel):
    user_id: int
    certificate_name: str
    organization: str
    year: str

@router.get("/certification/{user_id}")
def get_certifications(user_id: int, db: Session = Depends(get_db)):
    return db.query(Certification).filter(Certification.user_id == user_id).all()

@router.post("/certification")
def add_certification(cert: CertificationCreate, db: Session = Depends(get_db)):
    item = Certification(
        user_id=cert.user_id,
        certificate_name=cert.certificate_name,
        organization=cert.organization,
        year=cert.year,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/certification/{id}")
def delete_certification(id: int, db: Session = Depends(get_db)):
    item = db.query(Certification).filter(Certification.id == id).first()
    if item:
        db.delete(item)
        db.commit()
    return {"success": True}
