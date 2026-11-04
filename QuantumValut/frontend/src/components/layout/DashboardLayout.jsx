import React from 'react';
import Sidebar from './Sidebar';
import DashboardNavbar from './DashboardNavbar';

const DashboardLayout = ({ children }) => {
  return (
    <div id="dashboard-page" className="page">
      <Sidebar />
      <main className="main-content">
        <DashboardNavbar />
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;
