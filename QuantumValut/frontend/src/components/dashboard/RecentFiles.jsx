import React from 'react';
import SectionHeader from '../common/SectionHeader';
import { PqcSecurityBadge } from '../common/PqcSecurityBadge';
import { fileService } from '../../services/fileService';

const RecentFiles = ({ files, onDownload }) => {
  if (!files || files.length === 0) return null;

  const handleDownload = (fileId, name) => {
    if (onDownload) {
      onDownload(fileId, name);
    } else {
      fileService.downloadFile(fileId, name);
    }
  };

  return (
    <div style={{ marginBottom: '24px' }}>
      <SectionHeader title="Recent Files" />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {files.map(file => (
          <div 
            key={file.id} 
            style={{ 
              padding: '12px 16px', 
              backgroundColor: '#ffffff', 
              borderRadius: '8px', 
              border: '1px solid #e5e7eb', 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
              gap: '12px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
              <span style={{ fontSize: '20px' }}>📄</span>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 600, color: '#111827', fontSize: '14px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {file.name}
                </span>
                <span style={{ fontSize: '12px', color: '#6b7280' }}>
                  {fileService.formatFileSize(file.size)} • {fileService.formatDate(file.created_at)}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <PqcSecurityBadge algorithm={file.encryption_algorithm} fileHash={file.file_hash} size="small" />
              <button
                onClick={() => handleDownload(file.id, file.name)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#f3f4f6',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  color: '#1f2937'
                }}
                title="Download file"
              >
                📥 Download
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentFiles;
