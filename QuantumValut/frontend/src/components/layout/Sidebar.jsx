import React from 'react';
import { useSidebarStore } from '../../store/sidebarStore';
import StorageCard from '../common/StorageCard';

const Sidebar = ({ onOpenUpload, onOpenNewFolder }) => {
  const { activeView, setActiveView } = useSidebarStore();

  return (
    <aside className="sidebar" id="sidebar">
      <div className="sidebar-header">
        <div className="logo-sidebar" onClick={() => setActiveView('my-drive')} style={{ cursor: 'pointer' }}>
          <svg width="32" height="32" viewBox="0 0 40 40" fill="none">
            <rect width="40" height="40" rx="8" fill="#1a73e8" />
            <path
              d="M12 28V12h8c3.3 0 6 2.7 6 6s-2.7 6-6 6h-4v4H12zm4-8h4c1.1 0 2-.9 2-2s-.9-2-2-2h-4v4z"
              fill="white"
            />
          </svg>
          <span>QuantumVault</span>
        </div>
      </div>

      <div className="sidebar-actions" style={{ display: 'flex', gap: '8px', padding: '16px' }}>
        <button 
          className="btn-new" 
          id="sidebar-upload-btn"
          onClick={() => onOpenUpload && onOpenUpload()}
          style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
          </svg>
          <span>Upload</span>
        </button>
        <button 
          className="btn-new btn-document" 
          id="sidebar-new-folder-btn"
          onClick={() => onOpenNewFolder && onOpenNewFolder()}
          style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
          </svg>
          <span>Folder</span>
        </button>
      </div>

      <nav className="sidebar-nav">
        <a
          href="#my-drive"
          className={`nav-item ${activeView === 'my-drive' ? 'active' : ''}`}
          id="nav-my-drive"
          onClick={(e) => {
            e.preventDefault();
            setActiveView('my-drive');
          }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
          </svg>
          <span>My Drive</span>
        </a>

        <a
          href="#recent"
          className={`nav-item ${activeView === 'recent' ? 'active' : ''}`}
          id="nav-recent"
          onClick={(e) => {
            e.preventDefault();
            setActiveView('recent');
          }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" />
          </svg>
          <span>Recent</span>
        </a>

        <a
          href="#starred"
          className={`nav-item ${activeView === 'starred' ? 'active' : ''}`}
          id="nav-starred"
          onClick={(e) => {
            e.preventDefault();
            setActiveView('starred');
          }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
          </svg>
          <span>Starred</span>
        </a>

        <a
          href="#audit"
          className={`nav-item ${activeView === 'audit' ? 'active' : ''}`}
          id="nav-audit"
          onClick={(e) => {
            e.preventDefault();
            setActiveView('audit');
          }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z" />
          </svg>
          <span>Security & Audit</span>
        </a>
      </nav>

      <StorageCard />
    </aside>
  );
};

export default Sidebar;
