import React from 'react';
import SectionHeader from '../common/SectionHeader';

const ActivityFeed = ({ activity }) => {
  if (!activity || activity.length === 0) return null;

  return (
    <div style={{ marginBottom: '24px' }}>
      <SectionHeader title="Recent Activity" />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {activity.map(item => (
          <div key={item.id} style={{ padding: '12px', backgroundColor: 'var(--bg-surface, #fff)', borderRadius: '8px', border: '1px solid var(--border-color, #e0e0e0)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#1a73e8' }}></div>
              <span style={{ fontWeight: 500, textTransform: 'capitalize' }}>{item.action}</span>
              {item.target_name && <span>: {item.target_name}</span>}
              <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-secondary, #5f6368)' }}>
                {new Date(item.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ActivityFeed;
