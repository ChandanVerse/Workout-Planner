import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None

class WorkoutPlannerAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if st.session_state.token:
            headers["Authorization"] = f"Bearer {st.session_state.token}"
        return headers
    
    def register(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        data = {
            "email": email,
            "password": password,
            "full_name": full_name
        }
        response = requests.post(f"{self.base_url}/api/auth/register", json=data)
        return response.json()
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(f"{self.base_url}/api/auth/login", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Login failed")}
    
    def get_user_info(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/api/user/me", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch user info"}
    
    def create_workout_plan(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/api/workout/plan", json=preferences, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Failed to create workout plan")}
    
    def log_workout(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/api/progress/log", json=log_data, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Failed to log workout")}
    
    def get_progress_history(self, days: int = 7) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/api/progress/history?days={days}", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            return []
    
    def get_progress_stats(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/api/progress/stats", headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch progress stats"}

# Initialize API client
api = WorkoutPlannerAPI(API_BASE_URL)

def show_auth_page():
    st.title("🏋️‍♂️ Workout Planner")
    st.markdown("---")
    
    auth_mode = st.radio("Choose action:", ["Login", "Register"])
    
    if auth_mode == "Login":
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if email and password:
                    result = api.login(email, password)
                    if "access_token" in result:
                        st.session_state.token = result["access_token"]
                        st.session_state.user_info = api.get_user_info()
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Login failed"))
                else:
                    st.error("Please fill in all fields")
    
    else:  # Register
        st.subheader("Register")
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if full_name and email and password and confirm_password:
                    if password == confirm_password:
                        result = api.register(email, password, full_name)
                        if "id" in result:
                            st.success("Registration successful! Please login.")
                        else:
                            st.error("Registration failed")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")

def show_workout_plan_generator():
    st.title("💪 Create Your Workout Plan")
    st.markdown("---")
    
    with st.form("workout_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Focus Areas")
            focus_areas = st.multiselect(
                "Select muscle groups to focus on:",
                ["chest", "back", "shoulders", "arms", "legs", "core", "full body"],
                default=["chest", "legs", "core"]
            )
            
            st.subheader("Available Equipment")
            equipment = st.multiselect(
                "What equipment do you have?",
                ["bodyweight", "dumbbells", "barbell", "resistance_bands", "kettlebell", "machine"],
                default=["bodyweight", "dumbbells"]
            )
            
            workout_type = st.selectbox(
                "Workout Type",
                ["strength", "cardio", "flexibility", "mixed"],
                index=0
            )
        
        with col2:
            user_level = st.selectbox(
                "Your Fitness Level",
                ["beginner", "intermediate", "advanced"],
                index=0
            )
            
            days_per_week = st.slider(
                "Days per Week",
                min_value=1,
                max_value=7,
                value=3
            )
            
            session_duration = st.slider(
                "Session Duration (minutes)",
                min_value=15,
                max_value=120,
                value=60,
                step=15
            )
        
        submitted = st.form_submit_button("Generate Workout Plan", use_container_width=True)
        
        if submitted:
            if focus_areas and equipment:
                preferences = {
                    "focus_areas": focus_areas,
                    "available_equipment": equipment,
                    "workout_type": workout_type,
                    "user_level": user_level,
                    "days_per_week": days_per_week,
                    "session_duration": session_duration
                }
                
                with st.spinner("Generating your personalized workout plan..."):
                    plan = api.create_workout_plan(preferences)
                    if "error" not in plan:
                        st.session_state.current_plan = plan
                        st.success("Workout plan generated successfully!")
                        st.rerun()
                    else:
                        st.error(plan["error"])
            else:
                st.error("Please select at least one focus area and one equipment type")

def show_current_plan():
    if not st.session_state.current_plan:
        st.info("No workout plan generated yet. Go to 'Create Plan' to generate one.")
        return
    
    plan = st.session_state.current_plan
    
    st.title(f"📋 {plan['name']}")
    st.markdown("---")
    
    # Plan overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Days per Week", plan['days_per_week'])
    with col2:
        st.metric("Session Duration", f"{plan['session_duration']} min")
    with col3:
        st.metric("Workout Type", plan['workout_type'].title())
    with col4:
        st.metric("Level", plan['user_level'].title())
    
    st.markdown(f"**Description:** {plan['description']}")
    st.markdown("---")
    
    # Show daily workouts
    for day_plan in plan['days']:
        with st.expander(f"📅 Day {day_plan['day']}", expanded=True):
            st.markdown(f"**{len(day_plan['exercises'])} exercises planned**")
            
            for exercise in day_plan['exercises']:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{exercise['name']}**")
                    st.markdown(f"*{exercise['description']}*")
                    st.markdown(f"Target: {exercise['target_muscle'].title()} | Equipment: {exercise['equipment'].title()}")
                    
                    # Exercise details
                    details = []
                    if exercise.get('sets'):
                        details.append(f"Sets: {exercise['sets']}")
                    if exercise.get('reps'):
                        details.append(f"Reps: {exercise['reps']}")
                    if exercise.get('duration'):
                        details.append(f"Duration: {exercise['duration']}s")
                    if exercise.get('rest_time'):
                        details.append(f"Rest: {exercise['rest_time']}s")
                    
                    st.markdown(" | ".join(details))
                
                with col2:
                    if st.button(f"Log Workout", key=f"log_{day_plan['day']}_{exercise['id']}"):
                        show_log_workout_form(exercise, day_plan['day'])
                
                st.markdown("---")

