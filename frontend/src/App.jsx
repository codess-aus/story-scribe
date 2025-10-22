/**
 * StoryScribe - Main Application Component
 * 
 * This is the primary component for the StoryScribe application, integrating
 * the writing interface, prompt system, and navigation components.
 * 
 * The application uses React Router for navigation and Context API for state
 * management across components.


Interesting fact: React's component-based architecture was inspired by the XHP extension for PHP used internally at Facebook. The approach of breaking UIs into reusable components was revolutionary when React was first released in 2013 and has since become the standard pattern for modern web development frameworks.
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppStateProvider } from './contexts/AppStateContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Components
import Navbar from './components/layout/Navbar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import StoryEditor from './pages/StoryEditor';
import BookDevelopment from './pages/BookDevelopment';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

// Styles
import './styles/App.css';

/**
 * Protected route component that redirects to login if user is not authenticated
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

/**
 * Main App component that sets up routing and global providers
 */
function App() {
  const [isLoading, setIsLoading] = useState(true);
  
  // Simulate initial loading (e.g., checking auth status)
  useEffect(() => {
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  }, []);
  
  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <h2>Loading StoryScribe...</h2>
      </div>
    );
  }
  
  return (
    <Router>
      <AuthProvider>
        <AppStateProvider>
          <div className="app-container">
            <Navbar />
            <main className="main-content">
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                
                <Route path="/" element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } />
                
                <Route path="/write" element={
                  <ProtectedRoute>
                    <StoryEditor />
                  </ProtectedRoute>
                } />
                
                <Route path="/edit/:storyId" element={
                  <ProtectedRoute>
                    <StoryEditor />
                  </ProtectedRoute>
                } />
                
                <Route path="/book-development" element={
                  <ProtectedRoute>
                    <BookDevelopment />
                  </ProtectedRoute>
                } />
                
                <Route path="/settings" element={
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                } />
                
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
            <footer className="app-footer">
              <p>StoryScribe © {new Date().getFullYear()} - Your Trustworthy AI Writing Assistant</p>
            </footer>
          </div>
        </AppStateProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
