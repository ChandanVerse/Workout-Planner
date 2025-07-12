from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timedelta
from app.database import get_session
from app.models import User, WorkoutLog, Exercise
from app.schemas import WorkoutLogCreate, WorkoutLogResponse, ProgressStats, ProgressHistory
from app.auth.utils import get_current_user
from collections import defaultdict

router = APIRouter(prefix="/api/progress", tags=["progress"])

@router.post("/log", response_model=WorkoutLogResponse)
async def log_workout(
    log_data: WorkoutLogCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Log a completed workout"""
    try:
        # Verify exercise exists
        exercise = session.get(Exercise, log_data.exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        
        # Create workout log
        workout_log = WorkoutLog(
            user_id=current_user.id,
            exercise_id=log_data.exercise_id,
            sets_completed=log_data.sets_completed,
            reps_completed=log_data.reps_completed,
            duration_completed=log_data.duration_completed,
            weight_used=log_data.weight_used,
            notes=log_data.notes
        )
        
        session.add(workout_log)
        session.commit()
        session.refresh(workout_log)
        
        return WorkoutLogResponse(
            id=workout_log.id,
            exercise_id=workout_log.exercise_id,
            exercise_name=exercise.name,
            sets_completed=workout_log.sets_completed,
            reps_completed=workout_log.reps_completed,
            duration_completed=workout_log.duration_completed,
            weight_used=workout_log.weight_used,
            notes=workout_log.notes,
            completed_at=workout_log.completed_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging workout: {str(e)}")

@router.get("/history", response_model=List[ProgressHistory])
async def get_progress_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get workout history for the past N days"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query workout logs
        statement = select(WorkoutLog, Exercise).join(Exercise).where(
            WorkoutLog.user_id == current_user.id,
            WorkoutLog.completed_at >= start_date,
            WorkoutLog.completed_at <= end_date
        )
        
        results = session.exec(statement).all()
        
        # Group by date
        daily_stats = defaultdict(lambda: {
            'workouts_count': 0,
            'total_duration': 0,
            'muscle_groups': set()
        })
        
        for log, exercise in results:
            date_str = log.completed_at.strftime('%Y-%m-%d')
            daily_stats[date_str]['workouts_count'] += 1
            if log.duration_completed:
                daily_stats[date_str]['total_duration'] += log.duration_completed
            daily_stats[date_str]['muscle_groups'].add(exercise.target_muscle)
        
        # Convert to response format
        history = []
        for date_str, stats in daily_stats.items():
            history.append(ProgressHistory(
                date=date_str,
                workouts_count=stats['workouts_count'],
                total_duration=stats['total_duration'],
                muscle_groups=list(stats['muscle_groups'])
            ))
        
        # Sort by date
        history.sort(key=lambda x: x.date)
        
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress history: {str(e)}")

@router.get("/stats", response_model=ProgressStats)
async def get_progress_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get overall progress statistics"""
    try:
        # Query all workout logs for user
        statement = select(WorkoutLog, Exercise).join(Exercise).where(
            WorkoutLog.user_id == current_user.id
        )
        
        results = session.exec(statement).all()
        
        total_workouts = len(results)
        total_time_minutes = 0
        muscle_groups = set()
        
        for log, exercise in results:
            if log.duration_completed:
                total_time_minutes += log.duration_completed // 60
            muscle_groups.add(exercise.target_muscle)
        
        # Calculate average workouts per week
        if results:
            first_workout = min(log.completed_at for log, _ in results)
            weeks_since_first = (datetime.utcnow() - first_workout).days / 7
            avg_workouts_per_week = total_workouts / max(weeks_since_first, 1)
        else:
            avg_workouts_per_week = 0
        
        return ProgressStats(
            total_workouts=total_workouts,
            total_time_minutes=total_time_minutes,
            muscle_groups_trained=list(muscle_groups),
            avg_workouts_per_week=round(avg_workouts_per_week, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress stats: {str(e)}")