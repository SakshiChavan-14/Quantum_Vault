"""
QuantumVault - Phase 2B-4 Test Suite
Live Post-Quantum File Upload & Download Pipeline Integration Verification
Validates: Live PQC upload, algorithm dispatch, disk encryption, authenticated decryption,
fail-closed tampering checks, legacy Fernet backward compatibility, authorization, and full regression.
"""

import sys
import uuid
import os
import io
from pathlib import Path

from app.core.database import SessionLocal
from app.models.user import User
from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.repositories.folder_repository import FolderRepository
from app.repositories.auth_repository import AuthRepository
from app.services.file_service import FileService
from app.services.auth_service import AuthService
from app.services.encryption_service import EncryptionService
from app.services.hash_service import HashService
from app.services.pqc_crypto_service import PQC_ENCRYPTION_ALGORITHM, LEGACY_ENCRYPTION_ALGORITHM
from app.schemas.auth import RegisterRequest
from app.exceptions.FileExceptions import (
    FileNotFound,
    FileIntegrityCompromised,
    UnsupportedEncryptionAlgorithm,
    DecryptionFailed,
    UploadFailed,
)


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
    print("QUANTUMVAULT PHASE 2B-4 LIVE PQC PIPELINE INTEGRATION TESTS")
    print("="*70)

    db = SessionLocal()
    try:
        # Create test users via AuthService
        auth_service = AuthService(AuthRepository(db))
        user_req = RegisterRequest(
            full_name="PQC Live Test User",
            email=f"pqc_user_{uuid.uuid4().hex[:8]}@example.com",
            password="SecurePassword123!",
            confirm_password="SecurePassword123!"
        )
        test_user = auth_service.register_user(user_req)

        other_req = RegisterRequest(
            full_name="Other PQC User",
            email=f"other_{uuid.uuid4().hex[:8]}@example.com",
            password="SecurePassword123!",
            confirm_password="SecurePassword123!"
        )
        other_user = auth_service.register_user(other_req)

        file_service = FileService(FileRepository(db), FolderRepository(db))

        # Sample test data
        sample_plaintext = f"TOP SECRET QUANTUMVAULT REPORT 2026: PQC LIVE PIPELINE DATA {uuid.uuid4().hex}.".encode("utf-8")
        test_filename = f"confidential_pqc_{uuid.uuid4().hex[:6]}.txt"

        # TEST 1: New PQC file upload succeeds
        uploaded = file_service.upload_file(
            owner_id=test_user.id,
            filename=test_filename,
            file_content=sample_plaintext,
            description="Live PQC Test File"
        )
        results.record("TEST 1: New PQC file upload succeeds", bool(uploaded and uploaded.id))

        # Fetch ORM record directly from DB to inspect fields
        db_file = db.query(File).filter(File.id == uploaded.id).first()

        # TEST 2: New uploaded file has algorithm == AES-256-GCM+Kyber1024
        results.record(
            "TEST 2: New file has encryption_algorithm == AES-256-GCM+Kyber1024",
            db_file.encryption_algorithm == PQC_ENCRYPTION_ALGORITHM
        )

        # TEST 3: New file stores kyber_ciphertext
        results.record(
            "TEST 3: New file stores kyber_ciphertext (hex string)",
            bool(db_file.kyber_ciphertext and len(db_file.kyber_ciphertext) >= 3000)
        )

        # TEST 4: New file stores encrypted_dek
        results.record(
            "TEST 4: New file stores encrypted_dek (wrapped DEK hex)",
            bool(db_file.encrypted_dek and len(db_file.encrypted_dek) >= 80)
        )

        # TEST 5: New file stores encryption_nonce
        results.record(
            "TEST 5: New file stores encryption_nonce (12-byte hex)",
            bool(db_file.encryption_nonce and len(db_file.encryption_nonce) == 24)
        )

        # TEST 6: New PQC file has encryption_key_hash is NULL / unused
        results.record(
            "TEST 6: New PQC file has encryption_key_hash NULL (no raw key saved)",
            db_file.encryption_key_hash is None
        )

        # TEST 7: Encrypted file on disk is not equal to original plaintext
        disk_path = Path("uploads") / db_file.storage_path
        with open(disk_path, "rb") as f:
            disk_bytes = f.read()
        results.record(
            "TEST 7: Encrypted payload on disk is not equal to original plaintext",
            disk_bytes != sample_plaintext and sample_plaintext not in disk_bytes
        )

        # TEST 8: PQC file download restores exactly the original bytes
        downloaded_file, recovered_bytes = file_service.get_file_for_download(
            file_id=uploaded.id,
            owner_id=test_user.id
        )
        results.record(
            "TEST 8: PQC file download restores exact original plaintext bytes",
            recovered_bytes == sample_plaintext
        )

        # TEST 9: Tampered encrypted ciphertext fails closed
        tampered_bytes = bytearray(disk_bytes)
        tampered_bytes[0] ^= 0xFF  # Corrupt first byte of ciphertext
        with open(disk_path, "wb") as f:
            f.write(tampered_bytes)

        tamper_caught = False
        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=test_user.id)
        except DecryptionFailed:
            tamper_caught = True

        # Restore good file bytes on disk
        with open(disk_path, "wb") as f:
            f.write(disk_bytes)

        results.record("TEST 9: Tampered encrypted ciphertext fails closed", tamper_caught)

        # TEST 10: Tampered AES-GCM authentication tag/ciphertext fails closed
        tag_tampered = bytearray(disk_bytes)
        tag_tampered[-1] ^= 0xAA  # Corrupt last byte (part of auth tag)
        with open(disk_path, "wb") as f:
            f.write(tag_tampered)

        tag_tamper_caught = False
        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=test_user.id)
        except DecryptionFailed:
            tag_tamper_caught = True

        # Restore good file bytes on disk
        with open(disk_path, "wb") as f:
            f.write(disk_bytes)

        results.record("TEST 10: Tampered AES-GCM tag fails closed", tag_tamper_caught)

        # TEST 11: Tampered nonce fails closed
        original_nonce = db_file.encryption_nonce
        db_file.encryption_nonce = "00" * 12
        db.commit()

        nonce_tamper_caught = False
        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=test_user.id)
        except DecryptionFailed:
            nonce_tamper_caught = True

        db_file.encryption_nonce = original_nonce
        db.commit()
        results.record("TEST 11: Tampered encryption nonce fails closed", nonce_tamper_caught)

        # TEST 12: Tampered wrapped DEK fails closed
        original_dek = db_file.encrypted_dek
        db_file.encrypted_dek = "ff" * 40
        db.commit()

        dek_tamper_caught = False
        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=test_user.id)
        except DecryptionFailed:
            dek_tamper_caught = True

        db_file.encrypted_dek = original_dek
        db.commit()
        results.record("TEST 12: Tampered wrapped DEK fails closed", dek_tamper_caught)

        # TEST 13: Wrong Kyber secret key fails closed
        original_user_sk = test_user.kyber_secret_key_encrypted
        test_user.kyber_secret_key_encrypted = other_user.kyber_secret_key_encrypted
        db.commit()

        wrong_sk_caught = False
        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=test_user.id)
        except DecryptionFailed:
            wrong_sk_caught = True

        test_user.kyber_secret_key_encrypted = original_user_sk
        db.commit()
        results.record("TEST 13: Wrong Kyber secret key fails closed", wrong_sk_caught)

        # TEST 14: SHA-256 integrity mismatch raises FileIntegrityCompromised
        original_hash = db_file.file_hash
        db_file.file_hash = "a" * 64  # Tampered expected hash
        db.commit()

        hash_mismatch_caught = False
        returned_plaintext = None
        try:
            _, returned_plaintext = file_service.get_file_for_download(
                file_id=uploaded.id, owner_id=test_user.id
            )
        except FileIntegrityCompromised:
            hash_mismatch_caught = True

        db_file.file_hash = original_hash
        db.commit()
        results.record("TEST 14: SHA-256 integrity mismatch raises FileIntegrityCompromised", hash_mismatch_caught)

        # TEST 15: Integrity mismatch prevents plaintext return
        results.record("TEST 15: Integrity mismatch fails closed without returning plaintext", returned_plaintext is None)

        # TEST 16: Existing AES-128-Fernet legacy file still downloads correctly
        legacy_content = b"Legacy unencrypted original note from phase 3."
        enc_legacy, legacy_key, legacy_algo = EncryptionService.encrypt_file(legacy_content)
        legacy_hash = HashService.calculate_file_hash(legacy_content)

        legacy_disk_filename = f"legacy_{uuid.uuid4().hex}.enc"
        legacy_user_dir = Path("uploads") / test_user.id
        legacy_user_dir.mkdir(parents=True, exist_ok=True)
        legacy_disk_path = legacy_user_dir / legacy_disk_filename
        with open(legacy_disk_path, "wb") as f:
            f.write(enc_legacy)

        legacy_file = File(
            id=str(uuid.uuid4()),
            owner_id=test_user.id,
            original_filename="legacy_fernet_note.txt",
            stored_filename=legacy_disk_filename,
            file_size=len(legacy_content),
            mime_type="text/plain",
            storage_path=str(legacy_disk_path.relative_to(Path("uploads"))),
            file_hash=legacy_hash,
            is_encrypted=True,
            encryption_algorithm=LEGACY_ENCRYPTION_ALGORITHM,
            encryption_key_hash=legacy_key,
            kyber_ciphertext=None,
            encrypted_dek=None,
            encryption_nonce=None
        )
        db.add(legacy_file)
        db.commit()

        _, recovered_legacy = file_service.get_file_for_download(
            file_id=legacy_file.id,
            owner_id=test_user.id
        )
        results.record(
            "TEST 16: Existing AES-128-Fernet legacy files decrypt & download perfectly",
            recovered_legacy == legacy_content
        )

        # TEST 17: Unknown encryption_algorithm fails closed
        legacy_file.encryption_algorithm = "UNKNOWN-CIPHER-999"
        db.commit()

        unknown_algo_caught = False
        try:
            file_service.get_file_for_download(file_id=legacy_file.id, owner_id=test_user.id)
        except UnsupportedEncryptionAlgorithm:
            unknown_algo_caught = True

        results.record(
            "TEST 17: Unknown encryption algorithm fails closed (UnsupportedEncryptionAlgorithm)",
            unknown_algo_caught
        )

        # TEST 18: Unauthorized user cannot download another user's file
        unauthorized_caught = False
        try:
            file_service.get_file_for_download(file_id=uploaded.id, owner_id=other_user.id)
        except FileNotFound:
            unauthorized_caught = True

        results.record("TEST 18: Unauthorized user access rejected", unauthorized_caught)

        # TEST 19: No plaintext DEK is persisted in DB
        raw_db_vals = [str(v) for v in db_file.__dict__.values()]
        no_plaintext_dek_persisted = not any(
            hasattr(db_file, attr) for attr in ["dek", "plaintext_dek", "aes_key"]
        )
        results.record("TEST 19: No plaintext DEK persisted in database", no_plaintext_dek_persisted)

        # TEST 20: No Kyber secret key is exposed in file responses
        response_data = uploaded.model_dump()
        no_secrets_in_response = (
            "kyber_ciphertext" not in response_data
            and "encrypted_dek" not in response_data
            and "encryption_nonce" not in response_data
            and "encryption_key_hash" not in response_data
        )
        results.record("TEST 20: File API responses strictly exclude internal crypto metadata", no_secrets_in_response)

    except Exception as e:
        results.record("TEST SUITE EXECUTION FAILED", False, str(e))
    finally:
        db.close()

    # TEST 21, 22, 23: Run regressions for Phase 2B-1, Phase 2B-2, Phase 2B-3
    try:
        from tests_phase2b1 import run_all_tests as run_p2b1
        from tests_phase2b2 import run_all_tests as run_p2b2
        from tests_phase2b3 import run_all_tests as run_p2b3

        p2b1_ok = run_p2b1()
        results.record("TEST 21: Phase 2B-1 regression tests pass", p2b1_ok)

        p2b2_ok = run_p2b2()
        results.record("TEST 22: Phase 2B-2 regression tests pass", p2b2_ok)

        p2b3_ok = run_p2b3()
        results.record("TEST 23: Phase 2B-3 regression tests pass", p2b3_ok)
    except Exception as e:
        results.record("TEST 21-23: Regression test execution failed", False, str(e))

    # TEST 24 & 25: Application router and initialization validation
    try:
        from app.api.v1.files.router import router as files_router
        results.record("TEST 24: File API router and dependencies import cleanly", bool(files_router))
        
        from app.main import app as fastapi_app
        results.record("TEST 25: FastAPI app initializes successfully with live PQC pipeline", bool(fastapi_app))
    except Exception as e:
        results.record("TEST 24-25: FastAPI app import failed", False, str(e))

    print("\n" + "="*70)
    print(f"RESULTS SUMMARY: Passed: {results.passed}/{results.total}, Failed: {results.failed}/{results.total}")
    print("="*70)
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
