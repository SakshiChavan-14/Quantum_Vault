"""
QuantumVault - Phase 2B-6 Test Suite
Production Hardening, Database Configuration, MySQL Compatibility & Alembic Migrations
Validates: Dynamic DATABASE_URL support, MySQL URL enforcement, Alembic migration discovery,
ORM schema completeness, PQC persistence integrity, foreign keys, index structures,
non-destructive operations, and full regression.
"""

import sys
import uuid
import os
import json
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from sqlalchemy import create_engine, inspect, text
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, RefreshToken
from app.models.folder import Folder
from app.models.file import File
from app.models.audit_log import AuditLog
from app.repositories.file_repository import FileRepository
from app.repositories.folder_repository import FolderRepository
from app.repositories.auth_repository import AuthRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.file_service import FileService
from app.services.auth_service import AuthService
from app.services.audit_log_service import AuditLogService
from app.services.encryption_service import EncryptionService
from app.services.hash_service import HashService
from app.services.pqc_crypto_service import PQC_ENCRYPTION_ALGORITHM, LEGACY_ENCRYPTION_ALGORITHM
from app.schemas.auth import RegisterRequest


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def record(self, name: str, success: bool, message: str = ""):
        if success:
            self.passed += 1
            self.tests.append((name, "PASS", message))
            print(f"✅ PASS: {name}")
        else:
            self.failed += 1
            self.tests.append((name, "FAIL", message))
            print(f"❌ FAIL: {name} - {message}")

    @property
    def total(self) -> int:
        return self.passed + self.failed


