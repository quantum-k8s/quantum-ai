from fastapi import APIRouter, Depends, HTTPException
from common.dependencies import get_user_profile_service
from services.user_profile.service import UserProfileService
from schemas.user_profile import UserProfileUpdate

router = APIRouter(tags=["Profile"])

@router.get("/profile/{id}")
def get_profile(id: int, profile_service: UserProfileService = Depends(get_user_profile_service)):
    return profile_service.get_profile(id)

@router.put("/profile/{id}")
def update_profile(id: int, data: UserProfileUpdate, profile_service: UserProfileService = Depends(get_user_profile_service)):
    return profile_service.update_profile(id, data)
