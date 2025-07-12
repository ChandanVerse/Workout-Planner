from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import WorkoutType, UserLevel

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Workout Plan schemas
class WorkoutPlanCreate(BaseModel):
    focus_areas: List[str]
    available_equipment: List[str]
    workout_type: WorkoutType
    user_level: UserLevel
    days_per_week: int
    session_duration: int

class ExerciseInPlan(BaseModel):
    id: int
    name: str
    description: str
    target_muscle: str
    equipment: str
    sets: int
    reps: int
    duration: Optional[int] = None
    rest_time: Optional[int] = None
    order: int

class DayPlan(BaseModel):
    day: int
    exercises: List[ExerciseInPlan]

class WorkoutPlanResponse(BaseModel):
    id: int
    name: str
    description: str
    days_per_week: int
    session_duration: int
    workout_type: WorkoutType
    user_level: UserLevel
    days: List[DayPlan]

# Workout Log schemas
class WorkoutLogCreate(BaseModel):
    exercise_id: int
    sets_completed: int
    reps_completed: int
    duration_completed: Optional[int] = None
    weight_used: Optional[float] = None
    notes: Optional[str] = None

class WorkoutLogResponse(BaseModel):
    id: int
    exercise_id: int
    exercise_name: str
    sets_completed: int
    reps_completed: int
    duration_completed: Optional[int] = None
    weight_used: Optional[float] = None
    notes: Optional[str] = None
    completed_at: datetime

# Progress schemas
class ProgressStats(BaseModel):
    total_workouts: int
    total_time_minutes: int
    muscle_groups_trained: List[str]
    avg_workouts_per_week: float

class ProgressHistory(BaseModel):
    date: str
    workouts_count: int
    total_duration: int
    muscle_groups: List[str]