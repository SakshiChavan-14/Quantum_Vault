import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const UserProfile = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async (e) => {
    e.preventDefault();
    const result = await logout();
    if (result.success) {
      navigate('/');
    }
  };

  const initial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U';

  return (
    <div className="user-menu" ref={dropdownRef}>
      <div 
        className="user-avatar" 
        id="user-avatar"
        onClick={() => setIsOpen(!isOpen)}
        style={{ cursor: 'pointer' }}
      >
        {initial}
      </div>
      <div className={`user-dropdown ${!isOpen ? 'hidden' : ''}`} id="user-dropdown">
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-color, #e0e0e0)', marginBottom: '8px' }}>
          <div style={{ fontWeight: 500 }}>{user?.full_name}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary, #5f6368)' }}>{user?.email}</div>
          <div style={{ fontSize: '12px', marginTop: '4px', color: user?.is_verified ? '#34a853' : '#ea4335' }}>
            {user?.is_verified ? 'Verified' : 'Unverified'}
          </div>
        </div>
        <a href="#" onClick={(e) => { e.preventDefault(); setIsOpen(false); }}>
          Switch Account
        </a>
        <a href="#" onClick={handleLogout}>
          Sign Out
        </a>
      </div>
    </div>
  );
};

export default UserProfile;
