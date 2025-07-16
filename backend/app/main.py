import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.auth.routes import router as auth_router
from app.routes.user import router as user_router
from app.routes.workout import router as workout_router
from app.routes.progress import router as progress_router

# Load environment variables from a .env file
load_dotenv()

app = FastAPI(title="Workout Planner API", version="1.0.0")

# Get the frontend URL from environment variables, with a default for local development
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    # Use the frontend_url variable for allowed origins
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the API routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(workout_router)
app.include_router(progress_router)

@app.on_event("startup")
def on_startup():
    """Create database and tables on startup"""
    create_db_and_tables()

@app.get("/")
def read_root():
    """Root endpoint for the API"""
    return {"message": "Workout Planner API is running!"}