# QuantumVault — Developer Technical Understanding Report

Welcome to the comprehensive technical walkthrough of **QuantumVault**.

This document is designed as an architectural breakdown and mentoring manual. It explains every single piece of technology in your system, how they connect, why they were chosen, and how your cryptographic pipeline operates from the ground up.

---

# Section 1: Complete Technology Stack

### Technology Summary Table

| Technology | Category | What it is | Why we use it in QuantumVault | Where it is used |
| :--- | :--- | :--- | :--- | :--- |
| **React (v19)** | Frontend | UI component library | Declarative, component-driven reactive user interface | Entire frontend client (`frontend/src/`) |
| **Vite (v8)** | Frontend | Modern frontend build tool | Instant hot-module replacement and optimized asset bundling | Frontend development server & production builds |
| **React Router (v7)** | Frontend | Client-side routing library | Seamless navigation between Dashboard, My Drive, Starred, and Audit views without full page reloads | `frontend/src/routes/` |
| **Axios** | Frontend | Promise-based HTTP client | Configured instance with automatic credentials/cookie transport for API requests | `frontend/src/api/axios.js` and all API modules |
| **TanStack React Query (v5)**| Frontend | Async server-state manager | Caches, invalidates, and synchronizes server state for dashboard stats, storage, and activity feeds | `frontend/src/hooks/useDashboard.js` |
| **Zustand (v5)** | Frontend | Lightweight client state store | Manages active sidebar view and UI selection state | `frontend/src/store/sidebarStore.js` |
| **Formik & Yup** | Frontend | Form management & schema validation | Handles form state, client-side input validation (e.g., passwords, emails) and errors | `frontend/src/validation/` & auth forms |
| **React Hot Toast** | Frontend | Notification toast library | Non-intrusive status alerts for file uploads, renames, moves, and deletions | Across UI interaction handlers |
| **Python (3.11+)** | Backend | Core programming language | High developer productivity, rich cryptographic support, and clean asynchronous syntax | Entire backend system (`backend/app/`) |
| **FastAPI** | Backend | High-performance Python web framework | Automatic OpenAPI documentation, Pydantic type safety, and async REST route handlers | `backend/app/main.py` & `backend/app/api/` |
| **Uvicorn** | Backend | Lightning-fast ASGI web server | Executes FastAPI backend application on HTTP/1.1 and WebSockets | Application runner & CLI reloading process |
| **SQLAlchemy (v2.0)** | Backend | Python SQL Toolkit and ORM | Object-Relational Mapping to translate Python classes into MySQL tables and queries | `backend/app/models/` & `backend/app/repositories/` |
| **Pydantic (v2) & Settings** | Backend | Data parsing & validation engine | Validates incoming JSON bodies, serializes HTTP responses, and validates `.env` settings | `backend/app/schemas/` & `backend/app/core/config.py` |
| **PyMySQL** | Backend | Pure-Python MySQL client driver | Connects SQLAlchemy engine to the running MySQL database service | Database connection string driver |
| **Alembic** | Backend | Database schema migration tool | Tracks schema versions and executes incremental SQL schema upgrades | `backend/alembic/` & `alembic_version` table |
| **cryptography** | Security | Standard cryptographic library | Core primitives for AES-256-GCM, HKDF-SHA256, Fernet, and AES Key Wrap (RFC 3394) | `backend/app/services/pqc_crypto_service.py` |
| **bcrypt & Passlib** | Security | Slow password hashing framework | Securely hashes and salts user passwords using adaptive work factor | `backend/app/services/auth_service.py` |
| **python-jose** | Security | JavaScript Object Signing & Encryption | Generates, signs, and decodes JWT access tokens | `backend/app/services/auth_service.py` |
| **Loguru** | Backend | Structured logging framework | Centralized, formatted, thread-safe application and security event logging | `backend/app/core/logging.py` & services |
| **MySQL** | Database | Relational Database Management System | Persistent, ACID-compliant storage for users, files, folders, and audit logs | Port 3306 storage backend |
| **AES-256-GCM** | Security | Authenticated symmetric encryption | High-speed, authenticated payload encryption for files on disk | `backend/app/services/pqc_crypto_service.py` |
| **CRYSTALS-Kyber1024** | Security | Post-Quantum Key Encapsulation (KEM) | Quantum-resistant secret exchange protecting symmetric file keys against quantum attacks | `backend/app/services/kyber_service.py` |
| **HKDF-SHA256** | Security | HMAC-based Key Derivation Function | Expands the Kyber shared secret into a cryptographically strong Key Encryption Key (KEK) | `backend/app/services/pqc_crypto_service.py` |
| **AES Key Wrap (RFC 3394)**| Security | NIST-approved key wrapping cipher | Encapsulates the 256-bit DEK under the derived KEK with tamper detection | `backend/app/services/pqc_crypto_service.py` |
| **Master Key (Fernet)** | Security | Envelope server-side key protection | Encrypts the user's sensitive Kyber secret key before saving it in MySQL | `backend/app/services/key_protection_service.py` |

---

### In-Depth Technology Breakdown

#### 1. React
* **What is it?** A declarative JavaScript library for building component-based user interfaces.
* **Why we use it in QuantumVault:** It breaks the UI into reusable components (`FileCard`, `FileList`, `MoveFileModal`, `ActivityFeed`), efficiently updating only the modified DOM elements when state changes.
* **Where it is used:** The entire `frontend/src/` directory.
* **What happens internally:** React maintains a Virtual DOM in memory. When a state change occurs (e.g., a file is moved), React computes the diff between virtual trees and applies the minimal set of changes to the real browser DOM.
* **What would happen without it:** We would have to manually manipulate the DOM using vanilla JavaScript (`document.getElementById`), leading to spaghetti code and synchronization bugs between UI and state.

