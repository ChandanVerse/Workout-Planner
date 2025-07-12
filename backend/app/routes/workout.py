from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models import User
from app.schemas import WorkoutPlanCreate, WorkoutPlanResponse
from app.auth.utils import get_current_user
from app.planner import planner_service

router = APIRouter(prefix="/api/workout", tags=["workout"])

@router.post("/plan", response_model=WorkoutPlanResponse)
async def create_workout_plan(
    plan_request: WorkoutPlanCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Generate a workout plan based on user preferences"""
    try:
        # Convert request to dictionary
        preferences = {
            'focus_areas': plan_request.focus_areas,
            'available_equipment': plan_request.available_equipment,
            'workout_type': plan_request.workout_type,
            'user_level': plan_request.user_level,
            'days_per_week': plan_request.days_per_week,
            'session_duration': plan_request.session_duration
        }
        
        # Generate plan using planner service
        plan = planner_service.create_workout_plan(preferences, current_user.id)
        
        return WorkoutPlanResponse(**plan)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating workout plan: {str(e)}")