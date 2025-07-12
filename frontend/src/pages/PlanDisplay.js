import React, { useState, useEffect } from 'react';
import { apiClient } from '../utils/api';
import { showError, showSuccess } from '../utils/notifications';

const PlanDisplay = ({ planId }) => {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completedExercises, setCompletedExercises] = useState(new Set());
  const [expandedDays, setExpandedDays] = useState(new Set());

  useEffect(() => {
    if (planId) {
      fetchPlan();
    }
  }, [planId]);

  const fetchPlan = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/plans/${planId}`);
      setPlan(response.data);
      
      // Initialize expanded days (expand first day by default)
      if (response.data.exercises && Object.keys(response.data.exercises).length > 0) {
        setExpandedDays(new Set([Object.keys(response.data.exercises)[0]]));
      }
    } catch (error) {
      showError('Failed to fetch workout plan');
      console.error('Error fetching plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDay = (day) => {
    const newExpanded = new Set(expandedDays);
    if (newExpanded.has(day)) {
      newExpanded.delete(day);
    } else {
      newExpanded.add(day);
    }
    setExpandedDays(newExpanded);
  };

  const logExerciseCompletion = async (exerciseId, sets, reps, weight = null) => {
    try {
      const workoutData = {
        exercise_id: exerciseId,
        sets: parseInt(sets),
        reps: parseInt(reps),
        weight: weight ? parseFloat(weight) : null,
        date: new Date().toISOString().split('T')[0]
      };

      await apiClient.post('/workouts/', workoutData);
      setCompletedExercises(prev => new Set([...prev, exerciseId]));
      showSuccess('Exercise logged successfully!');
    } catch (error) {
      showError('Failed to log exercise');
      console.error('Error logging exercise:', error);
    }
  };

  const ExerciseCard = ({ exercise, dayIndex }) => {
    const [sets, setSets] = useState(exercise.sets || 3);
    const [reps, setReps] = useState(exercise.reps || 10);
    const [weight, setWeight] = useState('');
    const [isLogging, setIsLogging] = useState(false);

    const handleLog = async () => {
      setIsLogging(true);
      await logExerciseCompletion(exercise.id, sets, reps, weight);
      setIsLogging(false);
    };

    const isCompleted = completedExercises.has(exercise.id);

    return (
      <div className={`exercise-card ${isCompleted ? 'completed' : ''}`}>
        <div className="exercise-header">
          <h4 className="exercise-name">{exercise.name}</h4>
          {isCompleted && <span className="completed-badge">✓ Completed</span>}
        </div>
        
        <div className="exercise-details">
          <p className="exercise-description">{exercise.description}</p>
          
          <div className="exercise-params">
            <div className="param-group">
              <label>Sets:</label>
              <input
                type="number"
                value={sets}
                onChange={(e) => setSets(e.target.value)}
                min="1"
                max="10"
              />
            </div>
            <div className="param-group">
              <label>Reps:</label>
              <input
                type="number"
                value={reps}
                onChange={(e) => setReps(e.target.value)}
                min="1"
                max="50"
              />
            </div>
            <div className="param-group">
              <label>Weight (kg):</label>
              <input
                type="number"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
                placeholder="Optional"
                step="0.5"
              />
            </div>
          </div>

          <button
            className={`log-btn ${isCompleted ? 'logged' : ''}`}
            onClick={handleLog}
            disabled={isLogging || isCompleted}
          >
            {isLogging ? 'Logging...' : isCompleted ? 'Logged' : 'Log Exercise'}
          </button>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="plan-display">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading workout plan...</p>
        </div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="plan-display">
        <div className="no-plan">
          <h3>No workout plan selected</h3>
          <p>Generate a new workout plan to get started!</p>
        </div>
      </div>
    );
  }

  const exercisesByDay = plan.exercises || {};
  const days = Object.keys(exercisesByDay).sort();

  return (
    <div className="plan-display">
      <div className="plan-header">
        <h2>{plan.name}</h2>
        <div className="plan-meta">
          <span className="plan-goal">Goal: {plan.goal}</span>
          <span className="plan-duration">Duration: {plan.duration} weeks</span>
          <span className="plan-created">
            Created: {new Date(plan.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="plan-description">
        <p>{plan.description}</p>
      </div>

      <div className="workout-schedule">
        <h3>Weekly Schedule</h3>
        {days.length === 0 ? (
          <div className="no-exercises">
            <p>No exercises found in this plan.</p>
          </div>
        ) : (
          days.map((day, index) => (
            <div key={day} className="day-section">
              <div 
                className={`day-header ${expandedDays.has(day) ? 'expanded' : ''}`}
                onClick={() => toggleDay(day)}
              >
                <h4>
                  <span className="day-number">Day {index + 1}</span>
                  <span className="day-name">{day}</span>
                </h4>
                <div className="day-stats">
                  <span className="exercise-count">
                    {exercisesByDay[day].length} exercises
                  </span>
                  <span className="expand-icon">
                    {expandedDays.has(day) ? '▼' : '▶'}
                  </span>
                </div>
              </div>

              {expandedDays.has(day) && (
                <div className="day-exercises">
                  {exercisesByDay[day].map((exercise, exerciseIndex) => (
                    <ExerciseCard
                      key={exercise.id || exerciseIndex}
                      exercise={exercise}
                      dayIndex={index}
                    />
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <div className="plan-actions">
        <button className="secondary-btn" onClick={fetchPlan}>
          Refresh Plan
        </button>
      </div>
    </div>
  );
};

export default PlanDisplay;