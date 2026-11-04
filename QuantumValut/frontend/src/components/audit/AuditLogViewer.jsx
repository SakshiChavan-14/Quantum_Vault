import React, { useState, useEffect } from 'react';
import { auditApi } from '../../api/auditApi';

const CATEGORIES = ['ALL', 'AUTH', 'FILE', 'CRYPTO', 'SECURITY', 'SYSTEM'];
const STATUSES = ['ALL', 'SUCCESS', 'FAILURE', 'WARNING', 'INFO'];

export const AuditLogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedLog, setSelectedLog] = useState(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = { limit: 50 };
      if (categoryFilter !== 'ALL') params.category = categoryFilter;
      if (statusFilter !== 'ALL') params.status = statusFilter;
      
      const data = await auditApi.getMyAuditLogs(params);
      setLogs(Array.isArray(data) ? data : (data.logs || []));
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
      setError('Unable to load audit logs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [categoryFilter, statusFilter]);

  const getCategoryColor = (category) => {
    switch (category) {
      case 'AUTH': return { bg: 'rgba(37, 99, 235, 0.1)', text: '#2563eb', border: 'rgba(37, 99, 235, 0.3)' };
      case 'FILE': return { bg: 'rgba(5, 150, 105, 0.1)', text: '#059669', border: 'rgba(5, 150, 105, 0.3)' };
      case 'CRYPTO': return { bg: 'rgba(124, 58, 237, 0.1)', text: '#7c3aed', border: 'rgba(124, 58, 237, 0.3)' };
      case 'SECURITY': return { bg: 'rgba(220, 38, 38, 0.1)', text: '#dc2626', border: 'rgba(220, 38, 38, 0.3)' };
      case 'SYSTEM': default: return { bg: 'rgba(107, 114, 128, 0.1)', text: '#4b5563', border: 'rgba(107, 114, 128, 0.3)' };
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'SUCCESS':
        return <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#059669' }}>SUCCESS</span>;
      case 'FAILURE':
        return <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#dc2626' }}>FAILURE</span>;
      case 'WARNING':
        return <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#d97706' }}>WARNING</span>;
      case 'INFO': default:
        return <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#2563eb' }}>INFO</span>;
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#111827', margin: '0 0 4px 0' }}>
            🛡️ Security & Operational Audit Log
          </h2>
          <p style={{ fontSize: '13px', color: '#6b7280', margin: 0 }}>
            Real-time, cryptographically verified record of all security, file, and authentication events.
          </p>
        </div>

        <button 
          onClick={fetchLogs}
          style={{
            padding: '8px 14px',
            backgroundColor: '#ffffff',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          🔄 Refresh
        </button>
      </div>

      {/* Filters Bar */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '20px', flexWrap: 'wrap', alignItems: 'center', backgroundColor: '#f9fafb', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#4b5563' }}>Category:</span>
          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
            {CATEGORIES.map(cat => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '16px',
                  fontSize: '11px',
                  fontWeight: 600,
                  border: 'none',
                  cursor: 'pointer',
                  backgroundColor: categoryFilter === cat ? '#1a73e8' : '#e5e7eb',
                  color: categoryFilter === cat ? '#ffffff' : '#4b5563',
                  transition: 'all 0.15s ease'
                }}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: 'auto' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#4b5563' }}>Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '4px 8px',
              borderRadius: '6px',
              border: '1px solid #d1d5db',
              fontSize: '12px',
              backgroundColor: '#ffffff'
            }}
          >
            {STATUSES.map(stat => (
              <option key={stat} value={stat}>{stat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px', color: '#6b7280' }}>
          <p>Loading security audit logs...</p>
        </div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '48px', color: '#dc2626' }}>
          <p>{error}</p>
          <button onClick={fetchLogs} style={{ padding: '6px 12px', marginTop: '8px', cursor: 'pointer' }}>Retry</button>
        </div>
      ) : logs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '48px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>No audit events matching the selected filters.</p>
        </div>
      ) : (
        <div style={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb', color: '#6b7280', fontWeight: 600 }}>
                <th style={{ padding: '12px 16px' }}>Timestamp</th>
                <th style={{ padding: '12px 16px' }}>Category</th>
                <th style={{ padding: '12px 16px' }}>Event</th>
                <th style={{ padding: '12px 16px' }}>Status</th>
                <th style={{ padding: '12px 16px' }}>Message</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => {
                const catStyle = getCategoryColor(log.event_category);
                return (
                  <tr 
                    key={log.id} 
                    style={{ borderBottom: '1px solid #f3f4f6', transition: 'background-color 0.15s ease' }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fafafa'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <td style={{ padding: '12px 16px', color: '#6b7280', whiteSpace: 'nowrap' }}>
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: 600,
                        backgroundColor: catStyle.bg,
                        color: catStyle.text,
                        border: `1px solid ${catStyle.border}`
                      }}>
                        {log.event_category}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', fontWeight: 600, color: '#111827' }}>
                      {log.event_type}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      {getStatusBadge(log.status)}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#374151', maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {log.message}
                    </td>
                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                      {log.metadata_json && (
                        <button
                          onClick={() => setSelectedLog(log)}
                          style={{
                            padding: '4px 8px',
                            fontSize: '11px',
                            backgroundColor: '#f3f4f6',
                            border: '1px solid #d1d5db',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            color: '#374151'
                          }}
                        >
                          Details
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Details Modal */}
      {selectedLog && (
        <div 
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '16px'
          }}
          onClick={() => setSelectedLog(null)}
        >
          <div 
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              maxWidth: '520px',
              width: '100%',
              padding: '24px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#111827' }}>
                Audit Event Metadata
              </h3>
              <button 
                onClick={() => setSelectedLog(null)}
                style={{ background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer', color: '#6b7280' }}
              >
                ✕
              </button>
            </div>

            <div style={{ marginBottom: '12px', fontSize: '13px' }}>
              <div><strong>Event:</strong> {selectedLog.event_type}</div>
              <div><strong>Category:</strong> {selectedLog.event_category}</div>
              <div><strong>Status:</strong> {selectedLog.status}</div>
              <div><strong>Message:</strong> {selectedLog.message}</div>
            </div>

            <div style={{ backgroundColor: '#f8fafc', padding: '12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748b', marginBottom: '6px' }}>
                SANITIZED METADATA (NO SECRETS):
              </div>
              <pre style={{ margin: 0, fontSize: '12px', fontFamily: 'monospace', color: '#334155', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                {(() => {
                  try {
                    return JSON.stringify(JSON.parse(selectedLog.metadata_json), null, 2);
                  } catch {
                    return selectedLog.metadata_json;
                  }
                })()}
              </pre>
            </div>

            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setSelectedLog(null)}
                style={{
                  padding: '6px 14px',
                  backgroundColor: '#1a73e8',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditLogViewer;
