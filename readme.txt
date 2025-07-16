🏋️ Workout Planner Web App

A full-stack web application for generating personalized workout plans using AI-powered exercise recommendations and tracking progress with interactive charts.

---

Features
- AI-Powered Workout Generation: Creates personalized workout plans based on goals, fitness level, and preferences.
- Exercise Recommendations: Uses SentenceTransformer embeddings to find similar exercises.
- Progress Tracking: Interactive charts showing workout history, volume, and exercise breakdown.
- User Authentication: Secure JWT-based authentication system.
- Responsive Design: Modern dark theme with a mobile-friendly interface.
- Exercise Logging: Track sets, reps, and weights for each exercise.

---

Tech Stack

Backend:
- FastAPI: Modern Python web framework.
- PostgreSQL: Primary database.
- SQLModel: SQL databases in Python with type hints.
- SentenceTransformers: AI model for exercise embeddings.
- JWT: JSON Web Tokens for authentication.
- bcrypt: Password hashing.

Frontend:
- React: Frontend framework.
- Axios: HTTP client.
- React Router: Navigation.
- Recharts: Data visualization.
- CSS3: Custom styling with CSS variables.

---

Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- Git

---

Installation & Setup

1. Clone the Repository
    - `git clone https://github.com/yourusername/workout-planner.git`
    - `cd workout-planner`

2. Backend Setup
    - Create Python Virtual Environment
        - `cd backend`
        - `python -m venv venv`
        - Windows: `venv\Scripts\activate`
        - macOS/Linux: `source venv/bin/activate`
    - Install Dependencies
        - `pip install -r requirements.txt`
    - Database Setup
        - Install PostgreSQL (if not already installed):
            - Windows: Download from postgresql.org
            - macOS: `brew install postgresql`
            - Linux: `sudo apt-get install postgresql postgresql-contrib`
        - Create Database:
            - Connect to PostgreSQL as superuser: `psql -U postgres`
            - Create database and user:
                - `CREATE DATABASE workout_planner;`
                - `CREATE USER workout_user WITH PASSWORD 'your_password';`
                - `GRANT ALL PRIVILEGES ON DATABASE workout_planner TO workout_user;`
                - `\q`
    - Configure Environment Variables
        - Create a `.env` file in the backend directory:
            - `cp .env.example .env`
            - Edit `.env` with your settings:
                - `DATABASE_URL=postgresql://workout_user:your_password@localhost/workout_planner`
                - `SECRET_KEY=your-secret-key-here`
                - `ALGORITHM=HS256`
                - `ACCESS_TOKEN_EXPIRE_MINUTES=30`
    - Initialize Database
        - `python -c "from database import engine; from models import SQLModel; SQLModel.metadata.create_all(bind=engine); print('Database tables created successfully!')"`
    - Start Backend Server
        - `uvicorn main:app --reload --port 8000`
        - The backend will be available at http://localhost:8000

3. Frontend Setup
    - Install Dependencies
        - `cd ../frontend`
        - `npm install`
    - Configure API Endpoint
        - Create `.env` file in frontend directory:
            - `echo "REACT_APP_API_URL=http://localhost:8000" > .env`
    - Start Frontend Server
        - `npm start`
        - The frontend will be available at http://localhost:3000

---

Docker Setup (Optional)
- Backend Docker
    - `cd backend`
    - Build Docker image: `docker build -t workout-planner-backend .`
    - Run with Docker Compose: `docker-compose up -d`
- Frontend Docker
    - `cd frontend`
    - Build Docker image: `docker build -t workout-planner-frontend .`
    - Run container: `docker run -p 3000:3000 workout-planner-frontend`
- Full Stack Docker Compose
    - Create a `docker-compose.yml` file in the root directory.
    - Example:
        - version: '3.8'
        - services:
            - postgres:
                - image: postgres:13
                - environment:
                    - POSTGRES_DB: workout_planner
                    - POSTGRES_USER: workout_user
                    - POSTGRES_PASSWORD: your_password
                - ports: "5432:5432"
                - volumes: postgres_data:/var/lib/postgresql/data
            - backend:
                - build: ./backend
                - ports: "8000:8000"
                - depends_on: postgres
                - environment:
                    - DATABASE_URL: postgresql://workout_user:your_password@postgres/workout_planner
                    - SECRET_KEY: your-secret-key-here
                - volumes: ./backend:/app
            - frontend:
                - build: ./frontend
                - ports: "3000:3000"
                - depends_on: backend
                - environment:
                    - REACT_APP_API_URL: http://localhost:8000
        - volumes:
            - postgres_data:

---

