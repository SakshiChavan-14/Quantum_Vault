import React, { useState, useEffect } from 'react';
import mammoth from 'mammoth';
import { fileApi } from '../api/fileApi';
import { fileService } from '../services/fileService';
import { PqcSecurityBadge } from './common/PqcSecurityBadge';
import styles from './FilePreviewModal.module.css';

export const FilePreviewModal = ({ file, onClose, onDownload }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [objectUrl, setObjectUrl] = useState(null);
  const [textContent, setTextContent] = useState(null);
  const [docxHtml, setDocxHtml] = useState(null);

  const mimeType = file.mime_type || '';
  const ext = (file.file_extension || '').toLowerCase();
  const fileIcon = fileService.getFileIcon(mimeType, ext);
  const fileSize = fileService.formatFileSize(file.file_size);

  const isImage = mimeType.startsWith('image/') || ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext);
  const isPdf = mimeType === 'application/pdf' || ext === 'pdf';
  const isDocx = mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || ext === 'docx' || ext === 'doc';
  const isText = mimeType.startsWith('text/') || ['txt', 'md', 'json', 'js', 'py', 'css', 'html', 'csv', 'log', 'xml', 'ts', 'jsx', 'ini', 'yaml', 'yml'].includes(ext);
  const isAudio = mimeType.startsWith('audio/') || ['mp3', 'wav', 'ogg', 'm4a'].includes(ext);
  const isVideo = mimeType.startsWith('video/') || ['mp4', 'webm', 'mov', 'mkv'].includes(ext);

  useEffect(() => {
    let isMounted = true;
    let createdUrl = null;

    const loadContent = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fileApi.previewFile(file.id);
        const blob = new Blob([response.data], { type: mimeType || response.headers['content-type'] });

        if (!isMounted) return;

        if (isDocx) {
          const arrayBuffer = await blob.arrayBuffer();
          const result = await mammoth.convertToHtml({ arrayBuffer });
          if (isMounted) {
            setDocxHtml(result.value || '<p>Document is empty.</p>');
          }
        } else if (isText) {
          const text = await blob.text();
          if (isMounted) {
            setTextContent(text);
          }
        } else {
          createdUrl = URL.createObjectURL(blob);
          if (isMounted) {
            setObjectUrl(createdUrl);
          }
        }
      } catch (err) {
        if (isMounted) {
          console.error('Failed to load file preview:', err);
          setError('Failed to decrypt and load file preview. Please try downloading directly.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadContent();

    return () => {
      isMounted = false;
      if (createdUrl) {
        URL.revokeObjectURL(createdUrl);
      }
    };
  }, [file.id, mimeType, isDocx, isText]);

  const handleDownloadClick = () => {
    if (onDownload) {
      onDownload(file.id, file.original_filename);
    }
  };

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <span className={styles.fileIcon}>{fileIcon}</span>
            <div className={styles.fileInfo}>
              <div className={styles.fileName} title={file.original_filename}>
                {file.original_filename}
              </div>
              <div className={styles.fileMeta}>
                {fileSize} • {file.mime_type || 'Unknown type'}
              </div>
            </div>
          </div>

          <div className={styles.headerActions}>
            <PqcSecurityBadge
              algorithm={file.encryption_algorithm}
              fileHash={file.file_hash}
              size="small"
            />
            <button className={styles.downloadBtn} onClick={handleDownloadClick}>
              📥 Download
            </button>
            <button className={styles.closeBtn} onClick={onClose} title="Close">
              ✕
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className={styles.body}>
          {loading && (
            <div className={styles.loading}>
              <div className={styles.spinner} />
              <span>Decrypting and loading document view...</span>
            </div>
          )}

          {error && <div className={styles.error}>⚠️ {error}</div>}

          {!loading && !error && (
            <>
              {isDocx && docxHtml !== null && (
                <div
                  className={styles.previewDocxContainer}
                  dangerouslySetInnerHTML={{ __html: docxHtml }}
                />
              )}

              {isImage && objectUrl && (
                <img
                  src={objectUrl}
                  alt={file.original_filename}
                  className={styles.previewImage}
                />
              )}

              {isPdf && objectUrl && (
                <iframe
                  src={objectUrl}
                  title={file.original_filename}
                  className={styles.previewIframe}
                />
              )}

              {isText && textContent !== null && (
                <pre className={styles.previewCode}>{textContent}</pre>
              )}

              {isAudio && objectUrl && (
                <audio controls src={objectUrl} className={styles.previewAudio} />
              )}

              {isVideo && objectUrl && (
                <video controls src={objectUrl} className={styles.previewVideo} />
              )}

              {!isDocx && !isImage && !isPdf && !isText && !isAudio && !isVideo && (
                <div className={styles.unsupportedCard}>
                  <div className={styles.unsupportedIcon}>{fileIcon}</div>
                  <div className={styles.unsupportedTitle}>{file.original_filename}</div>
                  <div className={styles.unsupportedText}>
                    Direct browser preview is not supported for this file format ({ext.toUpperCase()}).
                  </div>
                  <button className={styles.downloadBtn} onClick={handleDownloadClick}>
                    📥 Download File to View
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FilePreviewModal;