def show_log_workout_form(exercise: Dict[str, Any], day: int):
    st.subheader(f"Log Workout: {exercise['name']}")
    
    with st.form(f"log_form_{exercise['id']}"):
        col1, col2 = st.columns(2)
        
        with col1:
            sets_completed = st.number_input(
                "Sets Completed",
                min_value=0,
                max_value=10,
                value=exercise.get('sets', 1)
            )
            
            reps_completed = st.number_input(
                "Reps Completed",
                min_value=0,
                max_value=100,
                value=exercise.get('reps', 10) if exercise.get('reps') else 10
            )
        
        with col2:
            duration_completed = st.number_input(
                "Duration (seconds)",
                min_value=0,
                max_value=3600,
                value=exercise.get('duration', 0) if exercise.get('duration') else 0
            )
            
            weight_used = st.number_input(
                "Weight Used (kg)",
                min_value=0.0,
                max_value=500.0,
                value=0.0,
                step=0.5
            )
        
        notes = st.text_area("Notes (optional)")
        
        submitted = st.form_submit_button("Log Workout")
        
        if submitted:
            log_data = {
                "exercise_id": exercise['id'],
                "sets_completed": int(sets_completed),
                "reps_completed": int(reps_completed),
                "duration_completed": int(duration_completed) if duration_completed > 0 else None,
                "weight_used": float(weight_used) if weight_used > 0 else None,
                "notes": notes if notes else None
            }
            
            result = api.log_workout(log_data)
            if "error" not in result:
                st.success("Workout logged successfully!")
                st.rerun()
            else:
                st.error(result["error"])

def show_progress_tracking():
    st.title("📊 Progress Tracking")
    st.markdown("---")
    
    # Progress stats
    stats = api.get_progress_stats()
    if "error" not in stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Workouts", stats['total_workouts'])
        with col2:
            st.metric("Total Time", f"{stats['total_time_minutes']} min")
        with col3:
            st.metric("Muscle Groups", len(stats['muscle_groups_trained']))
        with col4:
            st.metric("Avg/Week", f"{stats['avg_workouts_per_week']:.1f}")
        
        if stats['muscle_groups_trained']:
            st.markdown("**Muscle Groups Trained:** " + ", ".join(stats['muscle_groups_trained']))
    
    st.markdown("---")
    
    # Progress history
    days_to_show = st.selectbox("Show history for:", [7, 14, 30], index=0)
    history = api.get_progress_history(days_to_show)
    
    if history:
        # Create DataFrame for visualization
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        
        # Workouts over time
        fig_workouts = px.line(
            df, 
            x='date', 
            y='workouts_count',
            title='Workouts Over Time',
            labels={'workouts_count': 'Number of Workouts', 'date': 'Date'}
        )
        st.plotly_chart(fig_workouts, use_container_width=True)
        
        # Duration over time
        if 'total_duration' in df.columns:
            fig_duration = px.bar(
                df, 
                x='date', 
                y='total_duration',
                title='Workout Duration Over Time',
                labels={'total_duration': 'Duration (seconds)', 'date': 'Date'}
            )
            st.plotly_chart(fig_duration, use_container_width=True)
        
        # Muscle groups heatmap
        if any(df['muscle_groups'].apply(len) > 0):
            muscle_group_data = []
            for _, row in df.iterrows():
                for muscle in row['muscle_groups']:
                    muscle_group_data.append({
                        'date': row['date'],
                        'muscle_group': muscle,
                        'trained': 1
                    })
            
            if muscle_group_data:
                muscle_df = pd.DataFrame(muscle_group_data)
                muscle_pivot = muscle_df.pivot_table(
                    index='muscle_group', 
                    columns='date', 
                    values='trained', 
                    fill_value=0
                )
                
                fig_heatmap = px.imshow(
                    muscle_pivot,
                    title='Muscle Groups Trained (Heatmap)',
                    labels={'color': 'Trained'},
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No workout history found. Start logging your workouts to see progress!")

def show_sidebar():
    with st.sidebar:
        st.markdown("### 👋 Welcome!")
        if st.session_state.user_info:
            st.markdown(f"**{st.session_state.user_info['full_name']}**")
            st.markdown(f"📧 {st.session_state.user_info['email']}")
            st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_info = None
            st.session_state.current_plan = None
            st.rerun()

def main():
    st.set_page_config(
        page_title="Workout Planner",
        page_icon="🏋️‍♂️",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        padding: 1rem 0;
        border-bottom: 2px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if user is authenticated
    if not st.session_state.token:
        show_auth_page()
    else:
        show_sidebar()
        
        # Main navigation
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "💪 Create Plan", "📋 Current Plan", "📊 Progress"])
        
        with tab1:
            st.title("🏠 Dashboard")
            st.markdown("---")
            
            # Quick stats
            stats = api.get_progress_stats()
            if "error" not in stats and stats['total_workouts'] > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Workouts", stats['total_workouts'])
                with col2:
                    st.metric("This Week", f"{stats['avg_workouts_per_week']:.1f}")
                with col3:
                    st.metric("Total Time", f"{stats['total_time_minutes']} min")
            
            # Recent activity
            st.subheader("Recent Activity")
            recent_history = api.get_progress_history(7)
            if recent_history:
                for day in recent_history[-3:]:  # Show last 3 days
                    if day['workouts_count'] > 0:
                        st.markdown(f"**{day['date']}**: {day['workouts_count']} workouts, {day['total_duration']}s total")
            else:
                st.info("No recent activity. Start working out to see your progress!")
            
            # Quick actions
            st.subheader("Quick Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🆕 Create New Plan", use_container_width=True):
                    st.switch_page("Create Plan")
            with col2:
                if st.button("📝 Log Workout", use_container_width=True):
                    st.switch_page("Current Plan")
        
        with tab2:
            show_workout_plan_generator()
        
        with tab3:
            show_current_plan()
        
        with tab4:
            show_progress_tracking()

if __name__ == "__main__":
    main()