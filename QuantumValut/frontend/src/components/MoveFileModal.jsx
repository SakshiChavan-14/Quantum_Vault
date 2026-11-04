import React, { useState, useEffect } from 'react';
import { folderApi } from '../api/folderApi';
import { fileService } from '../services/fileService';
import styles from './MoveFileModal.module.css';

export const MoveFileModal = ({ file, onClose, onConfirm }) => {
  const [folders, setFolders] = useState([]);
  const [loadingFolders, setLoadingFolders] = useState(true);
  // Default to null or the opposite of current location if possible, but keep selection explicit
  const [selectedFolderId, setSelectedFolderId] = useState(undefined);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const currentFolderId = file.folder_id || null;

  useEffect(() => {
    let isMounted = true;
    const fetchFolders = async () => {
      try {
        setLoadingFolders(true);
        const data = await folderApi.getRootFolders();
        if (isMounted) {
          setFolders(data || []);
        }
      } catch (err) {
        if (isMounted) {
          setErrorMessage('Failed to load folders. Please try again.');
          console.error('Failed to load folders for move modal:', err);
        }
      } finally {
        if (isMounted) {
          setLoadingFolders(false);
        }
      }
    };

    fetchFolders();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleSelect = (folderId) => {
    setSelectedFolderId(folderId);
    setErrorMessage(null);
  };

  const handleMove = async () => {
    if (selectedFolderId === undefined) return;
    if (selectedFolderId === currentFolderId) return;

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const res = await onConfirm(file.id, selectedFolderId);
      if (res) {
        onClose();
      }
    } catch (err) {
      const msg = err.response?.data?.message || err.message || 'Failed to move file';
      setErrorMessage(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const fileIcon = fileService.getFileIcon(file.mime_type, file.file_extension);
  const isMoveDisabled =
    selectedFolderId === undefined ||
    selectedFolderId === currentFolderId ||
    isSubmitting;

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className={styles.header}>
          <h3 className={styles.headerTitle}>
            <span>📂</span> Move to folder
          </h3>
          <button
            className={styles.closeBtn}
            onClick={onClose}
            disabled={isSubmitting}
            title="Close"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className={styles.body}>
          {/* File Information Card */}
          <div className={styles.fileInfoCard}>
            <div className={styles.fileIcon}>{fileIcon}</div>
            <div className={styles.fileDetails}>
              <div className={styles.fileName} title={file.original_filename}>
                {file.original_filename}
              </div>
              <div className={styles.currentLoc}>
                Current location:{' '}
                <strong>
                  {currentFolderId
                    ? folders.find((f) => f.id === currentFolderId)?.name || 'Folder'
                    : 'My Drive (Root)'}
                </strong>
              </div>
            </div>
          </div>

          {/* Destination Selection */}
          <div className={styles.sectionLabel}>
            <span>Select Destination:</span>
            {selectedFolderId !== undefined && (
              <span style={{ fontSize: '11px', color: '#2563eb', fontWeight: 500 }}>
                Selected:{' '}
                {selectedFolderId === null
                  ? 'My Drive'
                  : folders.find((f) => f.id === selectedFolderId)?.name || 'Folder'}
              </span>
            )}
          </div>

          {loadingFolders ? (
            <div className={styles.loadingPlaceholder}>
              Loading available destinations...
            </div>
          ) : (
            <div className={styles.destinationList}>
              {/* Option: My Drive (Root) */}
              <div
                className={`${styles.destItem} ${
                  selectedFolderId === null ? styles.destItemSelected : ''
                } ${currentFolderId === null ? styles.destItemCurrent : ''}`}
                onClick={() => handleSelect(null)}
              >
                <div className={styles.destLeft}>
                  <span className={styles.destIcon}>📁</span>
                  <span className={styles.destName}>My Drive (Root)</span>
                </div>
                {currentFolderId === null ? (
                  <span className={styles.badgeCurrent}>Current</span>
                ) : selectedFolderId === null ? (
                  <span className={styles.badgeSelected}>✓</span>
                ) : null}
              </div>

              {/* Options: User Folders */}
              {folders.map((folder) => {
                const isCurrent = currentFolderId === folder.id;
                const isSelected = selectedFolderId === folder.id;
                return (
                  <div
                    key={folder.id}
                    className={`${styles.destItem} ${
                      isSelected ? styles.destItemSelected : ''
                    } ${isCurrent ? styles.destItemCurrent : ''}`}
                    onClick={() => handleSelect(folder.id)}
                  >
                    <div className={styles.destLeft}>
                      <span className={styles.destIcon}>📁</span>
                      <span className={styles.destName}>{folder.name}</span>
                    </div>
                    {isCurrent ? (
                      <span className={styles.badgeCurrent}>Current</span>
                    ) : isSelected ? (
                      <span className={styles.badgeSelected}>✓</span>
                    ) : null}
                  </div>
                );
              })}
            </div>
          )}

          {/* Error message */}
          {errorMessage && (
            <div className={styles.errorBanner}>
              <span>⚠️</span>
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className={styles.footer}>
          <button
            type="button"
            className={styles.cancelBtn}
            onClick={onClose}
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="button"
            className={styles.moveBtn}
            onClick={handleMove}
            disabled={isMoveDisabled}
          >
            {isSubmitting ? (
              <>
                <span>⏳</span> Moving...
              </>
            ) : (
              'Move File'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