Database Schema
- Users Table
    - id: Primary key
    - username: Unique username
    - email: User email
    - hashed_password: Bcrypt hashed password
    - created_at: Account creation timestamp
- Exercises Table
    - id: Primary key
    - name: Exercise name
    - description: Exercise description
    - muscle_group: Target muscle group
    - equipment: Required equipment
    - difficulty: Difficulty level
    - embedding: SentenceTransformer embedding vector
- Plans Table
    - id: Primary key
    - name: Plan name
    - description: Plan description
    - user_id: Foreign key to users
    - goal: Fitness goal
    - duration: Plan duration in weeks
    - exercises: JSON field containing exercise schedule
    - created_at: Creation timestamp
- Workouts Table
    - id: Primary key
    - user_id: Foreign key to users
    - exercise_id: Foreign key to exercises
    - sets: Number of sets
    - reps: Number of reps
    - weight: Weight used (optional)
    - date: Workout date
    - created_at: Log timestamp

---

Authentication
- Registration: Users create accounts with a username/email/password.
- Login: Returns a JWT token on successful authentication.
- Protected Routes: API endpoints require a valid JWT token.
- Token Refresh: Tokens expire after 30 minutes (configurable).

---

AI Exercise Recommendations
- Exercise Embeddings: Each exercise is converted to a vector representation.
- Similarity Search: Finds exercises similar to user preferences.
- Personalized Plans: Generates plans based on goals, fitness level, and equipment.
- Progressive Difficulty: Adjusts recommendations based on user progress.

---

API Endpoints
- Authentication
    - POST /auth/register - User registration
    - POST /auth/login - User login
    - GET /auth/me - Get current user info
- Exercises
    - GET /exercises/ - List all exercises
    - POST /exercises/ - Create a new exercise
    - GET /exercises/{id} - Get exercise details
    - GET /exercises/search - Search exercises
- Plans
    - GET /plans/ - List user's plans
    - POST /plans/ - Create a new plan
    - GET /plans/{id} - Get plan details
    - PUT /plans/{id} - Update a plan
    - DELETE /plans/{id} - Delete a plan
- Workouts
    - GET /workouts/ - List user's workouts
    - POST /workouts/ - Log a new workout
    - GET /workouts/stats - Get workout statistics

---

Testing
- Backend Tests
    - `cd backend`
    - `pytest tests/ -v`
- Frontend Tests
    - `cd frontend`
    - `npm test`

---

Deployment
- Backend Deployment (Heroku)
    - Create Heroku App: `heroku create workout-planner-backend`
    - Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
    - Set Environment Variables: `heroku config:set SECRET_KEY=your-secret-key`
    - Deploy: `git push heroku main`
- Frontend Deployment (Netlify)
    - Build for Production:
        - `cd frontend`
        - `npm run build`
    - Deploy to Netlify:
        - Install Netlify CLI: `npm install -g netlify-cli`
        - Deploy: `netlify deploy --prod --dir=build`

---

Environment Variables
- Backend (.env)
    - DATABASE_URL=postgresql://user:password@localhost/workout_planner
    - SECRET_KEY=your-secret-key-here
    - ALGORITHM=HS256
    - ACCESS_TOKEN_EXPIRE_MINUTES=30
    - CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
- Frontend (.env)
    - REACT_APP_API_URL=http://localhost:8000
    - REACT_APP_VERSION=1.0.0

---

Troubleshooting
- Database Connection Error:
    - Check if PostgreSQL is running.
    - Verify that DATABASE_URL is correct.
    - Ensure the database and user exist.
- CORS Issues:
    - Add the frontend URL to CORS_ORIGINS.
    - Check API_URL in the frontend .env file.
- JWT Token Issues:
    - Verify that SECRET_KEY is set.
    - Check the token expiration time.
    - Clear browser localStorage.
- Model Loading Error:
    - Ensure the SentenceTransformer model downloads correctly.
    - Check the internet connection on the first run.
    - Verify there is sufficient disk space.
- Performance Optimization:
    - Database Indexing:
        - CREATE INDEX idx_workouts_user_date ON workouts(user_id, date);
        - CREATE INDEX idx_plans_user ON plans(user_id);
        - CREATE INDEX idx_exercises_muscle_group ON exercises(muscle_group);
    - Frontend Optimization:
        - Enable React.StrictMode.
        - Use React.memo for expensive components.
        - Implement lazy loading for charts.
    - Backend Optimization:
        - Use connection pooling.
        - Implement Redis caching.
        - Add API rate limiting.

---

Contributing
- Fork the repository.
- Create a feature branch: `git checkout -b feature-name`
- Commit changes: `git commit -am 'Add feature'`
- Push to the branch: `git push origin feature-name`
- Create a Pull Request.
