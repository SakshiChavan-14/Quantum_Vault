import React from 'react';

const Footer = () => {
  return (
    <footer className="footer-landing">
      <div className="section-container">
        <div className="footer-content">
          <div className="footer-logo">
            <svg width="32" height="32" viewBox="0 0 40 40" fill="none">
              <rect width="40" height="40" rx="8" fill="#1a73e8" />
              <path
                d="M12 28V12h8c3.3 0 6 2.7 6 6s-2.7 6-6 6h-4v4H12zm4-8h4c1.1 0 2-.9 2-2s-.9-2-2-2h-4v4z"
                fill="white"
              />
            </svg>
            <span>CloudVault</span>
          </div>
          <p>Your trusted cloud storage solution.</p>
          <div className="footer-links">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Help</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
