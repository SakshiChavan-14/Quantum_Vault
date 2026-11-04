import React, { useState } from 'react';
import AuthLayout from '../../components/layout/AuthLayout';
import LoginForm from '../../components/common/LoginForm';
import SignupForm from '../../components/common/SignupForm';
import ForgotPasswordForm from '../../components/common/ForgotPasswordForm';

const Auth = () => {
  const [currentView, setCurrentView] = useState('login');

  const handleBackClick = () => {
    console.log('Back clicked to go to Landing');
  };

  
  let title = '';
  let subtitle = '';

  if (currentView === 'login') {
    title = 'Welcome back';
    subtitle = 'Sign in to continue to CloudVault';
  } else if (currentView === 'signup') {
    title = 'Create an account';
    subtitle = 'Join CloudVault today';
  } else if (currentView === 'forgot') {
    title = 'Reset password';
    subtitle = 'Enter your email to receive a reset link';
  }

  return (
    <AuthLayout title={title} subtitle={subtitle} onBackClick={handleBackClick}>
      {currentView === 'login' && (
        <LoginForm
          onSwitchToSignup={() => setCurrentView('signup')}
          onSwitchToForgot={() => setCurrentView('forgot')}
        />
      )}
      {currentView === 'signup' && (
        <SignupForm onSwitchToLogin={() => setCurrentView('login')} />
      )}
      {currentView === 'forgot' && (
        <ForgotPasswordForm onSwitchToLogin={() => setCurrentView('login')} />
      )}
    </AuthLayout>
  );
};

export default Auth;
