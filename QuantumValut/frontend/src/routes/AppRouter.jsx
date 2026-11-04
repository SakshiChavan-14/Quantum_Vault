import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import PublicRoute from './PublicRoute';
import ProtectedRoute from './ProtectedRoute';
import Landing from '../pages/Landing/Landing';
import Auth from '../pages/Auth/Auth';
import Dashboard from '../pages/Dashboard/Dashboard';
import NotFound from '../pages/NotFound/NotFound';

const AppRouter = () => {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicRoute>
            <Landing />
          </PublicRoute>
        }
      />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Auth />
          </PublicRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route path="/404" element={<NotFound />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};

export default AppRouter;
