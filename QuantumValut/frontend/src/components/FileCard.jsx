/**
 * FileCard Component
 * Displays a single file with PQC security badge and actions (download, delete, rename, etc.)
 */

import React, { useState } from 'react';
import { fileService } from '../services/fileService';
import { PqcSecurityBadge } from './common/PqcSecurityBadge';
import styles from './FileCard.module.css';

export const FileCard = ({
  file,
  onDelete,
  onDownload,
  onRename,
  onToggleFavorite,
  onOpenMoveModal,
  onPreview,
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState(file.original_filename);

  const fileIcon = fileService.getFileIcon(file.mime_type, file.file_extension);
  const fileSize = fileService.formatFileSize(file.file_size);
  const createdDate = fileService.formatDate(file.created_at);

  const handleDownload = () => {
    onDownload(file.id, file.original_filename);
    setShowMenu(false);
  };

  const handlePreview = () => {
    setShowMenu(false);
    if (onPreview) {
      onPreview(file);
    }
  };

  const handleDelete = () => {
    if (window.confirm(`Delete "${file.original_filename}"?`)) {
      onDelete(file.id, file.original_filename);
      setShowMenu(false);
    }
  };

  const handleRename = async () => {
    if (newName && newName !== file.original_filename) {
      const result = await onRename(file.id, newName);
      if (result) {
        setIsRenaming(false);
      }
    } else {
      setIsRenaming(false);
    }
  };

  const handleToggleFavorite = async () => {
    await onToggleFavorite(file.id);
    setShowMenu(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setIsRenaming(false);
      setNewName(file.original_filename);
    }
  };

  return (
    <div className={styles.fileCard}>
      {/* Top Header Row */}
      <div className={styles.cardHeader}>
        <div 
          className={styles.fileIcon} 
          onClick={handlePreview}
          style={{ cursor: 'pointer' }}
          title="Click to preview file"
        >
          {fileIcon}
        </div>
        <div className={styles.topActions}>
          {file.is_favorite && (
            <button
              className={styles.favoriteBtn}
              onClick={handleToggleFavorite}
              title="Remove from favorites"
            >
              ⭐
            </button>
          )}
          <div className={styles.menu}>
            <button
              className={styles.menuBtn}
              onClick={() => setShowMenu(!showMenu)}
              title="More options"
            >
              ⋮
            </button>

            {showMenu && (
              <div className={styles.dropdown}>
                <button className={styles.menuItem} onClick={handlePreview}>
                  👁️ Open / Preview
                </button>
                <button className={styles.menuItem} onClick={handleDownload}>
                  📥 Download
                </button>
                <button
                  className={styles.menuItem}
                  onClick={() => {
                    setIsRenaming(true);
                    setShowMenu(false);
                  }}
                >
                  ✏️ Rename
                </button>
                <button className={styles.menuItem} onClick={handleToggleFavorite}>
                  {file.is_favorite ? '★ Remove favorite' : '☆ Add favorite'}
                </button>
                <button
                  className={styles.menuItem}
                  onClick={() => {
                    setShowMenu(false);
                    if (onOpenMoveModal) {
                      onOpenMoveModal(file);
                    }
                  }}
                >
                  📂 Move to folder
                </button>
                <hr className={styles.divider} />
                <button
                  className={`${styles.menuItem} ${styles.danger}`}
                  onClick={handleDelete}
                >
                  🗑️ Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Body: File Name */}
      <div className={styles.cardBody}>
        {isRenaming ? (
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onBlur={handleRename}
            onKeyDown={handleKeyDown}
            className={styles.renameInput}
            autoFocus
          />
        ) : (
          <div 
            className={styles.fileName} 
            title={`Click to preview "${file.original_filename}"`}
            onClick={handlePreview}
            style={{ cursor: 'pointer' }}
          >
            {file.original_filename}
          </div>
        )}
      </div>

      {/* Footer: Metadata & Security Badge */}
      <div className={styles.cardFooter}>
        <div className={styles.fileMeta}>
          <span>{fileSize}</span>
          <span className={styles.dotSeparator}>•</span>
          <span>{createdDate}</span>
        </div>
        <div className={styles.badgeWrapper}>
          <PqcSecurityBadge
            algorithm={file.encryption_algorithm}
            fileHash={file.file_hash}
            size="small"
          />
        </div>
      </div>

      {/* Backdrop (close menu on outside click) */}
      {showMenu && (
        <div
          className={styles.backdrop}
          onClick={() => setShowMenu(false)}
        />
      )}
    </div>
  );
};
