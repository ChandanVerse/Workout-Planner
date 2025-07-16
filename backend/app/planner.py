from typing import List, Dict, Any
from app.models import WorkoutType, UserLevel, Exercise, WorkoutPlan, WorkoutPlanExercise
from app.embeddings import embedding_service
import json
import random

# CORRECTED: Explicitly type the list of dictionaries to allow for mixed value types (str and List[float])
SAMPLE_EXERCISES: List[Dict[str, Any]] = [
    {
        "name": "Push-ups",
        "description": "Classic bodyweight exercise targeting chest, shoulders, and triceps",
        "target_muscle": "chest",
        "equipment": "bodyweight",
        "difficulty": "beginner",
        "instructions": "Start in plank position, lower body until chest nearly touches ground, push back up"
    },
    {
        "name": "Squats",
        "description": "Fundamental lower body exercise targeting quads, glutes, and hamstrings",
        "target_muscle": "legs",
        "equipment": "bodyweight",
        "difficulty": "beginner",
        "instructions": "Stand with feet shoulder-width apart, lower hips back and down, return to standing"
    },
    {
        "name": "Dumbbell Bench Press",
        "description": "Chest exercise using dumbbells for upper body strength",
        "target_muscle": "chest",
        "equipment": "dumbbells",
        "difficulty": "intermediate",
        "instructions": "Lie on bench, press dumbbells up from chest level, lower with control"
    },
    {
        "name": "Deadlifts",
        "description": "Compound movement targeting posterior chain muscles",
        "target_muscle": "back",
        "equipment": "barbell",
        "difficulty": "intermediate",
        "instructions": "Stand with feet hip-width apart, hinge at hips, lower bar to ground, return to standing"
    },
    {
        "name": "Plank",
        "description": "Core stabilization exercise",
        "target_muscle": "core",
        "equipment": "bodyweight",
        "difficulty": "beginner",
        "instructions": "Hold rigid position on forearms and toes, maintain straight line from head to heels"
    },
    {
        "name": "Dumbbell Rows",
        "description": "Back exercise using dumbbells",
        "target_muscle": "back",
        "equipment": "dumbbells",
        "difficulty": "beginner",
        "instructions": "Bend over, pull dumbbells to sides of torso, lower with control"
    },
    {
        "name": "Lunges",
        "description": "Unilateral leg exercise",
        "target_muscle": "legs",
        "equipment": "bodyweight",
        "difficulty": "beginner",
        "instructions": "Step forward into lunge position, lower back knee toward ground, return to standing"
    },
    {
        "name": "Burpees",
        "description": "Full-body cardio exercise",
        "target_muscle": "full body",
        "equipment": "bodyweight",
        "difficulty": "intermediate",
        "instructions": "Squat down, jump back to plank, do push-up, jump feet to hands, jump up"
    },
    {
        "name": "Dumbbell Shoulder Press",
        "description": "Overhead pressing movement for shoulders",
        "target_muscle": "shoulders",
        "equipment": "dumbbells",
        "difficulty": "beginner",
        "instructions": "Press dumbbells overhead from shoulder level, lower with control"
    },
    {
        "name": "Mountain Climbers",
        "description": "Dynamic cardio and core exercise",
        "target_muscle": "core",
        "equipment": "bodyweight",
        "difficulty": "intermediate",
        "instructions": "Start in plank, alternate bringing knees to chest quickly"
    }
]

class WorkoutPlannerService:
    def __init__(self):
        # CORRECTED: Ensure the instance variable also has the correct, explicit type hint
        self.exercises: List[Dict[str, Any]] = self._prepare_exercises()
    
    # CORRECTED: The return type must match the explicit type hint used elsewhere
    def _prepare_exercises(self) -> List[Dict[str, Any]]:
        """Prepare exercises with embeddings"""
        exercises_with_embeddings: List[Dict[str, Any]] = []
        for exercise in SAMPLE_EXERCISES:
            embedding = embedding_service.create_exercise_embedding(exercise)
            exercise_with_embedding = exercise.copy()
            # This assignment is now valid because exercise_with_embedding is known to be Dict[str, Any]
            exercise_with_embedding['embedding'] = embedding
            exercises_with_embeddings.append(exercise_with_embedding)
        return exercises_with_embeddings
    
    def create_workout_plan(self, preferences: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a workout plan based on user preferences"""
        query = embedding_service.create_query_from_preferences(preferences)
        query_embedding = embedding_service.create_embedding(query)
        
        available_equipment = [eq.lower() for eq in preferences.get('available_equipment', [])]
        if 'bodyweight' not in available_equipment:
            available_equipment.append('bodyweight')
        
        filtered_exercises = [
            ex for ex in self.exercises 
            if ex.get('equipment', '').lower() in available_equipment
        ]
        
        # CORRECTED: Ensure the type hint for exercise_embeddings is also explicit
        exercise_embeddings: List[Dict[str, Any]] = [ex for ex in filtered_exercises if 'embedding' in ex]

        similar_exercises = embedding_service.find_similar_exercises(
            query_embedding, exercise_embeddings, top_k=20
        )
        
        if not similar_exercises:
            similar_exercises = filtered_exercises[:10]
        
        plan = self._generate_plan_structure(preferences, similar_exercises)
        
        return plan
    
    # CORRECTED: The 'exercises' parameter needs the correct, explicit type hint
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
        # Use max() to avoid division by zero if days_per_week is 0
        exercises_per_day = max(5, len(exercises) // max(1, days_per_week))
        
        for day in range(1, days_per_week + 1):
            day_exercises = []
            
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
                    'id': idx + 1,
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