import React from 'react';
import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', textAlign: 'center' }}>
      <h1>404 - Page Not Found</h1>
      <p style={{ margin: '20px 0', color: '#5f6368' }}>The page you are looking for does not exist.</p>
      <button className="btn-primary" onClick={() => navigate('/')}>
        Return to Home
      </button>
    </div>
  );
};

export default NotFound;
