/**
 * useFiles Hook
 * Manages file state and operations
 * Integrates with fileService for API calls
 */

import { useState, useCallback, useEffect } from 'react';
import { fileService } from '../services/fileService';

export const useFiles = (folderId = null, pageSize = 20) => {
  // State management
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [storageStats, setStorageStats] = useState(null);
  const [recentFiles, setRecentFiles] = useState([]);

  /**
   * Load files for current folder and page
   */
  const loadFiles = useCallback(async (pageNum = 1, query = '') => {
    try {
      setLoading(true);
      setError(null);

      let data;
      if (query) {
        data = await fileService.searchFiles(query, pageNum, pageSize);
      } else {
        data = await fileService.listFolderFiles(folderId, pageNum, pageSize);
      }

      setFiles(data.items || []);
      setTotalFiles(data.total || 0);
      setTotalPages(data.total_pages || 0);
      setPage(pageNum);
    } catch (err) {
      setError(err.message);
      console.error('Load files error:', err);
    } finally {
      setLoading(false);
    }
  }, [folderId, pageSize]);

  /**
   * Load storage statistics
   */
  const loadStorageStats = useCallback(async () => {
    try {
      const stats = await fileService.getStorageStats();
      setStorageStats(stats);
    } catch (err) {
      console.error('Load storage stats error:', err);
    }
  }, []);

  /**
   * Load recent files
   */
  const loadRecentFiles = useCallback(async () => {
    try {
      const recent = await fileService.getRecentFiles(10);
      setRecentFiles(recent);
    } catch (err) {
      console.error('Load recent files error:', err);
    }
  }, []);

  /**
   * Upload a file
   */
  const uploadFile = useCallback(async (file, metadata = {}) => {
    const result = await fileService.uploadFile(file, folderId, metadata);
    if (result) {
      // Refresh file list
      await loadFiles(1, searchQuery);
      // Refresh storage stats
      await loadStorageStats();
    }
    return result;
  }, [folderId, loadFiles, loadStorageStats, searchQuery]);

  /**
   * Download a file
   */
  const downloadFile = useCallback(async (fileId, filename) => {
    await fileService.downloadFile(fileId, filename);
  }, []);

  /**
   * Delete a file
   */
  const deleteFile = useCallback(async (fileId, filename) => {
    const success = await fileService.deleteFile(fileId, filename);
    if (success) {
      // Refresh file list
      await loadFiles(page, searchQuery);
      // Refresh storage stats
      await loadStorageStats();
    }
    return success;
  }, [page, loadFiles, loadStorageStats, searchQuery]);

  /**
   * Rename a file
   */
  const renameFile = useCallback(async (fileId, newFilename) => {
    const result = await fileService.renameFile(fileId, newFilename);
    if (result) {
      // Update in local state
      setFiles(files.map(f => f.id === fileId ? result : f));
    }
    return result;
  }, [files]);

  /**
   * Move a file
   */
  const moveFile = useCallback(async (fileId, newFolderId) => {
    const result = await fileService.moveFile(fileId, newFolderId);
    if (result) {
      // Remove from current list if moving to different folder
      if (newFolderId !== folderId) {
        setFiles(files.filter(f => f.id !== fileId));
        setTotalFiles(Math.max(0, totalFiles - 1));
      }
    }
    return result;
  }, [files, folderId, totalFiles]);

  /**
   * Toggle file favorite status
   */
  const toggleFavorite = useCallback(async (fileId) => {
    const result = await fileService.toggleFavorite(fileId);
    if (result) {
      // Update in local state
      setFiles(files.map(f => f.id === fileId ? result : f));
    }
    return result;
  }, [files]);

  /**
   * Search files
   */
  const search = useCallback(async (query) => {
    setSearchQuery(query);
    if (query.trim()) {
      await loadFiles(1, query);
    } else {
      await loadFiles(1, '');
    }
  }, [loadFiles]);

  /**
   * Clear search
   */
  const clearSearch = useCallback(async () => {
    setSearchQuery('');
    await loadFiles(1, '');
  }, [loadFiles]);

  /**
   * Go to page
   */
  const goToPage = useCallback(async (pageNum) => {
    await loadFiles(pageNum, searchQuery);
  }, [loadFiles, searchQuery]);

  /**
   * Restore deleted file
   */
  const restoreFile = useCallback(async (fileId, filename) => {
    const result = await fileService.restoreFile(fileId, filename);
    if (result) {
      await loadFiles(page, searchQuery);
      await loadStorageStats();
    }
    return result;
  }, [page, loadFiles, loadStorageStats, searchQuery]);

  /**
   * Refresh all data
   */
  const refresh = useCallback(async () => {
    await loadFiles(1, '');
    await loadStorageStats();
    await loadRecentFiles();
  }, [loadFiles, loadStorageStats, loadRecentFiles]);

  // Load initial data on mount
  useEffect(() => {
    loadFiles(1);
    loadStorageStats();
    loadRecentFiles();
  }, [folderId]);

  return {
    // State
    files,
    loading,
    error,
    page,
    totalPages,
    totalFiles,
    searchQuery,
    storageStats,
    recentFiles,

    // Actions
    uploadFile,
    downloadFile,
    deleteFile,
    renameFile,
    moveFile,
    toggleFavorite,
    search,
    clearSearch,
    goToPage,
    restoreFile,
    refresh,

    // Utilities
    formatFileSize: fileService.formatFileSize,
    getFileIcon: fileService.getFileIcon,
    formatDate: fileService.formatDate,
  };
};