#### 2. Vite
* **What is it?** A next-generation frontend build tool and development server powered by native ES modules and Rollup.
* **Why we use it in QuantumVault:** It provides sub-second server startup, instant Hot Module Replacement (HMR), and builds optimized, minified production JavaScript/CSS bundles.
* **Where it is used:** `frontend/vite.config.js`, `package.json` scripts.
* **What happens internally:** In development, Vite serves source code over native browser ES imports without bundling. For production (`npm run build`), it bundles and tree-shakes assets into optimized static chunks in `frontend/dist/`.
* **What would happen without it:** We would rely on older bundlers like Webpack, which take minutes to recompile on every change during development.

#### 3. FastAPI
* **What is it?** A modern, high-performance web framework for building APIs with Python based on standard Python type hints.
* **Why we use it in QuantumVault:** It automatically validates request data using Pydantic, generates interactive OpenAPI documentation (`/api/v1/openapi.json`), and provides asynchronous request handling.
* **Where it is used:** `backend/app/main.py` and all routers under `backend/app/api/v1/`.
* **What happens internally:** FastAPI inspects route parameter types and dependencies. When an HTTP request arrives, it passes the payload through Pydantic validators, executes dependencies (such as `get_current_active_user`), runs the route handler, and serializes the return value to JSON.
* **What would happen without it:** We would have to write hundreds of lines of boilerplate code to parse JSON, validate types, check headers, and format errors.

#### 4. Uvicorn
* **What is it?** A lightning-fast ASGI (Asynchronous Server Gateway Interface) server implementation for Python based on `uvloop` and `httptools`.
* **Why we use it in QuantumVault:** FastAPI requires an ASGI server to listen on network sockets, accept incoming HTTP/TCP connections, and execute the Python application.
* **Where it is used:** Started via CLI (`uvicorn app.main:app --reload`) or `backend/app/main.py`.
* **What happens internally:** Uvicorn binds to `0.0.0.0:8000`, receives incoming TCP network packets, parses HTTP/1.1 requests, transforms them into standardized ASGI scope/receive/send dictionaries, and hands them to FastAPI.
* **What would happen without it:** FastAPI is just an application callable; without an ASGI web server like Uvicorn, it cannot listen on a network port or accept HTTP connections.

#### 5. SQLAlchemy (v2.0)
* **What is it?** The industry-standard Python SQL toolkit and Object-Relational Mapper (ORM).
* **Why we use it in QuantumVault:** It allows developers to define database schemas as clean Python classes (`User`, `File`, `Folder`, `AuditLog`) and execute complex queries without writing raw SQL.
* **Where it is used:** `backend/app/models/`, `backend/app/repositories/`, `backend/app/core/database.py`.
* **What happens internally:** SQLAlchemy translates Python method calls (`db.query(File).filter(...)`) into parameterized SQL statements (`SELECT files.* FROM files WHERE ...`), executes them against MySQL via PyMySQL, and converts the resulting SQL rows into Python object instances.
* **What would happen without it:** We would have to write raw SQL strings, manually handle connection pooling, and map column tuples to dictionaries, exposing the app to SQL injection risks.

#### 6. Pydantic (v2)
* **What is it?** A data validation and settings management library based on Python type annotations.
* **Why we use it in QuantumVault:** It enforces strict type contracts for API request payloads and response bodies (e.g. `FileMoveRequest`, `DashboardActivityResponse`).
* **Where it is used:** `backend/app/schemas/` and `backend/app/core/config.py`.
* **What happens internally:** Pydantic compiles type schemas down to Rust (`pydantic-core`). When data enters the system, Pydantic parses values, validates constraints (e.g. string lengths, UUID formats, email formats), and coerces datetimes. If validation fails, it raises structured errors before business logic runs.
* **What would happen without it:** Invalid or malicious data types could reach backend services, causing unhandled runtime crashes or database corruption.

#### 7. bcrypt & Passlib
* **What is it?** A password hashing function designed by Niels Provos and David Mazières based on the Blowfish cipher.
* **Why we use it in QuantumVault:** It is an intentionally slow, adaptive, salted one-way hashing algorithm that protects user passwords against offline brute-force and dictionary attacks.
* **Where it is used:** `backend/app/services/auth_service.py` for user registration and password verification.
* **What happens internally:** bcrypt generates a cryptographically secure 128-bit random salt, combines it with the user's password, and runs $2^{\text{cost}}$ (e.g. $2^{12} = 4096$) iterations of key expansion before producing the final 60-character modular crypt format string.
* **What would happen without it:** If passwords were stored in plaintext or fast hashes (like MD5 or plain SHA-256), a database leak would immediately compromise all user accounts within seconds using rainbow tables.

#### 8. Cryptography (Python Library)
* **What is it?** The standard low-level cryptography library for Python providing both high-level recipes and hazardous materials (hazmat) primitives.
* **Why we use it in QuantumVault:** It provides high-speed C-bindings for AES-256-GCM, HKDF-SHA256, AES Key Wrap (RFC 3394), and Fernet envelope encryption.
* **Where it is used:** `backend/app/services/pqc_crypto_service.py` and `backend/app/services/key_protection_service.py`.
* **What happens internally:** It calls compiled OpenSSL/C cryptographic primitives with hardware acceleration (such as Intel AES-NI) for maximum throughput and constant-time execution (preventing timing attacks).
* **What would happen without it:** Writing custom cryptographic ciphers in pure Python is dangerously vulnerable to side-channel timing attacks and is orders of magnitude slower.

#### 9. Loguru
* **What is it?** An elegant, thread-safe Python logging framework.
* **Why we use it in QuantumVault:** It provides structured, colorized, informative log outputs with automatic traceback formatting, log rotation, and timestamps.
* **Where it is used:** `backend/app/core/logging.py` and throughout backend services.
* **What happens internally:** It intercepts standard Python `logging` handlers and routes messages through a thread-safe sink, outputting formatted logs to both stdout and persistent log files (`backend/logs/app.log`).
* **What would happen without it:** Standard `print` statements lack timestamps, severity levels (INFO/ERROR/WARN), contextual stack traces, and automatic persistence.

---

# Section 2: Setup Process from Scratch

### Backend Setup Step-by-Step

```text
Host Machine (Windows/Linux)
       ↓
Install Python 3.11+
       ↓
python -m venv venv  (Create isolated virtual environment)
       ↓
.\venv\Scripts\activate  (Activate virtual environment)
       ↓
pip install -r requirements.txt  (Install locked dependencies)
       ↓
Configure .env file  (Set DATABASE_URL & CRYPTO_MASTER_KEY)
       ↓
alembic upgrade head  (Apply schema to MySQL database)
       ↓
uvicorn app.main:app --reload  (Start backend server on port 8000)
```

#### What is a Python Virtual Environment?
A virtual environment is a self-contained directory tree that contains a specific Python interpreter and isolated set of installed libraries.

#### Why do we use `python -m venv venv`?
Without a virtual environment, `pip install` installs packages globally across the entire operating system. If another project needs `fastapi==0.90` and QuantumVault needs `fastapi==0.139`, they would collide and break. `python -m venv venv` creates an isolated sandbox named `venv` inside the project.

#### What does `venv\Scripts\activate` do?
It temporarily modifies the current terminal session's `PATH` environment variable so that typing `python` or `pip` points directly to `QuantumVault\backend\venv\Scripts\python.exe` instead of the global system Python.

#### What is `requirements.txt`?
It is a manifest listing all backend dependencies and their exact pinned versions (e.g. `fastapi==0.139.0`, `SQLAlchemy==2.0.51`, `cryptography==49.0.0`). Running `pip install -r requirements.txt` reads this file and installs the exact required dependencies into the active virtual environment.

---

### Frontend Setup Step-by-Step

```text
Install Node.js (v18+ / v20+) & npm
       ↓
cd frontend
       ↓
npm install  (Reads package.json and builds node_modules)
       ↓
npm run dev  (Starts local Vite HMR server on port 5173)
       ↓
npm run build  (Compiles & minifies production assets to dist/)
```

* **`node_modules`:** A local directory containing the source code of all JavaScript dependencies listed in `package.json` (such as React, React Router, Axios, Zustand).
* **`npm run dev`:** Starts Vite's local development server at `http://localhost:5173` with instant Hot Module Replacement (code changes reflect in the browser without a full reload).
* **`npm run build`:** Executes `vite build`, running the Rollup bundler to compile JSX into minified JavaScript, generate CSS bundles, and optimize HTML in `frontend/dist/`.

---

### Database & Migrations (MySQL & Alembic)

#### Why MySQL?
QuantumVault requires a relational, ACID-compliant database with strong foreign key constraints (cascading deletes, unique indexes, transactional integrity) to ensure that files, folders, and ownership records never become orphaned or inconsistent.

#### What is Alembic?
Alembic is SQLAlchemy's database migration tool. As your application evolves and you add columns (like `kyber_public_key` or `encrypted_dek`), Alembic generates incremental versioned migration scripts in `backend/alembic/versions/`. Running `alembic upgrade head` applies these schema updates to the live MySQL database without wiping existing data.

---

# Section 3: Complete Project Architecture

### Architecture Diagram

```
                             USER / BROWSER
                                   │
                                   │ HTTPS / HTTP
                                   ▼
                    React Single Page Application (SPA)
             [ Pages ── Hooks ── Zustand ── Axios Client ]
                                   │
                                   │ REST API (JSON + HttpOnly Cookies)
                                   ▼
                     FastAPI Application (Uvicorn)
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
          API Routers        Middleware        Dependencies
        (/files, /auth,    (CORS, Logging)   (Auth / DB Session)
          /dashboard)              │                  │
                │                  └─────────┬────────┘
                ▼                            ▼
         Service Layer  ◄─────────────► Security Layer
      (FileService, AuthService,      (PQC, AES-GCM, Kyber,
       DashboardService, etc.)        KeyProtection, Hash)
                │                            │
                ▼                            │
        Repository Layer                     │
      (FileRepo, UserRepo,                   │
       FolderRepo, AuditRepo)                │
                │                            │
                ▼                            ▼
           SQLAlchemy ORM            Encrypted Storage
                │                   (Disk /uploads/ directory)
                ▼
          MySQL Database
```

---

### Layer Responsibilities Explained

1. **Frontend (React Client):** Renders UI views, captures user actions (clicks, uploads, folder selections), manages local client state, and dispatches HTTP requests via Axios.
2. **API Router (`app/api/v1/`):** The HTTP interface. Defines URL paths (`POST /files/upload`, `PATCH /files/{id}/move`), validates incoming HTTP request bodies against Pydantic schemas, and extracts user session tokens. It contains **zero business logic**.
3. **Service Layer (`app/services/`):** The core business and logic engine. Coordinates file hashing, symmetric encryption, post-quantum key encapsulation, folder validation, and audit logging.
4. **Repository Layer (`app/repositories/`):** The database access abstraction. Encapsulates all SQLAlchemy queries (`select()`, `filter()`, `update()`, `commit()`). Services never write raw SQL queries directly.
5. **Database Models (`app/models/`):** Python ORM classes (`User`, `File`, `Folder`, `AuditLog`) mapped directly to MySQL database tables using SQLAlchemy declarative mixins.
6. **MySQL Database:** The physical persistent storage on disk storing structured tabular data.

---

### Life of a Request: The Upload Flow

```text
User selects file & clicks "Upload" in browser
                     ↓
React Component (`FileUpload.jsx`)
                     ↓
React Hook (`useFiles.js`)
                     ↓
Frontend Service (`fileService.js`)
                     ↓
Axios Client (`fileApi.js`) dispatches POST multipart/form-data
                     ↓
FastAPI Router (`app/api/v1/files/router.py`) receives request & verifies JWT cookie
                     ↓
FileService (`app/services/file_service.py`):
  1. Computes SHA-256 integrity hash
  2. Generates random 256-bit DEK & 96-bit GCM Nonce
  3. Encrypts payload with AES-256-GCM
  4. Encapsulates shared secret with User Kyber-1024 Public Key
  5. Derives KEK via HKDF-SHA256
  6. Wraps DEK with AES Key Wrap (RFC 3394)
  7. Writes ciphertext file to `uploads/<user_id>/<file_id>.enc`
                     ↓
FileRepository (`app/repositories/file_repository.py`) writes file record to MySQL
                     ↓
AuditLogService records `FILE_UPLOAD_SUCCESS` in MySQL
                     ↓
FastAPI returns HTTP 201 Created with FileResponse JSON
                     ↓
React updates state & displays success toast
```

---

# Section 4: Password Hashing (bcrypt)

```text
Plaintext Password: "MySecretPassword2026!"
                   ↓
Generate Random 128-bit Salt: "$2b$12$e8kP9X... (unique per user)"
                   ↓
bcrypt Hash Function (4096 rounds of key expansion)
                   ↓
Stored Hash in MySQL: "$2b$12$e8kP9X1mZ7u3Q5v8W2y0ueN4K6J8L1M3O5P7Q9R1S3T5U7V9W1X2Y"
```

### Password Hashing Concepts Explained

* **What is a Password Hash?** A mathematical one-way transformation that converts an input string into a fixed-length fingerprint that cannot be reversed.
* **Why don't we encrypt passwords instead?** Encryption is **two-way** (reversible with a key). If the encryption key is leaked, all user passwords across the entire system are compromised simultaneously. Hashing is **one-way** (irreversible).
* **Why don't we store passwords in plaintext?** If the database is breached, plaintext passwords allow attackers to immediately compromise every account and reuse them across other websites.
* **What is a Salt?** A cryptographically random string generated uniquely for every user and appended to the password before hashing. It prevents attackers from using precomputed "rainbow tables" to crack common passwords.
* **What is stored in MySQL?** The combined string containing the algorithm version, cost factor, salt, and hash (e.g. `$2b$12$...`).
* **Can the original password be recovered from the hash?** **No.** It is mathematically infeasible to reverse bcrypt. Verification works by hashing the incoming login password with the *same salt and cost factor* and comparing the results in constant time.

---

# Section 5: SHA-256 File Integrity

```text
Original Plaintext File (Document.pdf)
                 │
                 ▼
        SHA-256 Hash Algorithm
                 │
                 ▼
64-character Hex Digest: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
```

### File Hashing Concepts Explained

* **What is SHA-256?** Secure Hash Algorithm 256-bit: A cryptographic hash function that takes input of any size and produces a unique 256-bit (32-byte / 64 hex characters) digest.
* **Why do we create a file hash?** To ensure **data integrity**. If even a single bit in a 10 GB file is corrupted on disk or modified by an attacker, the SHA-256 hash completely changes (the *avalanche effect*).
* **How is it stored?** In the `files.file_hash` column in MySQL as a 64-character hexadecimal string.
* **How integrity verification works on download:**
  1. The encrypted file is decrypted back to plaintext.
  2. The backend recomputes the SHA-256 hash over the decrypted bytes.
  3. It compares `hmac.compare_digest(recalculated_hash, file.file_hash)`.
  4. If they match, the file is authentic. If they differ, the backend aborts with `FileIntegrityCompromised` and deletes the plaintext from memory.
* **Is SHA-256 file encryption?** **No.** Hashing is destructive and irreversible. You cannot reconstruct a file from its hash.

---

# Section 6: File Encryption (AES-256-GCM)

```text
Original File Plaintext (e.g. 50 MB PDF)
                   │
  ┌────────────────┴────────────────┐
  ▼                                 ▼
Generate Random 256-bit DEK    Generate Random 96-bit Nonce
(32 cryptographically random    (12 cryptographically random
 bytes unique to this file)     bytes unique to this encryption)
  │                                 │
  └────────────────┬────────────────┘
                   ▼
       AES-256-GCM Cipher Engine
                   │
                   ▼
Encrypted Ciphertext Payload + 128-bit Authentication Tag
       (Stored on disk as `<file_id>.enc`)
```

### Symmetric Encryption Concepts Explained

* **What is AES?** Advanced Encryption Standard: The gold-standard symmetric block cipher established by NIST.
* **What does 256 mean?** The cryptographic key length is 256 bits ($2^{256}$ possible combinations). It is considered secure against brute-force attacks.
* **What is GCM?** Galois/Counter Mode: An Authenticated Encryption with Associated Data (AEAD) mode that provides both **confidentiality** (hiding the data) and **authenticity/integrity** (detecting any tampering with ciphertext via a 16-byte authentication tag).
* **What is a Nonce?** "Number used ONCE". A 96-bit (12-byte) initialization vector.
* **Why must the nonce be unique?** In AES-GCM, reusing the same key and nonce pair to encrypt two different files completely breaks the authenticity guarantees and allows attackers to recover plaintext. QuantumVault generates a fresh `secrets.token_bytes(12)` nonce for every file upload.
* **Plaintext vs Ciphertext:** Plaintext is the original readable data; Ciphertext is the unreadable encrypted byte sequence.

---

# Section 7: Post-Quantum Cryptography (PQC) & CRYSTALS-Kyber

```
               THE QUANTUM THREAT
   Traditional Public-Key (RSA / ECC / DH)
                      │
   Vulnerable to Shor's Algorithm on Future
         Fault-Tolerant Quantum Computers
                      │
                      ▼
         POST-QUANTUM CRYPTOGRAPHY (PQC)
       Lattice-Based Math (Learning With Errors)
                      │
                      ▼
        CRYSTALS-Kyber1024 (NIST FIPS 203)
```

### Post-Quantum Cryptography Explained

* **What problem does PQC solve?** Future large-scale quantum computers running **Shor's Algorithm** will easily solve the integer factorization (RSA) and discrete logarithm (ECC/ECDSA) mathematical problems, rendering traditional public-key algorithms insecure.
* **Why is AES-256 still safe?** Quantum computers running **Grover's Algorithm** only achieve a quadratic speedup against symmetric ciphers. A 256-bit AES key provides 128 bits of post-quantum security, which remains computationally infeasible to break.
* **What is CRYSTALS-Kyber?** A lattice-based Key Encapsulation Mechanism (KEM) selected by NIST as the post-quantum standard (FIPS 203 ML-KEM) for quantum-resistant encryption.
* **What is a Key Encapsulation Mechanism (KEM)?** Unlike traditional public-key encryption which directly encrypts small messages, a KEM uses a public key to securely generate and encapsulate a shared 256-bit symmetric secret that only the owner of the private secret key can decapsulate.
* **Keypair Concept:**
  * **Kyber Public Key (1568 bytes):** Publicly known; used by the server to encapsulate a shared secret when uploading a file for that user.
  * **Kyber Secret Key (3168 bytes):** Kept strictly confidential; required to decapsulate the shared secret during download.
* **Exact Project Implementation:** Located in `backend/app/services/kyber_service.py` using standard CRYSTALS-Kyber-1024 parameter sets (Public Key: 1568 bytes, Secret Key: 3168 bytes, Ciphertext: 1568 bytes, Shared Secret: 32 bytes).

---

# Section 8: The Complete Hybrid Encryption Process

### Why Hybrid Encryption?

1. **Kyber is a KEM, not a streaming bulk cipher:** Kyber is designed to negotiate a 256-bit shared secret, not to encrypt gigabytes of video or document streams directly.
2. **Performance & Security:** Symmetric AES-256-GCM encrypts files at multi-gigabyte-per-second speeds with hardware acceleration, while Kyber-1024 quantum-proofs the key exchange.

---

### Comprehensive Upload Encryption Flowchart

```
                          PLAINTEXT FILE
                                │
                                ▼
                       Compute SHA-256 Hash
                                │
                                ▼
                   Generate Fresh Random 256-bit DEK
                   & Fresh Random 96-bit GCM Nonce
                                │
                                ▼
                 AES-256-GCM Encrypt File Payload
                                │
                                ▼
                     ENCRYPTED FILE ON DISK
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
Kyber-1024 Encapsulation                        AES GCM Metadata
(Using User's Kyber Public Key)                 (Nonce: 12 bytes)
        │                                               │
        ▼                                               │
  Shared Secret (32 bytes)                              │
        │                                               │
        ▼                                               │
   HKDF-SHA256 (Info: "quantumvault-file-kek-v2")       │
        │                                               │
        ▼                                               │
   KEK (32 bytes)                                       │
        │                                               │
        ▼                                               │
AES Key Wrap (RFC 3394) ◄─────── DEK (32 bytes)         │
        │                                               │
        ▼                                               │
Wrapped DEK (40 bytes hex)                              │
        │                                               │
        └───────────────────────┬───────────────────────┘
                                ▼
                PERSIST METADATA IN MYSQL DATABASE
       [ file_hash, kyber_ciphertext, encrypted_dek, nonce ]
```

---

# Section 9: HKDF (HMAC-based Key Derivation Function)

```text
Raw Kyber Shared Secret (32 pseudorandom bytes from KEM)
                       │
                       ▼
HKDF-SHA256 [ Salt = None, Info = b"quantumvault-file-kek-v2" ]
                       │
                       ▼
Key Encryption Key (KEK) (32 cryptographic key bytes)
```

* **What is Key Derivation?** The process of taking raw entropy or shared secrets and expanding them into a cryptographically uniform, distinct key suitable for a specific cipher.
* **Why do we need HKDF here?** Standard security practice prohibits using the direct output of a mathematical encapsulation mechanism directly as a cipher key. HKDF-SHA256 extracts and expands the entropy, domain-separating it with `b"quantumvault-file-kek-v2"`.
* **What is the KEK?** Key Encryption Key: A 256-bit symmetric key whose sole purpose is to wrap and protect the Data Encryption Key (DEK).

---

# Section 10: AES Key Wrap (RFC 3394)

```text
Data Encryption Key (DEK) [32 bytes]
                  │
                  ▼
AES Key Wrap Algorithm (RFC 3394) ◄─── Input: KEK [32 bytes]
                  │
                  ▼
Wrapped DEK [40 bytes (80 hex characters)]
```

* **What is RFC 3394 AES Key Wrap?** A specialized NIST-standard symmetric algorithm designed specifically to encapsulate cryptographic keys without requiring nonces, providing built-in integrity verification over the wrapped key material.
* **Why not store the DEK in plaintext?** If the database were compromised, an attacker would have all DEKs and could decrypt every file on disk. Storing the DEK wrapped under a post-quantum KEK ensures that only someone with the user's Kyber Secret Key can unwrap the DEK.

---

# Section 11: User Kyber Secret Key Protection

```text
User Registration / Kyber Keypair Generation
                     │
                     ▼
          Kyber-1024 Secret Key (3168 bytes)
                     │
                     ▼
       Server-Side Master Key Envelope Encryption
        (Fernet / AES-128-CBC + HMAC-SHA256)
        ◄─── CRYPTO_MASTER_KEY (from .env)
                     │
                     ▼
         kyber_secret_key_encrypted
        (Persisted in MySQL `users` table)
```

### Master Key Architecture
* **The Master Key (`CRYPTO_MASTER_KEY`):** A 32-byte URL-safe base64 key configured strictly in server environment variables (`.env`). It is **never** checked into Git or stored in MySQL.
* **Envelope Protection:** When a user registers, their Kyber secret key is encrypted under this master key before being saved to the database. Even with a full database dump, an attacker cannot extract any user's Kyber secret key without the master key.

---

### Cryptographic Key Comparison Table

| Key / Hash Name | Type | Generated By | Stored Where | Secret? | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Password Hash** | String (bcrypt) | `auth_service.py` | MySQL `users.password_hash` | **Yes** | Verify user authentication |
| **SHA-256 File Hash** | 64 Hex chars | `hash_service.py` | MySQL `files.file_hash` | No | File tamper & integrity detection |
| **DEK (Data Encryption Key)** | 32 Bytes AES | `pqc_crypto_service.py` | Ephemeral (RAM only) | **Yes** | Encrypts/decrypts actual file bytes |
| **KEK (Key Encryption Key)** | 32 Bytes AES | `HKDF-SHA256` | Ephemeral (RAM only) | **Yes** | Wraps/unwraps the file's DEK |
| **Kyber Public Key** | 1568 Bytes Hex | `kyber_service.py` | MySQL `users.kyber_public_key` | No | Encapsulates shared secret for uploads |
| **Kyber Secret Key** | 3168 Bytes Hex | `kyber_service.py` | Encrypted in MySQL `users.kyber_secret_key_encrypted` | **Strictly Secret** | Decapsulates shared secret on download |
| **Master Key** | 32 Bytes Base64 | Administrator | Server Environment (`.env`) | **Strictly Secret** | Encrypts user Kyber Secret Keys |
| **JWT Secret** | String HMAC | Administrator | Server Environment (`.env`) | **Strictly Secret** | Signs and verifies session JWTs |

---

# Section 12: File Download & Decryption

### Download & Verification Step-by-Step

```text
1. User clicks "Download" on FileCard
                    ↓
2. FastAPI verifies JWT authentication & checks file ownership in MySQL
                    ↓
3. Read encrypted payload from `uploads/<user_id>/<file_id>.enc`
                    ↓
4. Retrieve user record from MySQL containing `kyber_secret_key_encrypted`
                    ↓
5. KeyProtectionService decrypts Kyber Secret Key using `CRYPTO_MASTER_KEY`
                    ↓
6. KyberService decapsulates `file.kyber_ciphertext` using Secret Key → Shared Secret
                    ↓
7. HKDF-SHA256 expands Shared Secret → KEK
                    ↓
8. AES Key Unwrap (RFC 3394) unwraps `file.encrypted_dek` using KEK → DEK
                    ↓
9. AES-256-GCM decrypts payload using DEK and `file.encryption_nonce` → Plaintext Bytes
                    ↓
10. HashService recomputes SHA-256 on Plaintext Bytes and compares with `file.file_hash`
                    ↓
11. AuditLogService logs `FILE_DOWNLOAD_SUCCESS`
                    ↓
12. Stream plaintext bytes to browser with original filename header
```

* **Fail-Closed Security:** If the ciphertext has been modified, AES-GCM authentication fails with `InvalidTag`. If the file hash mismatches, it throws `FileIntegrityCompromised`. In all failure cases, **no decrypted data is ever returned**.

---

# Section 13: JWT Authentication & Cookies

```text
User Submits Login (Email + Password)
                 │
                 ▼
       Verify bcrypt Password Hash
                 │
                 ▼
  Generate Signed JWT Access Token (HS256)
  [ payload: { sub: user_id, exp: 15 mins } ]
                 │
                 ▼
  Set HttpOnly, SameSite=Lax Cookie in HTTP Response
  [ Set-Cookie: access_token=eyJhbG...; HttpOnly; Path=/; ]
                 │
                 ▼
  Browser stores cookie securely; automatically sends it on all API requests
```

* **What is an HttpOnly Cookie?** A cookie with the `HttpOnly` flag cannot be accessed by client-side JavaScript (`document.cookie`). This completely eliminates the threat of Cross-Site Scripting (XSS) token theft.
* **Why Access & Refresh Tokens?**
  * **Access Token (15-minute lifetime):** Fast, stateless authentication verified by HMAC signature.
  * **Refresh Token (7-day lifetime):** Stored as a hash in the database; used to renew expired access tokens without forcing the user to re-enter passwords.
* **Logout:** Calling `/auth/logout` instructs the browser to immediately clear the `access_token` cookie and revokes the refresh token in MySQL.

---

# Section 14: Database Schema & Tables

```
 ┌──────────────────────┐         ┌───────────────────────┐
 │        users         │1       *│     refresh_tokens    │
 │──────────────────────│─────────│───────────────────────│
 │ id (PK)              │         │ id (PK)               │
 │ email (UQ)           │         │ user_id (FK -> users) │
 │ password_hash        │         │ token_hash            │
 │ kyber_public_key     │         │ expires_at, revoked   │
 │ kyber_secret_key_enc │         └───────────────────────┘
 └──────────┬───────────┘
            │1
            │
            │* ┌────────────────────────┐
            ├──┤        folders         │1
            │  │────────────────────────│──┐
            │  │ id (PK)                │  │*
            │  │ owner_id (FK -> users) │◄─┘ (parent_id self-ref)
            │  │ parent_id (FK)         │
            │  │ name, file_count, size │
            │  └───────────┬────────────┘
            │1             │1
            │              │
            │*             │*
 ┌──────────┴──────────────┴┐     ┌───────────────────────┐
 │          files           │1   *│      audit_logs       │
 │──────────────────────────│─────│───────────────────────│
 │ id (PK)                  │     │ id (PK)               │
 │ owner_id (FK -> users)   │     │ user_id (FK -> users) │
 │ folder_id (FK -> folders)│     │ file_id (FK -> files) │
 │ original_filename        │     │ event_type, status    │
 │ file_hash, storage_path  │     │ message, metadata_json│
 │ kyber_ciphertext         │     │ created_at            │
 │ encrypted_dek, nonce     │     └───────────────────────┘
 └──────────────────────────┘
```

