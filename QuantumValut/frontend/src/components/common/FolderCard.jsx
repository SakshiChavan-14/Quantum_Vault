import React from 'react';

const FolderCard = ({ folder }) => {
  return (
    <div className="file-card">
      <div className="file-checkbox">
        <input type="checkbox" onChange={() => {}} />
      </div>
      <div className="file-icon folder">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="#5f6368">
          <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
        </svg>
      </div>
      <div className="file-info">
        <div className="file-name">{folder?.name || 'Untitled Folder'}</div>
        <div className="file-meta">{folder?.modified || 'Just now'}</div>
      </div>
      <div className="file-star">
        {folder?.starred ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#fbbc04">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M22 9.24l-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03L22 9.24zM12 15.4l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28L12 15.4z"/>
          </svg>
        )}
      </div>
      <div className="file-actions">
        <button className="icon-btn" onClick={(e) => e.preventDefault()}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default FolderCard;
