from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

class WorkoutType(str, Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    MIXED = "mixed"

class UserLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    workout_logs: List["WorkoutLog"] = Relationship(back_populates="user")

class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    target_muscle: str
    equipment: str
    difficulty: str
    instructions: str
    embedding: Optional[str] = Field(default=None)  # JSON string of vector
    
    # Relationships
    workout_plan_exercises: List["WorkoutPlanExercise"] = Relationship(back_populates="exercise")
    workout_logs: List["WorkoutLog"] = Relationship(back_populates="exercise")

class WorkoutPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    description: str
    days_per_week: int
    session_duration: int  # in minutes
    workout_type: WorkoutType
    user_level: UserLevel
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    exercises: List["WorkoutPlanExercise"] = Relationship(back_populates="workout_plan")

class WorkoutPlanExercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workout_plan_id: int = Field(foreign_key="workoutplan.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    day: int  # 1-7
    sets: int
    reps: int
    duration: Optional[int] = Field(default=None)  # in seconds
    rest_time: Optional[int] = Field(default=None)  # in seconds
    order: int  # order within the day
    
    # Relationships
    workout_plan: WorkoutPlan = Relationship(back_populates="exercises")
    exercise: Exercise = Relationship(back_populates="workout_plan_exercises")

class WorkoutLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    sets_completed: int
    reps_completed: int
    duration_completed: Optional[int] = Field(default=None)  # in seconds
    weight_used: Optional[float] = Field(default=None)  # in kg
    notes: Optional[str] = Field(default=None)
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="workout_logs")
    exercise: Exercise = Relationship(back_populates="workout_logs")