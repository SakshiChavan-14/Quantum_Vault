import React from 'react';

const AuthLayout = ({ title, subtitle, children, onBackClick }) => {
  return (
    <div id="auth-page" className="page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <svg
              width="48"
              height="48"
              viewBox="0 0 40 40"
              fill="none"
              onClick={onBackClick}
              style={{ cursor: 'pointer' }}
            >
              <rect width="40" height="40" rx="8" fill="#1a73e8" />
              <path
                d="M12 28V12h8c3.3 0 6 2.7 6 6s-2.7 6-6 6h-4v4H12zm4-8h4c1.1 0 2-.9 2-2s-.9-2-2-2h-4v4z"
                fill="white"
              />
            </svg>
            <h1 id="auth-title">{title}</h1>
            <p id="auth-subtitle">{subtitle}</p>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
