import React from 'react';

const Navbar = () => {
  return (
    <nav className="navbar-landing">
      <div className="nav-container">
        <div className="logo">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
            <rect width="40" height="40" rx="8" fill="#1a73e8" />
            <path
              d="M12 28V12h8c3.3 0 6 2.7 6 6s-2.7 6-6 6h-4v4H12zm4-8h4c1.1 0 2-.9 2-2s-.9-2-2-2h-4v4z"
              fill="white"
            />
          </svg>
          <span>CloudVault</span>
        </div>
        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#storage">Storage</a>
          <a href="#" onClick={(e) => e.preventDefault()}>Login</a>
          <a href="#" onClick={(e) => e.preventDefault()} className="btn-primary-landing">
            Get Started
          </a>
        </div>
        <button className="mobile-menu-btn" onClick={(e) => e.preventDefault()}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" />
          </svg>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
