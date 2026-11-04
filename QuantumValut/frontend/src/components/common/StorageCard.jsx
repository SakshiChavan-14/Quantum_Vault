import React from 'react';
import { useDashboard } from '../../hooks/useDashboard';

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 MB';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const StorageCard = () => {
  const { storage, loading } = useDashboard();

  if (loading || !storage) {
    return (
      <div className="sidebar-storage">
        <div className="storage-label">Storage</div>
        <div className="storage-progress">
          <div className="storage-bar">
            <div className="storage-fill" style={{ width: '0%' }}></div>
          </div>
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  const { used_storage, total_storage, percentage_used } = storage;
  
  return (
    <div className="sidebar-storage">
      <div className="storage-label">Storage</div>
      <div className="storage-progress">
        <div className="storage-bar">
          <div className="storage-fill" id="storage-bar-fill" style={{ width: `${percentage_used}%` }}></div>
        </div>
        <span id="storage-text">{formatBytes(used_storage)} of {formatBytes(total_storage)} used</span>
      </div>
    </div>
  );
};

export default StorageCard;

