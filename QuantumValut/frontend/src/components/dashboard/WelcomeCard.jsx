import React from 'react';

const WelcomeCard = ({ user }) => {
  if (!user) return null;

  const firstName = user.full_name ? user.full_name.split(' ')[0] : 'User';

  return (
    <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: 'var(--bg-surface, #fff)', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 500 }}>Welcome back, {firstName}</h2>
      {user.is_verified && <span style={{ fontSize: '12px', color: '#34a853' }}>Verified Account</span>}
    </div>
  );
};

export default WelcomeCard;
