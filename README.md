# QuantumVault

> **Proof-of-Concept Secure Cloud Storage with Hybrid Post-Quantum Key Encapsulation (Kyber-1024) and Authenticated AES-256-GCM**

[![Status](https://img.shields.io/badge/Status-Prototype%20%2F%20PoC-orange)](https://github.com/sakshichavandvg-sketch/Quantum_Vault)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2F%20Python-009688)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-React%2019%20%2F%20Vite-61DAFB)](https://react.dev/)
[![Cryptography](https://img.shields.io/badge/Crypto-AES--256--GCM%20%2B%20Kyber1024-blueviolet)](https://openquantumsafe.org/)

---

## Overview

**QuantumVault** is an educational and research prototype demonstrating a hybrid cryptographic architecture for cloud file storage. It combines classical authenticated symmetric encryption with post-quantum key encapsulation to protect data encryption keys against future quantum computer harvest-now-decrypt-later attacks.

> [!WARNING]
> **Prototype Notice:** QuantumVault is an architectural demonstration and research project. It has not undergone formal third-party cryptographic auditing and should not be used in production environments or for sensitive personal data.

---

## Cryptographic Architecture

The storage engine employs a hybrid cryptographic envelope scheme:

```
[Plaintext Payload]
       │
       ├──► SHA-256 Integrity Hash ──► Stored in Database Metadata
       │
       └──► AES-256-GCM Encryption (with fresh 96-bit Nonce & 256-bit DEK)
                   │
                   └──► Encrypted Payload (.bin) ──► Local Disk Storage (`uploads/`)

[Post-Quantum Key Protection]
Recipient Kyber-1024 Public Key
       │
       ├──► Kyber-1024 Encapsulation ──► Kyber Ciphertext (Stored in DB)
       │            │
       │            └──► 256-bit Shared Secret
       │                        │
       │                        └──► HKDF-SHA256 (Context: `quantumvault-file-kek-v2`)
       │                                     │
       │                                     └──► 256-bit KEK
       │                                            │
       └──► RFC 3394 AES Key Wrap (KEK, DEK) ◄──────┘
                   │
                   └──► Wrapped DEK (Stored in DB)
```

### 1. Payload Encryption (Data at Rest)
- **Algorithm:** Authenticated AES-256-GCM via Python `cryptography` hazmat primitives.
- **Key Generation:** A unique 256-bit Data Encryption Key (DEK) and a 96-bit cryptographic nonce are generated per file using CSPRNG (`secrets.token_bytes`).
- **Legacy Compatibility:** Includes legacy fallback support for V1 files encrypted with Fernet (AES-128-CBC with HMAC-SHA256).

### 2. Post-Quantum Key Encapsulation (KEM)
- **Algorithm:** CRYSTALS-Kyber-1024 (Round 3 parameterization; precursor to standardized NIST FIPS 203 ML-KEM).
- **Function:** Kyber is used strictly as a **Key Encapsulation Mechanism (KEM)** to establish a shared secret, not for direct bulk file encryption.
- **Native Implementation:** Wraps `oqs.KeyEncapsulation` via the Open Quantum Safe (`liboqs`) C library when installed.
- **Implementation Caveat / Fallback Mode:** In environments where native `liboqs` is not installed, the service falls back to a development simulation mode using XOR masks and random byte tokens. *Simulation fallback provides zero cryptographic or quantum resistance.*

### 3. Key Wrapping & Derivation
- **KEK Derivation:** HKDF-SHA256 (RFC 5869) derives a 256-bit Key Encryption Key (KEK) from the Kyber shared secret.
- **Key Wrapping:** The DEK is wrapped using RFC 3394 AES Key Wrap with the KEK.

### 4. Integrity & Decryption Verification
- **Authenticated Decryption:** AES-256-GCM automatically verifies ciphertext integrity via its 16-byte authentication tag (`InvalidTag` check).
- **Plaintext Hash Check:** Upon decryption, a secondary constant-time SHA-256 check (`hmac.compare_digest`) verifies payload authenticity before returning bytes to the caller.

### 5. Server-Side Key Management & Trust Model
- **Trust Model:** This is a **server-managed encryption architecture**, *not* client-side zero-knowledge end-to-end encryption (E2EE). The backend receives plaintext over TLS and performs encryption and decryption server-side.
- **User Key Protection:** User Kyber secret keys are generated server-side and encrypted at rest in the database using a server-side master key (`CRYPTO_MASTER_KEY`) via Fernet.

---

## Security & Authentication

- **Authentication:** JWT access tokens and refresh tokens signed with HMAC-SHA256 (`python-jose`).
- **Session Transport:** Transmitted via `HttpOnly`, `SameSite=Lax` cookies with `Secure` flag configuration.
- **Password Security:** Salted password hashing via `bcrypt` (enforcing max 72-byte password length).
- **Access Control:** User ownership verification on file access (`file.owner_id == current_user.id`), with fail-closed generic 404 responses to mitigate user enumeration.
- **Audit Logging:** Structured database event logging for security events (login, file upload, decryption failures, integrity mismatches).

---

## Current Status & Limitations

| Component | Current Implementation | Status |
| :--- | :--- | :--- |
| **File Encryption** | AES-256-GCM + SHA-256 plaintext integrity check | Implemented |
| **PQC Algorithm** | CRYSTALS-Kyber1024 KEM (liboqs-python wrapper) | Functional (when `liboqs` is present) |
| **PQC Fallback** | Random token simulation with XOR mask | Non-cryptographic fallback (dev only) |
| **Key Wrapping** | HKDF-SHA256 + RFC 3394 AES Key Wrap | Implemented |
| **Trust Model** | Server-side cryptographic processing | Server-managed (not zero-knowledge E2EE) |
| **Storage Engine** | Local filesystem (`uploads/`) | Prototype (Local storage) |
| **Database** | SQLAlchemy 2.0 with PostgreSQL or SQLite support | Implemented |
| **Cloud / Orchestration**| Docker / Kubernetes / S3 / Redis / CDN | Planned / Unimplemented |
| **Compliance Certifications** | FIPS 140-2 / NIST SP 800-132 certifications | Unverified / Uncertified |

---

## Documentation & Notes

Supplementary design notes and research documents are archived in the [`notes/`](notes/) folder:

- **[QUANTUMVAULT_PROJECT_COMPLETE.md](notes/QUANTUMVAULT_PROJECT_COMPLETE.md)** - Project phase milestone summary
- **[QUANTUMVAULT_RESEARCH_PAPER.md](notes/QUANTUMVAULT_RESEARCH_PAPER.md)** - Research and architectural overview
- **[QUANTUMVAULT_TECHNICAL_UNDERSTANDING_REPORT.md](notes/QUANTUMVAULT_TECHNICAL_UNDERSTANDING_REPORT.md)** - Technical report
- **[PHASE3_ENCRYPTION_COMPLETION.md](notes/PHASE3_ENCRYPTION_COMPLETION.md)** - Phase 3 cryptographic implementation notes
- **[PHASE4_KYBER_GUIDE.md](notes/PHASE4_KYBER_GUIDE.md)** - Post-quantum Kyber integration notes
- **[PHASE5_PRODUCTION_DEPLOYMENT.md](notes/PHASE5_PRODUCTION_DEPLOYMENT.md)** - Target deployment architectural guide

---

## Project Structure

```
QuantumVault/
├── notes/                   # Architecture notes, reports, and phase documentation
│   ├── PHASE3_ENCRYPTION_COMPLETION.md
│   ├── PHASE4_KYBER_GUIDE.md
│   ├── PHASE5_PRODUCTION_DEPLOYMENT.md
│   ├── QUANTUMVAULT_RESEARCH_PAPER.md
│   └── ...
├── QuantumValut/
│   ├── backend/             # FastAPI backend application
│   │   ├── alembic/         # Database migrations
│   │   ├── app/
│   │   │   ├── api/v1/      # REST API endpoints (auth, files, folders, dashboard)
│   │   │   ├── core/        # Security, JWT, cookies, DB session
│   │   │   ├── models/      # SQLAlchemy ORM models
│   │   │   └── services/    # Crypto, Kyber, hashing, and file services
│   │   └── requirements.txt
│   └── frontend/            # React + Vite application
│       ├── src/             # Components, pages, hooks, Zustand stores
│       └── package.json
└── README.md
```

---

## Quick Start (Development Setup)

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (default development) or PostgreSQL 14+

### 1. Backend Setup

```bash
cd QuantumValut/backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/macOS

# Apply database migrations
alembic upgrade head

# Start development API server
uvicorn app.main:app --reload
```

> [!NOTE]
> To enable native post-quantum Kyber support, compile and install [Open Quantum Safe (liboqs)](https://github.com/open-quantum-safe/liboqs) and `liboqs-python` in your environment. Without `liboqs`, the backend operates in development simulation mode.

### 2. Frontend Setup

```bash
cd QuantumValut/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

### 3. Service Endpoints
- **Web UI:** `http://localhost:5173`
- **FastAPI API:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`

---

## Testing

Backend test suites are located in `QuantumValut/backend`:

```bash
cd QuantumValut/backend
python tests_phase2b1.py
python tests_phase2c_e2e.py
```

---

## License & Attribution

This project is licensed under the MIT License. Post-quantum cryptographic concepts are based on CRYSTALS-Kyber (NIST Post-Quantum Cryptography standardization).
