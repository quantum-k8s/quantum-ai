from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas.user_profile import UserProfileUpdate
from core.security import get_current_user

router = APIRouter(tags=["Profile"])

@router.get("/profile/{id}")
def get_profile(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"success": False}

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "country": user.country,
        "state": user.state,
        "city": user.city,
        "github": user.github,
        "linkedin": user.linkedin,
        "profile_image": user.profile_image
    }

@router.put("/profile/{id}")
def update_profile(id: int, data: UserProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"success": False}

    user.name = data.get("name", user.name)
    user.phone = data.get("phone", user.phone)
    user.gender = data.get("gender", user.gender)
    user.country = data.get("country", user.country)
    user.state = data.get("state", user.state)
    user.city = data.get("city", user.city)
    user.github = data.get("github", user.github)
    user.linkedin = data.get("linkedin", user.linkedin)

    db.commit()
    return {"success": True}
