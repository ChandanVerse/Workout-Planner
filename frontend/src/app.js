import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated } from './utils/auth';
import Login from './pages/Login';
import Register from './pages/Register';
import WorkoutForm from './pages/WorkoutForm';
import PlanDisplay from './pages/PlanDisplay';
import Progress from './pages/Progress';
import Navbar from './components/Navbar';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="main-content">
          <Routes>
            <Route 
              path="/login" 
              element={!isAuthenticated() ? <Login /> : <Navigate to="/workout" />} 
            />
            <Route 
              path="/register" 
              element={!isAuthenticated() ? <Register /> : <Navigate to="/workout" />} 
            />
            <Route 
              path="/workout" 
              element={isAuthenticated() ? <WorkoutForm /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/plan" 
              element={isAuthenticated() ? <PlanDisplay /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/progress" 
              element={isAuthenticated() ? <Progress /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/" 
              element={<Navigate to={isAuthenticated() ? "/workout" : "/login"} />} 
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;