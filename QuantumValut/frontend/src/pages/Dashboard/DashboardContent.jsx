import React, { useState, useEffect } from 'react';
import { useSidebarStore } from '../../store/sidebarStore';
import { useDashboard } from '../../hooks/useDashboard';
import { useFiles } from '../../hooks/useFiles';
import { folderApi } from '../../api/folderApi';
import WelcomeCard from '../../components/dashboard/WelcomeCard';
import StatisticsGrid from '../../components/dashboard/StatisticsGrid';
import RecentFiles from '../../components/dashboard/RecentFiles';
import ActivityFeed from '../../components/dashboard/ActivityFeed';
import { FileList } from '../../components/FileList';
import { FileUpload } from '../../components/FileUpload';
import { AuditLogViewer } from '../../components/audit/AuditLogViewer';
import toast from 'react-hot-toast';

const DashboardContent = () => {
  const { activeView, setActiveView } = useSidebarStore();
  const { overview, recentFiles: dashRecentFiles, activity, loading: dashLoading, refreshDashboard } = useDashboard();
  const [currentFolder, setCurrentFolder] = useState(null);

  const {
    files,
    loading: filesLoading,
    error: filesError,
    page,
    totalPages,
    totalFiles,
    searchQuery,
    storageStats,
    uploadFile,
    downloadFile,
    deleteFile,
    renameFile,
    moveFile,
    toggleFavorite,
    search,
    goToPage,
    refresh: refreshFiles,
  } = useFiles(currentFolder?.id || null, 12);

  const [folders, setFolders] = useState([]);
  const [loadingFolders, setLoadingFolders] = useState(false);
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);

  const fetchFolders = async () => {
    try {
      setLoadingFolders(true);
      const data = await folderApi.getRootFolders();
      setFolders(data || []);
    } catch (err) {
      console.error('Failed to load folders:', err);
    } finally {
      setLoadingFolders(false);
    }
  };

  useEffect(() => {
    fetchFolders();
  }, []);

  const handleCreateFolder = async (e) => {
    e.preventDefault();
    if (!newFolderName.trim()) return;

    try {
      await folderApi.createFolder({ name: newFolderName.trim() });
      toast.success(`Folder "${newFolderName}" created successfully`);
      setNewFolderName('');
      setShowFolderModal(false);
      fetchFolders();
      refreshDashboard();
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to create folder';
      toast.error(msg);
    }
  };

  const handleFileUploadSuccess = async (file, metadata = {}) => {
    const meta = { ...metadata };
    if (currentFolder) {
      meta.folder_id = currentFolder.id;
    }
    const res = await uploadFile(file, meta);
    if (res) {
      refreshDashboard();
      fetchFolders();
    }
    return res;
  };

  const handleMoveFile = async (fileId, targetFolderId) => {
    const res = await moveFile(fileId, targetFolderId);
    if (res) {
      refreshDashboard();
      fetchFolders();
    }
    return res;
  };

  return (
    <div className="content-area" id="content-area" style={{ padding: '24px', overflowY: 'auto' }}>
      {/* Top Header / View Selector */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#111827', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            {activeView === 'my-drive' && (
              currentFolder ? (
                <>
                  <span
                    onClick={() => setCurrentFolder(null)}
                    style={{ cursor: 'pointer', color: '#1a73e8', textDecoration: 'underline' }}
                    title="Back to My Drive"
                  >
                    📁 My Drive
                  </span>
                  <span style={{ color: '#9ca3af', textDecoration: 'none' }}>/</span>
                  <span>📂 {currentFolder.name}</span>
                </>
              ) : (
                '📁 My Drive'
              )
            )}
            {activeView === 'recent' && '🕒 Recent Files'}
            {activeView === 'starred' && '⭐ Starred Files'}
            {activeView === 'audit' && '🛡️ Security & Audit Logs'}
          </h1>
          <p style={{ fontSize: '13px', color: '#6b7280', margin: '4px 0 0 0' }}>
            {currentFolder
              ? `Viewing files in folder "${currentFolder.name}"`
              : 'Quantum-safe encrypted storage powered by AES-256-GCM and Kyber-1024 Post-Quantum Cryptography.'}
          </p>
        </div>

        {activeView === 'my-drive' && (
          <div style={{ display: 'flex', gap: '8px' }}>
            {currentFolder && (
              <button
                onClick={() => setCurrentFolder(null)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#374151',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                ⬅ Back to My Drive
              </button>
            )}
            <button
              onClick={() => setShowFolderModal(true)}
              style={{
                padding: '8px 16px',
                backgroundColor: '#ffffff',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                color: '#374151',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📁 New Folder
            </button>
          </div>
        )}
      </div>

      {/* VIEW: AUDIT LOGS */}
      {activeView === 'audit' && <AuditLogViewer />}

      {/* VIEW: RECENT */}
      {activeView === 'recent' && (
        <div>
          <RecentFiles files={dashRecentFiles} onDownload={downloadFile} />
        </div>
      )}

      {/* VIEW: STARRED */}
      {activeView === 'starred' && (
        <div>
          <FileList
            files={files.filter(f => f.is_favorite)}
            loading={filesLoading}
            error={filesError}
            page={1}
            totalPages={1}
            searchQuery={searchQuery}
            onSearch={search}
            onGoToPage={goToPage}
            onUpload={handleFileUploadSuccess}
            onDelete={deleteFile}
            onDownload={downloadFile}
            onRename={renameFile}
            onMove={handleMoveFile}
            onToggleFavorite={toggleFavorite}
            storageStats={storageStats}
          />
        </div>
      )}

      {/* VIEW: MY DRIVE */}
      {activeView === 'my-drive' && (
        <>
          {/* Welcome & Statistics (only on root) */}
          {!currentFolder && (
            <>
              {overview?.user && <WelcomeCard user={overview.user} />}
              {overview?.statistics && <StatisticsGrid statistics={overview.statistics} />}
            </>
          )}

          {/* Quick Upload Action Banner */}
          <div style={{ marginBottom: '24px' }}>
            <FileUpload onUpload={handleFileUploadSuccess} />
          </div>

          {/* Folders Section (only on root) */}
          {!currentFolder && folders.length > 0 && (
            <div style={{ marginBottom: '24px' }}>
              <div style={{ fontSize: '15px', fontWeight: 600, color: '#111827', marginBottom: '12px' }}>
                Folders ({folders.length})
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
                {folders.map(folder => (
                  <div
                    key={folder.id}
                    onClick={() => setCurrentFolder(folder)}
                    style={{
                      padding: '14px 16px',
                      backgroundColor: '#ffffff',
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#1a73e8';
                      e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)';
                    }}
                    title={`Open folder "${folder.name}"`}
                  >
                    <span style={{ fontSize: '20px' }}>📁</span>
                    <span style={{ fontSize: '14px', fontWeight: 600, color: '#1f2937', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {folder.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Files List Section */}
          <div style={{ marginTop: '20px' }}>
            <div style={{ fontSize: '15px', fontWeight: 600, color: '#111827', marginBottom: '12px' }}>
              {currentFolder ? `Files in "${currentFolder.name}" (${totalFiles})` : `All Files (${totalFiles})`}
            </div>
            <FileList
              files={files}
              loading={filesLoading}
              error={filesError}
              page={page}
              totalPages={totalPages}
              searchQuery={searchQuery}
              onSearch={search}
              onGoToPage={goToPage}
              onUpload={handleFileUploadSuccess}
              onDelete={deleteFile}
              onDownload={downloadFile}
              onRename={renameFile}
              onMove={handleMoveFile}
              onToggleFavorite={toggleFavorite}
              storageStats={storageStats}
            />
          </div>

          {/* Activity Feed (only on root) */}
          {!currentFolder && activity && activity.length > 0 && (
            <div style={{ marginTop: '32px' }}>
              <ActivityFeed activity={activity} />
            </div>
          )}
        </>
      )}

      {/* New Folder Modal */}
      {showFolderModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '16px'
          }}
          onClick={() => setShowFolderModal(false)}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              maxWidth: '400px',
              width: '100%',
              padding: '24px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: 600, color: '#111827' }}>
              Create New Folder
            </h3>
            <form onSubmit={handleCreateFolder}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#4b5563', marginBottom: '6px' }}>
                  Folder Name
                </label>
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="e.g. Confidential Research"
                  autoFocus
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '1px solid #d1d5db',
                    fontSize: '14px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button
                  type="button"
                  onClick={() => setShowFolderModal(false)}
                  style={{
                    padding: '8px 14px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '13px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!newFolderName.trim()}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#1a73e8',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardContent;