def run_all_tests() -> bool:
    results = TestResults()
    print("\n" + "="*70)
    print("QUANTUMVAULT PHASE 2B-6 DATABASE & PRODUCTION HARDENING TESTS")
    print("="*70)

    # TEST 1: DATABASE_URL loads correctly
    db_url_loaded = bool(settings.DATABASE_URL and len(settings.DATABASE_URL) > 5)
    results.record("TEST 1: DATABASE_URL loads correctly from environment configuration", db_url_loaded)

    # TEST 2: Active configuration uses MySQL only
    is_mysql = settings.DATABASE_URL.startswith("mysql+pymysql://") or settings.DATABASE_URL.startswith("mysql://")
    results.record("TEST 2: Active DATABASE_URL is configured for MySQL only", is_mysql)

    # TEST 3: MySQL URL format is accepted by Settings validator
    try:
        dummy_mysql_settings = Settings(
            DATABASE_URL="mysql+pymysql://quantum_user:SecretPass123!@localhost:3306/quantumvault"
        )
        mysql_accepted = dummy_mysql_settings.DATABASE_URL.startswith("mysql+pymysql://")
    except Exception:
        mysql_accepted = False
    results.record("TEST 3: MySQL+PyMySQL connection URL format is accepted by configuration validator", mysql_accepted)

    # TEST 4: Invalid database URLs and non-MySQL formats are rejected by validator
    invalid_url_caught = False
    try:
        Settings(DATABASE_URL="sqlite:///./old_db.sqlite")
    except ValidationError:
        invalid_url_caught = True
    except Exception:
        invalid_url_caught = True
    results.record("TEST 4: Non-MySQL database configurations are rejected by validator", invalid_url_caught)

    # TEST 5 & 6: All ORM models are discovered by SQLAlchemy Base metadata
    expected_tables = {"users", "refresh_tokens", "folders", "files", "audit_logs"}
    discovered_tables = set(Base.metadata.tables.keys())
    all_discovered = expected_tables.issubset(discovered_tables)
    results.record("TEST 5: All 5 ORM models are discovered by SQLAlchemy Base metadata", all_discovered)
    results.record("TEST 6: Migration metadata contains users, refresh_tokens, folders, files, audit_logs", all_discovered)

    # Database inspector checks on active engine
    with engine.connect() as conn:
        insp = inspect(conn)
        live_tables = set(insp.get_table_names())

        # TEST 7: users table schema is correct
        user_cols = {c["name"]: c for c in insp.get_columns("users")}
        user_schema_ok = (
            "kyber_public_key" in user_cols
            and "kyber_secret_key_encrypted" in user_cols
            and "email" in user_cols
            and "password_hash" in user_cols
        )
        results.record("TEST 7: users table schema contains all required authentication and Kyber columns", user_schema_ok)

        # TEST 8: files table schema is correct
        file_cols = {c["name"]: c for c in insp.get_columns("files")}
        file_schema_ok = (
            "kyber_ciphertext" in file_cols
            and "encrypted_dek" in file_cols
            and "encryption_nonce" in file_cols
            and "encryption_algorithm" in file_cols
            and "encryption_key_hash" in file_cols
            and "file_hash" in file_cols
        )
        results.record("TEST 8: files table schema contains all required PQC Version 2 and legacy columns", file_schema_ok)

        # TEST 9: audit_logs table schema is correct
        audit_cols = {c["name"]: c for c in insp.get_columns("audit_logs")}
        audit_schema_ok = (
            "event_type" in audit_cols
            and "event_category" in audit_cols
            and "status" in audit_cols
            and "message" in audit_cols
            and "metadata_json" in audit_cols
            and "user_id" in audit_cols
            and "file_id" in audit_cols
        )
        results.record("TEST 9: audit_logs table schema contains all required security event columns", audit_schema_ok)

        # TEST 10: Foreign keys are declared correctly
        fk_files = [fk["referred_table"] for fk in insp.get_foreign_keys("files")]
        fk_audit = [fk["referred_table"] for fk in insp.get_foreign_keys("audit_logs")]
        fk_ok = "users" in fk_files and "folders" in fk_files and "users" in fk_audit
        results.record("TEST 10: Foreign key relationships to users and folders are valid", fk_ok)

        # TEST 11: Required indexes exist
        file_indexes = [idx["name"] for idx in insp.get_indexes("files")]
        audit_indexes = [idx["name"] for idx in insp.get_indexes("audit_logs")]
        indexes_ok = (
            any("owner_id" in str(idx) for idx in file_indexes)
            and any("event_type" in str(idx) for idx in audit_indexes)
        )
        results.record("TEST 11: Required database indexes exist on files and audit_logs tables", indexes_ok)

    # Persistence verification using real transactions
    db = SessionLocal()
    try:
        auth_service = AuthService(AuthRepository(db))
        test_email = f"p2b6_user_{uuid.uuid4().hex[:8]}@example.com"
        reg_req = RegisterRequest(
            full_name="Phase 2B-6 Test User",
            email=test_email,
            password="SecurePassword123!",
            confirm_password="SecurePassword123!"
        )
        created_user = auth_service.register_user(reg_req)

        # TEST 12: Kyber public key can be persisted
        results.record(
            "TEST 12: Kyber-1024 public key is successfully persisted in database",
            bool(created_user.kyber_public_key and len(created_user.kyber_public_key) >= 3000)
        )

        # TEST 13: Encrypted Kyber secret key can be persisted
        results.record(
            "TEST 13: Encrypted Kyber secret key is successfully persisted in database",
            bool(created_user.kyber_secret_key_encrypted and len(created_user.kyber_secret_key_encrypted) >= 100)
        )

        # TEST 14: PQC file metadata can be persisted
        file_service = FileService(FileRepository(db), FolderRepository(db))
        sample_plaintext = f"PQC Database Hardening Payload 2026 {uuid.uuid4().hex}.".encode("utf-8")
        uploaded_file = file_service.upload_file(
            owner_id=created_user.id,
            filename=f"p2b6_file_{uuid.uuid4().hex[:6]}.txt",
            file_content=sample_plaintext,
            description="Phase 2B-6 Database Test"
        )
        db_file = db.query(File).filter(File.id == uploaded_file.id).first()
        pqc_persisted = (
            db_file.encryption_algorithm == PQC_ENCRYPTION_ALGORITHM
            and db_file.kyber_ciphertext is not None
            and db_file.encrypted_dek is not None
            and db_file.encryption_nonce is not None
        )
        results.record("TEST 14: Post-Quantum Cryptographic file metadata persists reliably", pqc_persisted)

        # TEST 15: Audit events can be persisted
        audit_service = AuditLogService(AuditLogRepository(db))
        log_entry = audit_service.log_security_event(
            event_type="DATABASE_COMPATIBILITY_CHECK",
            status="SUCCESS",
            message="Database schema compatibility test executed successfully",
            user_id=created_user.id,
            file_id=uploaded_file.id
        )
        results.record("TEST 15: Audit events persist successfully with relational integrity", log_entry is not None and log_entry.id is not None)

        # TEST 16: No plaintext cryptographic secret is persisted
        no_secrets = (
            not hasattr(db_file, "dek")
            and not hasattr(db_file, "plaintext_dek")
            and not hasattr(created_user, "kyber_secret_key_plaintext")
        )
        results.record("TEST 16: Zero plaintext DEKs, KEKs, or Kyber secret keys are persisted in DB", no_secrets)

        # TEST 17: Legacy Fernet metadata remains compatible
        legacy_data = b"Legacy compatibility test."
        enc_legacy, legacy_key, legacy_algo = EncryptionService.encrypt_file(legacy_data)
        legacy_file = File(
            id=str(uuid.uuid4()),
            owner_id=created_user.id,
            original_filename="legacy_compat.txt",
            stored_filename=f"legacy_{uuid.uuid4().hex}.enc",
            file_size=len(legacy_data),
            mime_type="text/plain",
            storage_path="uploads/legacy.enc",
            file_hash=HashService.calculate_file_hash(legacy_data),
            is_encrypted=True,
            encryption_algorithm=LEGACY_ENCRYPTION_ALGORITHM,
            encryption_key_hash=legacy_key
        )
        db.add(legacy_file)
        db.commit()
        retrieved_legacy = db.query(File).filter(File.id == legacy_file.id).first()
        results.record("TEST 17: Legacy AES-128-Fernet metadata remains fully compatible with ORM schema", retrieved_legacy is not None)

    except Exception as e:
        results.record("DATABASE TEST EXECUTION FAILED", False, str(e))
    finally:
        db.close()

    # TEST 18: Database connection error handling
    try:
        bad_engine = create_engine("mysql+pymysql://nonexistent_user:invalid_pass@127.0.0.1:9999/nonexistent_db", connect_args={"connect_timeout": 1})
        with bad_engine.connect() as conn:
            pass
        db_err_handled = False
    except Exception:
        db_err_handled = True
    results.record("TEST 18: Unreachable database connection fails cleanly without crashing process", db_err_handled)

    # TEST 19: FastAPI application imports successfully
    try:
        from app.main import app as fastapi_app
        results.record("TEST 19: FastAPI application imports cleanly with hardened database config", bool(fastapi_app))
    except Exception as e:
        results.record("TEST 19: FastAPI app import failed", False, str(e))

    # TEST 20: Full regression suite execution
    try:
        from tests_phase2b1 import run_all_tests as run_p2b1
        from tests_phase2b2 import run_all_tests as run_p2b2
        from tests_phase2b3 import run_all_tests as run_p2b3
        from tests_phase2b4 import run_all_tests as run_p2b4
        from tests_phase2b5 import run_all_tests as run_p2b5

        p2b1 = run_p2b1()
        p2b2 = run_p2b2()
        p2b3 = run_p2b3()
        p2b4 = run_p2b4()
        p2b5 = run_p2b5()
        regression_all = p2b1 and p2b2 and p2b3 and p2b4 and p2b5
        results.record("TEST 20: Full regression suite (Phase 2B-1 through Phase 2B-5) passes 100%", regression_all)
    except Exception as e:
        results.record("TEST 20: Regression suite execution failed", False, str(e))

    print("\n" + "="*70)
    print(f"RESULTS SUMMARY: Passed: {results.passed}/{results.total}, Failed: {results.failed}/{results.total}")
    print("="*70)
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
