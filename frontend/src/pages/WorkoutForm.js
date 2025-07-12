import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { workoutAPI } from '../api';

const WorkoutForm = () => {
  const [formData, setFormData] = useState({
    focus_areas: [],
    available_equipment: [],
    workout_type: 'strength',
    user_level: 'beginner',
    days_per_week: 3,
    session_duration: 60
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const focusAreaOptions = [
    'chest', 'back', 'shoulders', 'arms', 'legs', 'core', 'full body'
  ];

  const equipmentOptions = [
    'bodyweight', 'dumbbells', 'barbell', 'resistance bands', 'machines'
  ];

  const handleCheckboxChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(item => item !== value)
        : [...prev[field], value]
    }));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'days_per_week' || name === 'session_duration' 
        ? parseInt(value) 
        : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await workoutAPI.createPlan(formData);
      // Store the plan in localStorage for the PlanDisplay component
      localStorage.setItem('current_plan', JSON.stringify(response.data));
      navigate('/plan');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create workout plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="workout-form-container">
      <h2>Create Your Workout Plan</h2>
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit} className="workout-form">
        <div className="form-section">
          <h3>Focus Areas</h3>
          <div className="checkbox-group">
            {focusAreaOptions.map(area => (
              <label key={area} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.focus_areas.includes(area)}
                  onChange={() => handleCheckboxChange('focus_areas', area)}
                />
                {area.charAt(0).toUpperCase() + area.slice(1)}
              </label>
            ))}
          </div>
        </div>

        <div className="form-section">
          <h3>Available Equipment</h3>
          <div className="checkbox-group">
            {equipmentOptions.map(equipment => (
              <label key={equipment} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.available_equipment.includes(equipment)}
                  onChange={() => handleCheckboxChange('available_equipment', equipment)}
                />
                {equipment.charAt(0).toUpperCase() + equipment.slice(1)}
              </label>
            ))}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="workout_type">Workout Type</label>
            <select
              id="workout_type"
              name="workout_type"
              value={formData.workout_type}
              onChange={handleChange}
            >
              <option value="strength">Strength</option>
              <option value="cardio">Cardio</option>
              <option value="flexibility">Flexibility</option>
              <option value="mixed">Mixed</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="user_level">Experience Level</label>
            <select
              id="user_level"
              name="user_level"
              value={formData.user_level}
              onChange={handleChange}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="days_per_week">Days per Week</label>
            <input
              type="number"
              id="days_per_week"
              name="days_per_week"
              value={formData.days_per_week}
              onChange={handleChange}
              min="1"
              max="7"
            />
          </div>

          <div className="form-group">
            <label htmlFor="session_duration">Session Duration (minutes)</label>
            <input
              type="number"
              id="session_duration"
              name="session_duration"
              value={formData.session_duration}
              onChange={handleChange}
              min="15"
              max="180"
            />
          </div>
        </div>

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Creating Plan...' : 'Create Workout Plan'}
        </button>
      </form>
    </div>
  );
};

export default WorkoutForm;