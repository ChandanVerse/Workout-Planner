from typing import List, Dict, Any
from app.models import WorkoutType, UserLevel, Exercise, WorkoutPlan, WorkoutPlanExercise
from app.embeddings import embedding_service
import json
import random

# Sample exercise data (in production, this would come from ExerciseDB API)
SAMPLE_EXERCISES = [
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
        self.exercises = self._prepare_exercises()
    
    def _prepare_exercises(self) -> List[Dict]:
        """Prepare exercises with embeddings"""
        exercises_with_embeddings = []
        for exercise in SAMPLE_EXERCISES:
            embedding = embedding_service.create_exercise_embedding(exercise)
            exercise_with_embedding = exercise.copy()
            exercise_with_embedding['embedding'] = embedding
            exercises_with_embeddings.append(exercise_with_embedding)
        return exercises_with_embeddings
    
    def create_workout_plan(self, preferences: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a workout plan based on user preferences"""
        # Create query from preferences
        query = embedding_service.create_query_from_preferences(preferences)
        query_embedding = embedding_service.create_embedding(query)
        
        # Filter exercises by available equipment
        available_equipment = [eq.lower() for eq in preferences.get('available_equipment', [])]
        if 'bodyweight' not in available_equipment:
            available_equipment.append('bodyweight')  # Always include bodyweight
        
        filtered_exercises = [
            ex for ex in self.exercises 
            if ex['equipment'].lower() in available_equipment
        ]
        
        # Find similar exercises
        similar_exercises = embedding_service.find_similar_exercises(
            query_embedding, filtered_exercises, top_k=20
        )
        
        if not similar_exercises:
            similar_exercises = filtered_exercises[:10]  # Fallback
        
        # Generate plan structure
        plan = self._generate_plan_structure(preferences, similar_exercises)
        
        return plan
    
    def _generate_plan_structure(self, preferences: Dict[str, Any], exercises: List[Dict]) -> Dict[str, Any]:
        """Generate the actual workout plan structure"""
        days_per_week = preferences.get('days_per_week', 3)
        session_duration = preferences.get('session_duration', 60)
        user_level = preferences.get('user_level', 'beginner')
        workout_type = preferences.get('workout_type', 'strength')
        
        # Determine sets and reps based on user level and workout type
        if user_level == 'beginner':
            sets_range = (2, 3)
            reps_range = (8, 12)
        elif user_level == 'intermediate':
            sets_range = (3, 4)
            reps_range = (10, 15)
        else:  # advanced
            sets_range = (4, 5)
            reps_range = (12, 20)
        
        # Create daily plans
        days = []
        exercises_per_day = max(5, len(exercises) // days_per_week)
        
        for day in range(1, days_per_week + 1):
            day_exercises = []
            
            # Select exercises for this day
            start_idx = (day - 1) * exercises_per_day
            end_idx = start_idx + exercises_per_day
            day_exercise_list = exercises[start_idx:end_idx]
            
            if not day_exercise_list:
                day_exercise_list = exercises[:exercises_per_day]
            
            for idx, exercise in enumerate(day_exercise_list):
                sets = random.randint(*sets_range)
                reps = random.randint(*reps_range)
                
                # For cardio exercises, use duration instead of reps
                if workout_type == 'cardio' or 'cardio' in exercise.get('description', '').lower():
                    duration = random.randint(30, 60)  # seconds
                    reps = None
                else:
                    duration = None
                
                day_exercises.append({
                    'id': idx + 1,  # Temporary ID
                    'name': exercise['name'],
                    'description': exercise['description'],
                    'target_muscle': exercise['target_muscle'],
                    'equipment': exercise['equipment'],
                    'sets': sets,
                    'reps': reps,
                    'duration': duration,
                    'rest_time': 60 if workout_type == 'strength' else 30,
                    'order': idx + 1
                })
            
            days.append({
                'day': day,
                'exercises': day_exercises
            })
        
        return {
            'id': 1,  # Temporary ID
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