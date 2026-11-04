import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

const PublicRoute = ({ children }) => {
  const { isAuthenticated, isInitialized } = useAuthStore();

  if (!isInitialized) {
    return (
      <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div style={{ color: '#5f6368' }}>Loading...</div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default PublicRoute;
