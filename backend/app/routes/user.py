from fastapi import APIRouter, Depends
from app.models import User
from app.schemas import UserResponse
from app.auth.utils import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )