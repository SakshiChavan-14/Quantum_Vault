# QuantumVault - Secure Cloud Storage with Post-Quantum Cryptography

🔐 **Production-Ready Secure Cloud Storage with AES-128 Encryption + Kyber Post-Quantum Security**

## Overview

QuantumVault is a complete, production-grade secure cloud storage system featuring:

- **AES-128-Fernet Encryption** - All files encrypted at rest
- **SHA-256 Integrity Verification** - Verify files haven't been modified
- **Kyber-1024 Post-Quantum Encryption** - Protect against quantum computer threats
- **React Frontend** - Modern, responsive user interface
- **FastAPI Backend** - High-performance async API
- **Kubernetes Ready** - Scale to millions of users
- **Production Infrastructure** - Monitoring, backups, disaster recovery

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 14+ (production)

### Local Development

```bash
# Backend setup
cd QuantumValut/backend
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload

# Frontend setup (in another terminal)
cd QuantumValut/frontend
npm install
npm run dev
```

### Access
- API: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Documentation & Notes

All comprehensive documentation is organized in the [`notes/`](notes/) folder:

- **[QUANTUMVAULT_PROJECT_COMPLETE.md](notes/QUANTUMVAULT_PROJECT_COMPLETE.md)** - Complete project overview with certificate
- **[QUANTUMVAULT_RESEARCH_PAPER.md](notes/QUANTUMVAULT_RESEARCH_PAPER.md)** - Research paper & architecture deep dive
- **[QUANTUMVAULT_TECHNICAL_UNDERSTANDING_REPORT.md](notes/QUANTUMVAULT_TECHNICAL_UNDERSTANDING_REPORT.md)** - Technical report
- **[PHASE3_ENCRYPTION_COMPLETION.md](notes/PHASE3_ENCRYPTION_COMPLETION.md)** - AES-256 encryption & SHA-256 details
- **[PHASE4_KYBER_GUIDE.md](notes/PHASE4_KYBER_GUIDE.md)** - Post-quantum Kyber-1024 integration
- **[PHASE5_PRODUCTION_DEPLOYMENT.md](notes/PHASE5_PRODUCTION_DEPLOYMENT.md)** - Production infrastructure setup
- **[QUANTUMVAULT_COMPLETION_STATUS.md](notes/QUANTUMVAULT_COMPLETION_STATUS.md)** - Completion status breakdown
- **[QUANTUMVAULT_FINAL_STATUS.md](notes/QUANTUMVAULT_FINAL_STATUS.md)** - Final project status report

## Features

### Security
- End-to-end encryption (AES-128-Fernet)
- Integrity verification (SHA-256)
- Post-quantum protection (Kyber-1024)
- JWT authentication
- HttpOnly secure cookies
- User ownership verification
- HTTPS/TLS support

### Storage
- File upload/download with encryption
- Folder hierarchy management
- 5 GB quota per user
- Soft delete with recovery
- Access tracking
- File search
- Favorites

### User Experience
- Drag-and-drop upload
- Real-time search
- Responsive design
- Toast notifications
- Storage statistics
- File actions menu

## Architecture

### Backend
- **Framework:** FastAPI
- **Database:** SQLAlchemy ORM + PostgreSQL
- **Auth:** JWT + HttpOnly Cookies
- **Encryption:** Cryptography library
- **Async:** Uvicorn

### Frontend
- **Framework:** React 19
- **Build:** Vite
- **State:** Zustand + React Hooks
- **Styling:** CSS Modules
- **UI:** Lucide Icons

---

**Status:** Production Ready - Ready for deployment  
**Security Level:** Post-quantum cryptography included
