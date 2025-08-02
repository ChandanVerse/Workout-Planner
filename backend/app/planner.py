from typing import List, Dict, Any
from app.models import WorkoutType, UserLevel, Exercise
from app.embeddings import embedding_service
from sqlmodel import Session, select
from app.database import get_session
import json
import random

class WorkoutPlannerService:
    def __init__(self):
        pass
    
    def _get_exercises_from_db(self, session: Session) -> List[Dict[str, Any]]:
        """Get exercises from database and convert to dict format"""
        statement = select(Exercise)
        exercises = session.exec(statement).all()
        
        exercises_list = []
        for exercise in exercises:
            exercise_dict = {
                "id": exercise.id,
                "name": exercise.name,
                "description": exercise.description,
                "target_muscle": exercise.target_muscle,
                "equipment": exercise.equipment,
                "difficulty": exercise.difficulty,
                "instructions": exercise.instructions
            }
            
            # Parse embedding if it exists
            if exercise.embedding:
                try:
                    embedding = json.loads(exercise.embedding)
                    exercise_dict['embedding'] = embedding
                except json.JSONDecodeError:
                    exercise_dict['embedding'] = []
            else:
                exercise_dict['embedding'] = []
            
            exercises_list.append(exercise_dict)
        
        return exercises_list
    
    def create_workout_plan(self, preferences: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a workout plan based on user preferences"""
        # Get a database session
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Get exercises from database
            exercises = self._get_exercises_from_db(session)
            
            if not exercises:
                return {"error": "No exercises found in database. Please seed the database first."}
            
            query = embedding_service.create_query_from_preferences(preferences)
            query_embedding = embedding_service.create_embedding(query)
            
            available_equipment = [eq.lower() for eq in preferences.get('available_equipment', [])]
            if 'bodyweight' not in available_equipment:
                available_equipment.append('bodyweight')
            
            # Filter exercises by available equipment
            filtered_exercises = [
                ex for ex in exercises 
                if ex.get('equipment', '').lower() in available_equipment
            ]
            
            if not filtered_exercises:
                filtered_exercises = exercises  # Fallback to all exercises
            
            # Find similar exercises if embeddings are available
            exercise_embeddings = [ex for ex in filtered_exercises if ex.get('embedding')]
            
            if query_embedding and exercise_embeddings:
                similar_exercises = embedding_service.find_similar_exercises(
                    query_embedding, exercise_embeddings, top_k=20
                )
            else:
                similar_exercises = filtered_exercises[:20]
            
            if not similar_exercises:
                similar_exercises = filtered_exercises[:10]
            
            plan = self._generate_plan_structure(preferences, similar_exercises)
            
            return plan
            
        finally:
            session.close()
    
    def _generate_plan_structure(self, preferences: Dict[str, Any], exercises: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate the actual workout plan structure"""
        days_per_week = preferences.get('days_per_week', 3)
        session_duration = preferences.get('session_duration', 60)
        user_level = preferences.get('user_level', 'beginner')
        workout_type = preferences.get('workout_type', 'strength')
        
        if user_level == 'beginner':
            sets_range = (2, 3)
            reps_range = (8, 12)
        elif user_level == 'intermediate':
            sets_range = (3, 4)
            reps_range = (10, 15)
        else:
            sets_range = (4, 5)
            reps_range = (12, 20)
        
        days = []
        exercises_per_day = max(4, len(exercises) // max(1, days_per_week))
        
        for day in range(1, days_per_week + 1):
            day_exercises = []
            
            # Get exercises for this day
            start_idx = (day - 1) * exercises_per_day
            end_idx = start_idx + exercises_per_day
            day_exercise_list = exercises[start_idx:end_idx]
            
            if not day_exercise_list:
                day_exercise_list = exercises[:exercises_per_day]
            
            for idx, exercise in enumerate(day_exercise_list):
                sets = random.randint(*sets_range)
                reps = random.randint(*reps_range)
                
                reps_val = reps
                duration = None
                
                if workout_type == 'cardio' or 'cardio' in exercise.get('description', '').lower():
                    duration = random.randint(30, 60)
                    reps_val = None
                
                day_exercises.append({
                    'id': exercise['id'],  # Use actual database ID
                    'name': exercise['name'],
                    'description': exercise['description'],
                    'target_muscle': exercise['target_muscle'],
                    'equipment': exercise['equipment'],
                    'sets': sets,
                    'reps': reps_val,
                    'duration': duration,
                    'rest_time': 60 if workout_type == 'strength' else 30,
                    'order': idx + 1
                })
            
            days.append({
                'day': day,
                'exercises': day_exercises
            })
        
        return {
            'id': 1,
            'name': f"{preferences.get('workout_type', 'Custom').title()} Workout Plan",
            'description': f"A {days_per_week}-day {preferences.get('workout_type', 'custom')} workout plan",
            'days_per_week': days_per_week,
            'session_duration': session_duration,
            'workout_type': preferences.get('workout_type', 'strength'),
            'user_level': user_level,
            'days': days
        }

# Global instance
planner_service = WorkoutPlannerService()