1. **`users`:** Core user identities, login credentials (bcrypt hash), and Post-Quantum Kyber-1024 public/encrypted secret keypair.
2. **`refresh_tokens`:** Stores cryptographically hashed active session refresh tokens linked to `users.id`.
3. **`folders`:** Hierarchical folder tree (`parent_id` self-reference), folder sizes, and file count statistics.
4. **`files`:** File metadata, ownership references, MIME types, SHA-256 hash, and Post-Quantum cryptographic fields (`kyber_ciphertext`, `encrypted_dek`, `encryption_nonce`).
5. **`audit_logs`:** Append-only security audit log recording every login, upload, download, move, and access failure.
6. **`alembic_version`:** Single-row table storing the current migration version hash of the database schema.

---

# Section 15: File Movement Architecture

```text
User selects "Move to folder" ──► Selects Target Folder in Modal ──► PATCH /api/v1/files/{file_id}/move
                                                                                │
                                                                                ▼
                                                               ┌────────────────────────────────┐
                                                               │  1. Verify File Ownership      │
                                                               │  2. Verify Folder Ownership    │
                                                               │  3. Check Duplicate Filename   │
                                                               │  4. Update `file.folder_id`    │
                                                               │  5. Update Folder Statistics   │
                                                               │  6. Record FILE_MOVED Audit Log│
                                                               └────────────────┬───────────────┘
                                                                                │
                                                                                ▼
                                                                Return HTTP 200 FileResponse
```

### Why File Moving Involves Zero Cryptographic Overhead

Moving a file simply updates its organizational parent pointer (`folder_id`) in MySQL.
* **No file decryption or re-encryption:** The physical encrypted file on disk (`uploads/<user_id>/<file_id>.enc`) is completely untouched.
* **Zero changes to keys or hashes:** The file's SHA-256 integrity hash, AES-256 DEK, Kyber ciphertext, and nonce remain identical.
* **Zero storage penalty:** Moving a file does not duplicate bytes or change storage quota.

---

# Section 16: Audit & Security Logging

* **What is an Audit Log?** A permanent, chronological record of system events providing accountability and security monitoring.
* **Logged Event Categories:**
  * **AUTH:** `USER_REGISTERED`, `USER_LOGIN_SUCCESS`, `USER_LOGOUT`
  * **FILE:** `FILE_UPLOAD_SUCCESS`, `FILE_DOWNLOAD_SUCCESS`, `FILE_MOVED`, `FILE_DELETED`, `FILE_RENAMED`
  * **CRYPTO:** `FILE_DECRYPTION_SUCCESS`, `KEY_WRAP_SUCCESS`
  * **SECURITY:** `UNAUTHORIZED_FILE_ACCESS`, `INTEGRITY_CHECK_FAILED`, `AES_GCM_AUTHENTICATION_FAILED`
* **Dashboard Activity Feed Integration:** When the dashboard loads (`GET /dashboard/activity`), `dashboard_repository.py` queries recent `AuditLog` records, humanizes action names (e.g. `FILE_MOVED` $\rightarrow$ "Moved"), and renders them in the live activity feed.

---

# Section 17: Core API Endpoints Reference

| Endpoint | Method | Caller & Timing | Backend Operation | Response Content |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/auth/me` | `GET` | Frontend on app load to verify session | Decodes JWT cookie, queries active user | User profile JSON (`id`, `email`, `full_name`) |
| `/api/v1/dashboard/overview` | `GET` | Dashboard view load | Aggregates file/folder/favorite counts | Statistics object & user summary |
| `/api/v1/dashboard/storage` | `GET` | Dashboard view load | Computes storage usage vs 5 GB quota | Used, available, total bytes & percentage |
| `/api/v1/dashboard/recent-files` | `GET` | Dashboard & Recent views | Queries 10 most recent files with PQC metadata | List of file items with algorithms & hashes |
| `/api/v1/dashboard/activity` | `GET` | Dashboard view load | Queries latest 10 AuditLog entries | List of humanized activity items with timestamps |
| `/api/v1/files/folder/{folder_id}`| `GET` | Folder view & My Drive | Returns paginated list of files in folder (or root for `null`) | Paginated `FileListResponse` |
| `/api/v1/folders/root` | `GET` | My Drive view & Move Modal | Queries user's root-level folders | List of `FolderResponse` objects |
| `/api/v1/files/{file_id}/move` | `PATCH` | Move File Modal confirmation | Validates ownership, updates `folder_id` and folder stats | Updated `FileResponse` |

---

# Section 18: Project File Structure

### Backend Structure (`backend/`)

```
backend/
├── alembic/                 # Database schema migration scripts & environment
├── app/
│   ├── api/v1/              # REST API route controllers
│   │   ├── audit/           # Audit log endpoints
│   │   ├── auth/            # Registration, login, logout, refresh
│   │   ├── dashboard/       # Overview, stats, storage, activity
│   │   ├── files/           # Upload, download, move, rename, delete
│   │   └── folders/         # Folder CRUD and hierarchy
│   ├── core/                # Global config, database session, logging setup
│   ├── dependencies/        # FastAPI dependency injection (auth checks, db session)
│   ├── exceptions/          # Custom domain exception classes & HTTP mappings
│   ├── models/              # SQLAlchemy ORM database models
│   ├── repositories/        # Database query abstractions
│   ├── schemas/             # Pydantic request & response schemas
│   ├── services/            # Core business logic & cryptographic engines
│   └── main.py              # FastAPI application factory, CORS, exception handlers
├── uploads/                 # Local directory for encrypted ciphertext file storage
├── requirements.txt         # Pinned Python package dependencies
└── tests_phase2c_e2e.py     # End-to-end integration test suite
```

---

### Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── api/                 # Axios HTTP client instances and API modules
│   │   ├── authApi.js       # Auth endpoint calls
│   │   ├── fileApi.js       # File CRUD & move endpoint calls
│   │   ├── folderApi.js     # Folder CRUD endpoint calls
│   │   └── dashboardApi.js  # Stats & activity calls
│   ├── components/          # Reusable UI React components
│   │   ├── common/          # Badges, buttons, headers
│   │   ├── dashboard/       # Welcome card, statistics grid, activity feed
│   │   ├── FileCard.jsx     # Single file item with actions dropdown
│   │   ├── FileList.jsx     # File grid with search & pagination
│   │   ├── FileUpload.jsx   # Drag-and-drop file upload zone
│   │   └── MoveFileModal.jsx# Folder selector modal for file movement
│   ├── hooks/               # Custom React hooks (`useFiles`, `useDashboard`)
│   ├── pages/               # Route pages (Dashboard, Login, Register)
│   ├── routes/              # Protected & public React Router configuration
│   ├── services/            # Client business logic layer & toast notifications
│   ├── store/               # Zustand global state (active sidebar tab)
│   └── main.jsx             # React entry point mounting into index.html
├── package.json             # NPM dependencies and scripts
└── vite.config.js           # Vite development server & build configuration
```

