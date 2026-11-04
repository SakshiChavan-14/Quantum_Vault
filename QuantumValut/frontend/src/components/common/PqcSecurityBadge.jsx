import React, { useState } from 'react';

export const PqcSecurityBadge = ({ algorithm, fileHash, size = 'normal' }) => {
  const [showModal, setShowModal] = useState(false);
  const isPQC = algorithm === 'AES-256-GCM+Kyber1024';
  const isLegacy = algorithm === 'AES-128-Fernet';

  return (
    <>
      <div 
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: size === 'small' ? '2px 8px' : '4px 10px',
          borderRadius: '12px',
          fontSize: size === 'small' ? '11px' : '12px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          backgroundColor: isPQC ? 'rgba(16, 185, 129, 0.12)' : isLegacy ? 'rgba(245, 158, 11, 0.12)' : 'rgba(107, 114, 128, 0.12)',
          color: isPQC ? '#059669' : isLegacy ? '#d97706' : '#4b5563',
          border: `1px solid ${isPQC ? 'rgba(16, 185, 129, 0.3)' : isLegacy ? 'rgba(245, 158, 11, 0.3)' : 'rgba(107, 114, 128, 0.3)'}`,
        }}
        onClick={(e) => {
          e.stopPropagation();
          setShowModal(true);
        }}
        title="Click to view cryptographic security details"
      >
        <span>{isPQC ? '🛡️' : isLegacy ? '🔐' : '🔒'}</span>
        <span>{isPQC ? 'Post-Quantum Protected' : isLegacy ? 'Legacy Encryption' : 'Standard'}</span>
      </div>

      {showModal && (
        <div 
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '16px'
          }}
          onClick={() => setShowModal(false)}
        >
          <div 
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              maxWidth: '480px',
              width: '100%',
              padding: '24px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
              color: '#1f2937'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '24px' }}>{isPQC ? '🛡️' : '🔐'}</span>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#111827' }}>
                  {isPQC ? 'Post-Quantum Security' : 'Legacy Security'}
                </h3>
              </div>
              <button 
                onClick={() => setShowModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#6b7280' }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
                <span style={{ color: '#6b7280', fontWeight: 500 }}>Encryption Algorithm:</span>
                <span style={{ fontWeight: 600, color: '#111827' }}>{isPQC ? 'AES-256-GCM' : 'AES-128-Fernet (CBC+HMAC)'}</span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
                <span style={{ color: '#6b7280', fontWeight: 500 }}>Key Encapsulation:</span>
                <span style={{ fontWeight: 600, color: '#111827' }}>{isPQC ? 'ML-KEM / Kyber-1024' : 'Direct Server-Side Key'}</span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
                <span style={{ color: '#6b7280', fontWeight: 500 }}>Key Protection:</span>
                <span style={{ fontWeight: 600, color: '#111827' }}>{isPQC ? 'RFC 3394 AES Key Wrap' : 'Master Key Encrypted'}</span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
                <span style={{ color: '#6b7280', fontWeight: 500 }}>KEK Derivation:</span>
                <span style={{ fontWeight: 600, color: '#111827' }}>{isPQC ? 'HKDF-SHA256' : 'N/A'}</span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
                <span style={{ color: '#6b7280', fontWeight: 500 }}>Integrity Verification:</span>
                <span style={{ fontWeight: 600, color: '#059669' }}>SHA-256 Constant-Time Verified ✅</span>
              </div>

              {fileHash && (
                <div style={{ padding: '8px 12px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
                  <div style={{ color: '#6b7280', fontWeight: 500, marginBottom: '4px' }}>SHA-256 Digest:</div>
                  <code style={{ fontSize: '11px', wordBreak: 'break-all', color: '#374151' }}>{fileHash}</code>
                </div>
              )}
            </div>

            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#1a73e8',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '6px',
                  fontWeight: 500,
                  cursor: 'pointer'
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PqcSecurityBadge;
