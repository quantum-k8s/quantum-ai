from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from common.dependencies import get_auth_service
from services.auth.service import AuthService
from schemas.auth import UserCreate, UserLogin, Token, UserResponse

router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
def signup(user_in: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.signup(user_in)

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login(user_in)

@router.get("/users", response_model=list[UserResponse])
def get_all_users(auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.get_all_users()
