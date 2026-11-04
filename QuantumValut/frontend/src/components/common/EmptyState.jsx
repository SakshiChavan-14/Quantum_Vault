import React from 'react';

const EmptyState = () => {
  return (
    <div className="empty-state" id="empty-state">
      <svg width="96" height="96" viewBox="0 0 24 24" fill="#5f6368">
        <path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z" />
      </svg>
      <h3>No files yet</h3>
      <p>Upload files or create folders to get started</p>
      <button className="btn-primary" onClick={(e) => e.preventDefault()}>
        Upload files
      </button>
      <button className="btn-secondary" onClick={(e) => e.preventDefault()}>
        Create document
      </button>
    </div>
  );
};

export default EmptyState;
