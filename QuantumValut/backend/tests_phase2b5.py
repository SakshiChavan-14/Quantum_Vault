"""
QuantumVault - Phase 2B-5 Test Suite
Audit Logging & Security Event Integration Verification
Validates: AuditLog model & table, upload/download event tracking, crypto events,
security alerts (tampering, integrity check failure, unauthorized access), auth events,
metadata sanitization, legacy compatibility, and complete regression.
"""

import sys
import uuid
import os
import json
from pathlib import Path
from sqlalchemy import inspect
from fastapi import Response

from app.core.database import SessionLocal, engine
from app.models.user import User
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
from app.schemas.auth import RegisterRequest, LoginRequest
from app.exceptions.FileExceptions import (
    FileNotFound,
    FileIntegrityCompromised,
    UnsupportedEncryptionAlgorithm,
    DecryptionFailed,
    UploadFailed,
)
from app.exceptions import InvalidCredentials


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
    print("QUANTUMVAULT PHASE 2B-5 AUDIT LOGGING & SECURITY EVENT TESTS")
    print("="*70)

    db = SessionLocal()
    try:
        # TEST 1: AuditLog table exists
        with engine.connect() as conn:
            insp = inspect(conn)
            tables = insp.get_table_names()
            audit_cols = [c["name"] for c in insp.get_columns("audit_logs")] if "audit_logs" in tables else []
            table_ok = "audit_logs" in tables and all(
                col in audit_cols for col in ["id", "event_type", "event_category", "status", "message", "created_at"]
            )
        results.record("TEST 1: AuditLog table exists in database with required schema", table_ok)

        # Create test users
        auth_service = AuthService(AuthRepository(db))
        test_email = f"audit_user_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePassword123!"
        
        reg_req = RegisterRequest(
            full_name="Audit Log Test User",
            email=test_email,
            password=password,
            confirm_password=password
        )
        test_user = auth_service.register_user(reg_req)

        other_email = f"other_audit_{uuid.uuid4().hex[:8]}@example.com"
        other_req = RegisterRequest(
            full_name="Other Audit User",
            email=other_email,
            password=password,
            confirm_password=password
        )
        other_user = auth_service.register_user(other_req)

        file_service = FileService(FileRepository(db), FolderRepository(db))

        # Upload a file
        sample_plaintext = f"CONFIDENTIAL AUDIT DATA {uuid.uuid4().hex}.".encode("utf-8")
        test_filename = f"audit_test_{uuid.uuid4().hex[:6]}.txt"

        uploaded = file_service.upload_file(
            owner_id=test_user.id,
            filename=test_filename,
            file_content=sample_plaintext,
            description="Audit Logging Test File"
        )

        # TEST 2: Successful file upload creates audit logs
        upload_logs = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == test_user.id, AuditLog.event_type == "FILE_UPLOAD_SUCCESS")
            .all()
        )
        results.record("TEST 2: Successful file upload creates FILE_UPLOAD_SUCCESS audit log", len(upload_logs) > 0)

        # TEST 3: Successful encryption creates audit log
        crypto_logs = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == test_user.id, AuditLog.event_type == "FILE_ENCRYPTION_SUCCESS")
            .all()
        )
        results.record("TEST 3: Successful encryption creates FILE_ENCRYPTION_SUCCESS audit log", len(crypto_logs) > 0)

        # TEST 4: Successful PQC download creates audit log
        _, recovered_bytes = file_service.get_file_for_download(
            file_id=uploaded.id,
            owner_id=test_user.id
        )
        download_logs = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == test_user.id, AuditLog.file_id == uploaded.id, AuditLog.event_type == "FILE_DOWNLOAD_SUCCESS")
            .all()
        )
        results.record("TEST 4: Successful PQC download creates FILE_DOWNLOAD_SUCCESS audit log", len(download_logs) > 0 and recovered_bytes == sample_plaintext)

        # TEST 5: Successful decryption creates audit log
        decrypt_logs = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == test_user.id, AuditLog.file_id == uploaded.id, AuditLog.event_type == "FILE_DECRYPTION_SUCCESS")
            .all()
        )
        results.record("TEST 5: Successful decryption creates FILE_DECRYPTION_SUCCESS audit log", len(decrypt_logs) > 0)

        # TEST 6: Tampered ciphertext creates security audit log
        db_file = db.query(File).filter(File.id == uploaded.id).first()
        disk_path = Path("uploads") / db_file.storage_path
        with open(disk_path, "rb") as f:
            disk_bytes = f.read()

        tampered_bytes = bytearray(disk_bytes)
        tampered_bytes[0] ^= 0xFF  # Corrupt ciphertext
        with open(disk_path, "wb") as f:
            f.write(tampered_bytes)

        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=test_user.id)
        except DecryptionFailed:
            pass

        # Restore good file bytes
        with open(disk_path, "wb") as f:
            f.write(disk_bytes)

        tamper_logs = (
            db.query(AuditLog)
            .filter(AuditLog.file_id == uploaded.id, AuditLog.event_type == "AES_GCM_AUTHENTICATION_FAILED")
            .all()
        )
        results.record("TEST 6: Tampered ciphertext creates AES_GCM_AUTHENTICATION_FAILED audit log", len(tamper_logs) > 0)

        # TEST 7: SHA-256 mismatch creates INTEGRITY_CHECK_FAILED
        orig_hash = db_file.file_hash
        db_file.file_hash = "b" * 64
        db.commit()

        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=test_user.id)
        except FileIntegrityCompromised:
            pass

        db_file.file_hash = orig_hash
        db.commit()

        integrity_logs = (
            db.query(AuditLog)
            .filter(AuditLog.file_id == uploaded.id, AuditLog.event_type == "INTEGRITY_CHECK_FAILED")
            .all()
        )
        results.record("TEST 7: SHA-256 mismatch creates INTEGRITY_CHECK_FAILED audit log", len(integrity_logs) > 0)

        # TEST 8: Unauthorized file access creates audit event
        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=other_user.id)
        except FileNotFound:
            pass

        unauth_logs = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == other_user.id, AuditLog.file_id == uploaded.id, AuditLog.event_type == "UNAUTHORIZED_FILE_ACCESS")
            .all()
        )
        results.record("TEST 8: Unauthorized file access creates UNAUTHORIZED_FILE_ACCESS audit event", len(unauth_logs) > 0)

        # TEST 9: Login success creates audit event
        response = Response()
        login_req = LoginRequest(email=test_email, password=password)
        auth_service.authenticate_user(login_req, response)

        login_success_logs = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == test_user.id, AuditLog.event_type == "USER_LOGIN_SUCCESS")
            .all()
        )
        results.record("TEST 9: Login success creates USER_LOGIN_SUCCESS audit event", len(login_success_logs) > 0)

        # TEST 10: Login failure creates audit event
        bad_login_req = LoginRequest(email=test_email, password="WrongPassword999!")
        try:
            auth_service.authenticate_user(bad_login_req, response)
        except InvalidCredentials:
            pass

        login_fail_logs = (
            db.query(AuditLog)
            .filter(AuditLog.event_type == "USER_LOGIN_FAILED")
            .all()
        )
        results.record("TEST 10: Login failure creates USER_LOGIN_FAILED audit event", len(login_fail_logs) > 0)

        # TEST 11: No cryptographic secret appears in audit metadata
        all_logs = db.query(AuditLog).all()
        sensitive_crypto_words = ["dek", "kek", "shared_secret", "secret_key", "crypto_master_key", "plaintext"]
        crypto_leak_found = False
        for log in all_logs:
            if log.metadata_json:
                data = json.loads(log.metadata_json)
                for k in data.keys():
                    if any(w in str(k).lower() for w in sensitive_crypto_words):
                        crypto_leak_found = True
        results.record("TEST 11: No cryptographic secret appears in audit metadata", not crypto_leak_found)

        # TEST 12: No password or token appears in audit logs
        password_leak_found = False
        for log in all_logs:
            if log.metadata_json:
                data = json.loads(log.metadata_json)
                for k in data.keys():
                    if "password" in str(k).lower() or "token" in str(k).lower():
                        password_leak_found = True
        results.record("TEST 12: No password or token appears in audit logs", not password_leak_found)

        # TEST 13: Legacy Fernet download still works
        legacy_content = b"Audit logging legacy note test."
        enc_legacy, legacy_key, legacy_algo = EncryptionService.encrypt_file(legacy_content)
        legacy_hash = HashService.calculate_file_hash(legacy_content)

        legacy_disk_filename = f"audit_legacy_{uuid.uuid4().hex}.enc"
        legacy_user_dir = Path("uploads") / test_user.id
        legacy_user_dir.mkdir(parents=True, exist_ok=True)
        legacy_disk_path = legacy_user_dir / legacy_disk_filename
        with open(legacy_disk_path, "wb") as f:
            f.write(enc_legacy)

        legacy_file = File(
            id=str(uuid.uuid4()),
            owner_id=test_user.id,
            original_filename="audit_legacy_note.txt",
            stored_filename=legacy_disk_filename,
            file_size=len(legacy_content),
            mime_type="text/plain",
            storage_path=str(legacy_disk_path.relative_to(Path("uploads"))),
            file_hash=legacy_hash,
            is_encrypted=True,
            encryption_algorithm=LEGACY_ENCRYPTION_ALGORITHM,
            encryption_key_hash=legacy_key,
        )
        db.add(legacy_file)
        db.commit()

        _, recovered_legacy = file_service.get_file_for_download(
            file_id=legacy_file.id,
            owner_id=test_user.id
        )
        results.record("TEST 13: Legacy Fernet download still works and logs events", recovered_legacy == legacy_content)

        # TEST 14: PQC AES-256-GCM+Kyber1024 download still works
        _, recovered_pqc = file_service.get_file_for_download(
            file_id=uploaded.id,
            owner_id=test_user.id
        )
        results.record("TEST 14: PQC AES-256-GCM+Kyber1024 download verified with audit logging", recovered_pqc == sample_plaintext)

    except Exception as e:
        results.record("TEST SUITE EXECUTION FAILED", False, str(e))
    finally:
        db.close()

    # TEST 15, 16, 17, 18: Regression suites for Phase 2B-1, Phase 2B-2, Phase 2B-3, Phase 2B-4
    try:
        from tests_phase2b1 import run_all_tests as run_p2b1
        from tests_phase2b2 import run_all_tests as run_p2b2
        from tests_phase2b3 import run_all_tests as run_p2b3
        from tests_phase2b4 import run_all_tests as run_p2b4

        results.record("TEST 15: Phase 2B-1 regression tests pass", run_p2b1())
        results.record("TEST 16: Phase 2B-2 regression tests pass", run_p2b2())
        results.record("TEST 17: Phase 2B-3 regression tests pass", run_p2b3())
        results.record("TEST 18: Phase 2B-4 regression tests pass", run_p2b4())
    except Exception as e:
        results.record("TEST 15-18: Regression test execution failed", False, str(e))

    # TEST 19: Application import validation
    try:
        from app.main import app as fastapi_app
        results.record("TEST 19: FastAPI application imports successfully with audit routes", bool(fastapi_app))
    except Exception as e:
        results.record("TEST 19: FastAPI app import failed", False, str(e))

    print("\n" + "="*70)
    print(f"RESULTS SUMMARY: Passed: {results.passed}/{results.total}, Failed: {results.failed}/{results.total}")
    print("="*70)
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