---

# Section 19: How the Project Was Tested

### Test Suites Overview

1. **PQC Cryptographic Foundation Tests:** Validates AES-256-GCM encryption/decryption, fresh 96-bit nonce generation, Kyber-1024 encapsulation/decapsulation shared secret match, HKDF-SHA256 derivation, and AES Key Wrap/Unwrap roundtrip.
2. **Server-Side Key Protection Tests:** Validates that the master key protects user Kyber secret keys and that plaintext secret keys are never written to disk or database.
3. **Fail-Closed Tamper Tests:** Verifies that modifying a single ciphertext byte, tampering with the GCM authentication tag, or corrupting the SHA-256 hash immediately raises exceptions without leaking plaintext.
4. **End-to-End Integration Suite (`tests_phase2c_e2e.py`):** Uses FastAPI's `TestClient` against the live MySQL database to test registration, JWT cookies, folder creation, encrypted upload, decrypted download, file moves, and logout (20/20 test suites passing).
5. **Frontend Production Build:** Verified via `npm run build` using Vite to ensure zero JSX, CSS module, or bundling errors.

---

# Section 20: Life of a File Inside QuantumVault

Follow the complete journey of a file called **`Financial_Report_2026.pdf`**:

```text
 1. Alice logs in via React UI; receives a signed HttpOnly JWT cookie.
 2. Alice drags `Financial_Report_2026.pdf` (15 MB) into the upload area.
 3. Axios streams the file bytes via POST /api/v1/files/upload.
 4. FastAPI intercepts the request, verifies Alice's JWT cookie, and invokes FileService.
 5. HashService reads the stream and computes the SHA-256 hash: "a4f8c2...".
 6. PQC Engine generates a cryptographically random 256-bit DEK and a 96-bit GCM Nonce.
 7. AES-256-GCM encrypts the 15 MB PDF into an authenticated ciphertext payload.
 8. The ciphertext payload is written to disk at `uploads/<alice_id>/<file_uuid>.enc`.
 9. KyberService encapsulates a 256-bit shared secret using Alice's Kyber-1024 Public Key,
    producing a 1568-byte Kyber Ciphertext.
10. HKDF-SHA256 expands the shared secret into a 256-bit Key Encryption Key (KEK).
11. AES Key Wrap (RFC 3394) wraps the DEK under the KEK, producing a 40-byte Wrapped DEK.
12. FileRepository persists the file metadata (hash, storage path, Kyber ciphertext,
    wrapped DEK, nonce) into the MySQL `files` table.
13. AuditLogService writes a `FILE_UPLOAD_SUCCESS` event to the `audit_logs` table.
14. Alice's dashboard updates in real time, displaying the file with its PQC Security Badge.
15. Alice clicks the three-dot menu on the file card and chooses "Move to folder".
16. MoveFileModal opens, loading Alice's folders; Alice selects "Confidential Audits".
17. Axios sends PATCH /api/v1/files/{file_id}/move with {"folder_id": "<folder_uuid>"}.
18. Backend validates that Alice owns both the file and the destination folder.
19. MySQL updates `files.folder_id` and folder counters; physical file data remains untouched.
20. AuditLogService logs `FILE_MOVED`; the file immediately appears inside "Confidential Audits".
21. Later, Alice clicks "Download".
22. Backend verifies Alice's ownership and reads the encrypted bytes from disk.
23. KeyProtectionService decrypts Alice's Kyber Secret Key using the server CRYPTO_MASTER_KEY.
24. KyberService decapsulates the stored Kyber ciphertext to recover the shared secret.
25. HKDF derives the KEK; AES Key Unwrap recovers the original DEK.
26. AES-256-GCM decrypts the ciphertext payload back to plaintext bytes.
27. HashService calculates the SHA-256 hash on the plaintext and confirms it matches "a4f8c2...".
28. The verified original `Financial_Report_2026.pdf` is streamed to Alice's browser.
```
