# backend/seed_database.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.database import engine
from app.models import Exercise
from app.embeddings import embedding_service
import json

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

def seed_exercises():
    """Seed the database with sample exercises"""
    with Session(engine) as session:
        # Check if exercises already exist
        statement = select(Exercise)
        existing_exercises = session.exec(statement).all()
        
        if existing_exercises:
            print(f"Database already has {len(existing_exercises)} exercises. Skipping seed.")
            return
        
        print("Seeding database with sample exercises...")
        
        for exercise_data in SAMPLE_EXERCISES:
            # Create embedding for the exercise
            embedding = embedding_service.create_exercise_embedding(exercise_data)
            embedding_json = json.dumps(embedding) if embedding else None
            
            # Create Exercise object
            exercise = Exercise(
                name=exercise_data["name"],
                description=exercise_data["description"],
                target_muscle=exercise_data["target_muscle"],
                equipment=exercise_data["equipment"],
                difficulty=exercise_data["difficulty"],
                instructions=exercise_data["instructions"],
                embedding=embedding_json
            )
            
            session.add(exercise)
            print(f"Added exercise: {exercise.name}")
        
        session.commit()
        print(f"Successfully seeded {len(SAMPLE_EXERCISES)} exercises!")

if __name__ == "__main__":
    seed_exercises()