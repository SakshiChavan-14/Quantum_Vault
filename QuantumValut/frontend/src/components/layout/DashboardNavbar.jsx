import React from 'react';
import SearchBar from '../common/SearchBar';
import ThemeToggle from '../common/ThemeToggle';
import NotificationButton from '../common/NotificationButton';
import UserProfile from '../common/UserProfile';

const DashboardNavbar = () => {
  return (
    <header className="top-navbar">
      <div className="navbar-left">
        <button className="menu-toggle" onClick={(e) => e.preventDefault()}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" />
          </svg>
        </button>
        <div className="breadcrumb" id="breadcrumb">
          <span className="breadcrumb-item" onClick={(e) => e.preventDefault()}>
            My Drive
          </span>
        </div>
      </div>

      <div className="navbar-center">
        <SearchBar />
      </div>

      <div className="navbar-right">
        <ThemeToggle />
        <NotificationButton />
        {/* Preserving the original upload button from HTML as well */}
        <button className="icon-btn" onClick={(e) => document.getElementById('file-upload').click()}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z" />
          </svg>
        </button>
        <input type="file" id="file-upload" multiple hidden />
        <UserProfile />
      </div>
    </header>
  );
};

export default DashboardNavbar;
