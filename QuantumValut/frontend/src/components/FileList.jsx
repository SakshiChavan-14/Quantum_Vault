/**
 * FileList Component
 * Displays list of files with search and pagination
 */

import React, { useState } from 'react';
import { FileCard } from './FileCard';
import { MoveFileModal } from './MoveFileModal';
import { FilePreviewModal } from './FilePreviewModal';
import styles from './FileList.module.css';

export const FileList = ({
  files,
  loading,
  error,
  page,
  totalPages,
  searchQuery,
  onSearch,
  onGoToPage,
  onUpload,
  onDelete,
  onDownload,
  onRename,
  onMove,
  onToggleFavorite,
  storageStats,
}) => {
  const [searchInput, setSearchInput] = useState(searchQuery);
  const [activeMoveFile, setActiveMoveFile] = useState(null);
  const [activePreviewFile, setActivePreviewFile] = useState(null);

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchInput(value);
    onSearch(value);
  };

  const handleClearSearch = () => {
    setSearchInput('');
    onSearch('');
  };

  const handlePrevPage = () => {
    if (page > 1) {
      onGoToPage(page - 1);
    }
  };

  const handleNextPage = () => {
    if (page < totalPages) {
      onGoToPage(page + 1);
    }
  };

  const handleConfirmMove = async (fileId, targetFolderId) => {
    if (onMove) {
      return await onMove(fileId, targetFolderId);
    }
    return null;
  };

  return (
    <div className={styles.fileList}>
      {/* Header with search and stats */}
      <div className={styles.header}>
        <div className={styles.searchSection}>
          <input
            type="text"
            placeholder="Search files..."
            value={searchInput}
            onChange={handleSearch}
            className={styles.searchInput}
          />
          {searchInput && (
            <button
              className={styles.clearBtn}
              onClick={handleClearSearch}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* Storage stats */}
        {storageStats && (
          <div className={styles.storageStats}>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Used:</span>
              <span className={styles.statValue}>
                {(storageStats.used_storage_bytes / 1024 / 1024 / 1024).toFixed(2)} GB
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Total:</span>
              <span className={styles.statValue}>
                {(storageStats.total_storage_bytes / 1024 / 1024 / 1024).toFixed(2)} GB
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Files:</span>
              <span className={styles.statValue}>
                {storageStats.file_count}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className={styles.content}>
        {loading && (
          <div className={styles.emptyState}>
            <p>Loading files...</p>
          </div>
        )}

        {error && (
          <div className={styles.errorState}>
            <p>⚠️ {error}</p>
          </div>
        )}

        {!loading && !error && files.length === 0 && (
          <div className={styles.emptyState}>
            <p>📁 No files here yet</p>
            <small>Upload files using the upload button above</small>
          </div>
        )}

        {!loading && !error && files.length > 0 && (
          <div className={styles.fileGrid}>
            {files.map((file) => (
              <FileCard
                key={file.id}
                file={file}
                onDelete={onDelete}
                onDownload={onDownload}
                onRename={onRename}
                onToggleFavorite={onToggleFavorite}
                onOpenMoveModal={(f) => setActiveMoveFile(f)}
                onPreview={(f) => setActivePreviewFile(f)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {!loading && !error && totalPages > 1 && (
        <div className={styles.pagination}>
          <button
            className={styles.pageBtn}
            onClick={handlePrevPage}
            disabled={page === 1}
          >
            ← Previous
          </button>

          <div className={styles.pageInfo}>
            Page {page} of {totalPages}
          </div>

          <button
            className={styles.pageBtn}
            onClick={handleNextPage}
            disabled={page === totalPages}
          >
            Next →
          </button>
        </div>
      )}

      {/* Move File Modal */}
      {activeMoveFile && (
        <MoveFileModal
          file={activeMoveFile}
          onClose={() => setActiveMoveFile(null)}
          onConfirm={handleConfirmMove}
        />
      )}

      {/* File Preview Modal */}
      {activePreviewFile && (
        <FilePreviewModal
          file={activePreviewFile}
          onClose={() => setActivePreviewFile(null)}
          onDownload={onDownload}
        />
      )}
    </div>
  );
};

