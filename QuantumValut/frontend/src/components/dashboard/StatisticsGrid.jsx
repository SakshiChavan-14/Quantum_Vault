import React from 'react';

const StatisticsGrid = ({ statistics }) => {
  if (!statistics) return null;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', marginBottom: '24px' }}>
      <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface, #fff)', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary, #5f6368)' }}>Total Files</div>
        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{statistics.total_files}</div>
      </div>
      <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface, #fff)', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary, #5f6368)' }}>Total Folders</div>
        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{statistics.total_folders}</div>
      </div>
      <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface, #fff)', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary, #5f6368)' }}>Favorites</div>
        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{statistics.favorites}</div>
      </div>
      <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface, #fff)', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary, #5f6368)' }}>Shared Files</div>
        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{statistics.shared_files}</div>
      </div>
    </div>
  );
};

export default StatisticsGrid;
