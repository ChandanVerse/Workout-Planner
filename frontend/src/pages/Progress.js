import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { apiClient } from '../utils/api';
import { showError } from '../utils/notifications';

const Progress = () => {
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30'); // days
  const [selectedMetric, setSelectedMetric] = useState('volume');

  useEffect(() => {
    fetchWorkouts();
  }, [timeRange]);

  const fetchWorkouts = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/workouts/');
      setWorkouts(response.data);
    } catch (error) {
      showError('Failed to fetch workout data');
      console.error('Error fetching workouts:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterWorkoutsByTimeRange = (workouts, days) => {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - parseInt(days));
    
    return workouts.filter(workout => 
      new Date(workout.date) >= cutoffDate
    );
  };

  const generateProgressData = () => {
    const filteredWorkouts = filterWorkoutsByTimeRange(workouts, timeRange);
    
    // Group workouts by date
    const workoutsByDate = {};
    filteredWorkouts.forEach(workout => {
      const date = workout.date;
      if (!workoutsByDate[date]) {
        workoutsByDate[date] = [];
      }
      workoutsByDate[date].push(workout);
    });

    // Calculate daily metrics
    const progressData = Object.entries(workoutsByDate).map(([date, dayWorkouts]) => {
      const totalVolume = dayWorkouts.reduce((sum, w) => 
        sum + (w.sets * w.reps * (w.weight || 0)), 0
      );
      const totalSets = dayWorkouts.reduce((sum, w) => sum + w.sets, 0);
      const totalReps = dayWorkouts.reduce((sum, w) => sum + w.reps, 0);
      const exerciseCount = dayWorkouts.length;

      return {
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        fullDate: date,
        volume: totalVolume,
        sets: totalSets,
        reps: totalReps,
        exercises: exerciseCount
      };
    }).sort((a, b) => new Date(a.fullDate) - new Date(b.fullDate));

    return progressData;
  };

  const generateExerciseBreakdown = () => {
    const filteredWorkouts = filterWorkoutsByTimeRange(workouts, timeRange);
    
    const exerciseStats = {};
    filteredWorkouts.forEach(workout => {
      const exerciseName = workout.exercise?.name || 'Unknown Exercise';
      if (!exerciseStats[exerciseName]) {
        exerciseStats[exerciseName] = {
          name: exerciseName,
          count: 0,
          totalVolume: 0,
          totalSets: 0,
          totalReps: 0
        };
      }
      exerciseStats[exerciseName].count++;
      exerciseStats[exerciseName].totalVolume += workout.sets * workout.reps * (workout.weight || 0);
      exerciseStats[exerciseName].totalSets += workout.sets;
      exerciseStats[exerciseName].totalReps += workout.reps;
    });

    return Object.values(exerciseStats)
      .sort((a, b) => b.count - a.count)
      .slice(0, 10); // Top 10 exercises
  };

  const generateWeeklyComparison = () => {
    const filteredWorkouts = filterWorkoutsByTimeRange(workouts, timeRange);
    
    const weeklyData = {};
    filteredWorkouts.forEach(workout => {
      const date = new Date(workout.date);
      const weekStart = new Date(date.setDate(date.getDate() - date.getDay()));
      const weekKey = weekStart.toISOString().split('T')[0];
      
      if (!weeklyData[weekKey]) {
        weeklyData[weekKey] = {
          week: weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          workouts: 0,
          totalVolume: 0,
          totalSets: 0
        };
      }
      weeklyData[weekKey].workouts++;
      weeklyData[weekKey].totalVolume += workout.sets * workout.reps * (workout.weight || 0);
      weeklyData[weekKey].totalSets += workout.sets;
    });

    return Object.values(weeklyData).sort((a, b) => new Date(a.week) - new Date(b.week));
  };

  const calculateStats = () => {
    const filteredWorkouts = filterWorkoutsByTimeRange(workouts, timeRange);
    
    const totalWorkouts = filteredWorkouts.length;
    const totalVolume = filteredWorkouts.reduce((sum, w) => 
      sum + (w.sets * w.reps * (w.weight || 0)), 0
    );
    const totalSets = filteredWorkouts.reduce((sum, w) => sum + w.sets, 0);
    const totalReps = filteredWorkouts.reduce((sum, w) => sum + w.reps, 0);
    const uniqueExercises = new Set(filteredWorkouts.map(w => w.exercise?.name)).size;

    const avgWorkoutsPerWeek = totalWorkouts / (parseInt(timeRange) / 7);
    const avgVolumePerWorkout = totalWorkouts > 0 ? totalVolume / totalWorkouts : 0;

    return {
      totalWorkouts,
      totalVolume,
      totalSets,
      totalReps,
      uniqueExercises,
      avgWorkoutsPerWeek: Math.round(avgWorkoutsPerWeek * 10) / 10,
      avgVolumePerWorkout: Math.round(avgVolumePerWorkout)
    };
  };

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0'];

  if (loading) {
    return (
      <div className="progress-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading progress data...</p>
        </div>
      </div>
    );
  }

  const progressData = generateProgressData();
  const exerciseBreakdown = generateExerciseBreakdown();
  const weeklyData = generateWeeklyComparison();
  const stats = calculateStats();

  return (
    <div className="progress-container">
      <div className="progress-header">
        <h2>Workout Progress</h2>
        <div className="progress-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 3 months</option>
            <option value="180">Last 6 months</option>
            <option value="365">Last year</option>
          </select>
        </div>
      </div>

      {workouts.length === 0 ? (
        <div className="no-data">
          <h3>No workout data available</h3>
          <p>Start logging your workouts to see progress charts!</p>
        </div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>{stats.totalWorkouts}</h3>
              <p>Total Workouts</p>
            </div>
            <div className="stat-card">
              <h3>{stats.totalVolume.toLocaleString()}</h3>
              <p>Total Volume (kg)</p>
            </div>
            <div className="stat-card">
              <h3>{stats.totalSets}</h3>
              <p>Total Sets</p>
            </div>
            <div className="stat-card">
              <h3>{stats.totalReps}</h3>
              <p>Total Reps</p>
            </div>
            <div className="stat-card">
              <h3>{stats.uniqueExercises}</h3>
              <p>Unique Exercises</p>
            </div>
            <div className="stat-card">
              <h3>{stats.avgWorkoutsPerWeek}</h3>
              <p>Avg Workouts/Week</p>
            </div>
          </div>

          <div className="charts-container">
            <div className="chart-section">
              <h3>Daily Progress</h3>
              <div className="chart-controls">
                <select 
                  value={selectedMetric} 
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  className="metric-select"
                >
                  <option value="volume">Volume (kg)</option>
                  <option value="sets">Sets</option>
                  <option value="reps">Reps</option>
                  <option value="exercises">Exercises</option>
                </select>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={progressData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey={selectedMetric} 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    dot={{ fill: '#8884d8' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-section">
              <h3>Weekly Comparison</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="workouts" fill="#8884d8" name="Workouts" />
                  <Bar dataKey="totalSets" fill="#82ca9d" name="Total Sets" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-section">
              <h3>Exercise Breakdown</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={exerciseBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {exerciseBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-section">
              <h3>Top Exercises</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={exerciseBreakdown.slice(0, 5)} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={100} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Progress;