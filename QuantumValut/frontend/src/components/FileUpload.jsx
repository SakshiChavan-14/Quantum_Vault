/**
 * FileUpload Component
 * Handles file uploads with drag-and-drop support
 */

import React, { useState, useRef } from 'react';
import styles from './FileUpload.module.css';

export const FileUpload = ({ onUpload, folderId = null, disabled = false }) => {
  const fileInputRef = useRef(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [isFavorite, setIsFavorite] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file) => {
    if (file) {
      setSelectedFile(file);
      setShowModal(true);
    }
  };

  const handleInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const metadata = {
      description: description || null,
      isFavorite,
    };

    const result = await onUpload(selectedFile, metadata);

    if (result) {
      // Reset form
      setSelectedFile(null);
      setDescription('');
      setIsFavorite(false);
      setShowModal(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleCancel = () => {
    setSelectedFile(null);
    setDescription('');
    setIsFavorite(false);
    setShowModal(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <>
      {/* Upload Button */}
      <button
        className={styles.uploadButton}
        onClick={() => fileInputRef.current?.click()}
        disabled={disabled}
        title="Upload a file"
      >
        📤 Upload File
      </button>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className={styles.fileInput}
        onChange={handleInputChange}
        accept="*/*"
        disabled={disabled}
      />

      {/* Drag and drop area */}
      <div
        className={`${styles.dropZone} ${isDragActive ? styles.active : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className={styles.dropContent}>
          <p>Drag files here to upload</p>
          <small>or click the upload button</small>
        </div>
      </div>

      {/* Upload Modal */}
      {showModal && selectedFile && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <h3>Upload File</h3>

            {/* File preview */}
            <div className={styles.filePreview}>
              <div className={styles.fileIcon}>📄</div>
              <div className={styles.fileInfo}>
                <p className={styles.fileName}>{selectedFile.name}</p>
                <p className={styles.fileSize}>
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>

            {/* Description input */}
            <div className={styles.formGroup}>
              <label>Description (optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add a description for this file..."
                rows="3"
              />
            </div>

            {/* Favorite checkbox */}
            <div className={styles.formGroup}>
              <label>
                <input
                  type="checkbox"
                  checked={isFavorite}
                  onChange={(e) => setIsFavorite(e.target.checked)}
                />
                Mark as favorite
              </label>
            </div>

            {/* Actions */}
            <div className={styles.actions}>
              <button
                className={styles.cancelBtn}
                onClick={handleCancel}
              >
                Cancel
              </button>
              <button
                className={styles.uploadBtn}
                onClick={handleUpload}
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal backdrop */}
      {showModal && (
        <div className={styles.backdrop} onClick={handleCancel} />
      )}
    </>
  );
};
