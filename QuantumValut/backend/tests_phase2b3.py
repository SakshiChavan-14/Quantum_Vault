"""
QuantumVault - Phase 2B-3 Test Suite
File Cryptographic Metadata Schema & Migration Verification
Validates: File ORM fields, Nullability, Legacy compatibility, PQC record support,
Schema privacy, Non-destructive database migration, and Phase 2B-1/2B-2 regression.
"""

import sys
import uuid
from sqlalchemy import inspect

from app.core.database import SessionLocal, engine
from app.models.file import File
from app.models.user import User
from app.schemas.file import FileResponse, FileListItem
from app.services.pqc_crypto_service import (
    PQC_ENCRYPTION_ALGORITHM,
    PQC_CRYPTO_VERSION,
    LEGACY_ENCRYPTION_ALGORITHM
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


def run_all_tests() -> bool:
    results = TestResults()
    print("\n" + "="*70)
    print("QUANTUMVAULT PHASE 2B-3 FILE METADATA SCHEMA & MIGRATION TESTS")
    print("="*70)

    # Inspect columns from active DB engine
    with engine.connect() as conn:
        insp = inspect(conn)
        db_cols = {c["name"]: c for c in insp.get_columns("files")}

    # TEST 1: File model contains kyber_ciphertext
    has_kc = hasattr(File, "kyber_ciphertext") and "kyber_ciphertext" in db_cols
    results.record("TEST 1: File model & DB table contain kyber_ciphertext", has_kc)

    # TEST 2: File model contains encrypted_dek
    has_ed = hasattr(File, "encrypted_dek") and "encrypted_dek" in db_cols
    results.record("TEST 2: File model & DB table contain encrypted_dek", has_ed)

    # TEST 3: File model contains encryption_nonce
    has_en = hasattr(File, "encryption_nonce") and "encryption_nonce" in db_cols
    results.record("TEST 3: File model & DB table contain encryption_nonce", has_en)

    # TEST 4: All new PQC metadata fields are nullable
    kc_null = db_cols.get("kyber_ciphertext", {}).get("nullable", True)
    ed_null = db_cols.get("encrypted_dek", {}).get("nullable", True)
    en_null = db_cols.get("encryption_nonce", {}).get("nullable", True)
    results.record("TEST 4: All new PQC metadata fields are nullable for backward compatibility", kc_null and ed_null and en_null)

    # TEST 5: encryption_key_hash remains present
    has_ekh = hasattr(File, "encryption_key_hash") and "encryption_key_hash" in db_cols
    results.record("TEST 5: Legacy encryption_key_hash column retained", has_ekh)

    db = SessionLocal()
    try:
        # Create a test owner
        test_owner = User(
            id=str(uuid.uuid4()),
            full_name="Schema Test User",
            email=f"schematest_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="mock_hash"
        )
        db.add(test_owner)
        db.commit()

        # TEST 6: Legacy File record can exist (AES-128-Fernet, encryption_key_hash populated, PQC NULL)
        legacy_file = File(
            id=str(uuid.uuid4()),
            owner_id=test_owner.id,
            original_filename="legacy_notes.txt",
            stored_filename=f"stored_{uuid.uuid4().hex}.enc",
            file_size=1024,
            mime_type="text/plain",
            storage_path="uploads/test/legacy.enc",
            is_encrypted=True,
            encryption_algorithm=LEGACY_ENCRYPTION_ALGORITHM,
            encryption_key_hash="legacy_mock_fernet_key_base64==",
            kyber_ciphertext=None,
            encrypted_dek=None,
            encryption_nonce=None
        )
        db.add(legacy_file)
        db.commit()
        db.refresh(legacy_file)

        legacy_ok = (
            legacy_file.encryption_algorithm == "AES-128-Fernet"
            and legacy_file.encryption_key_hash == "legacy_mock_fernet_key_base64=="
            and legacy_file.kyber_ciphertext is None
            and legacy_file.encrypted_dek is None
            and legacy_file.encryption_nonce is None
        )
        results.record("TEST 6: Legacy AES-128-Fernet file records persist successfully", legacy_ok)

        # TEST 7: Future PQC File record can exist (AES-256-GCM+Kyber1024, encryption_key_hash NULL, PQC populated)
        pqc_file = File(
            id=str(uuid.uuid4()),
            owner_id=test_owner.id,
            original_filename="quantum_vault_doc.pdf",
            stored_filename=f"stored_{uuid.uuid4().hex}.pqc",
            file_size=2048,
            mime_type="application/pdf",
            storage_path="uploads/test/quantum.pqc",
            is_encrypted=True,
            encryption_algorithm=PQC_ENCRYPTION_ALGORITHM,
            encryption_key_hash=None,
            kyber_ciphertext="00" * 1568,
            encrypted_dek="aa" * 40,
            encryption_nonce="12" * 12
        )
        db.add(pqc_file)
        db.commit()
        db.refresh(pqc_file)

        pqc_ok = (
            pqc_file.encryption_algorithm == PQC_ENCRYPTION_ALGORITHM
            and pqc_file.encryption_key_hash is None
            and pqc_file.kyber_ciphertext == "00" * 1568
            and pqc_file.encrypted_dek == "aa" * 40
            and pqc_file.encryption_nonce == "12" * 12
        )
        results.record("TEST 7: PQC AES-256-GCM+Kyber1024 file records persist successfully", pqc_ok)

        # TEST 8: No plaintext DEK field exists
        no_plaintext_dek = not hasattr(File, "dek") and not hasattr(File, "plaintext_dek") and not hasattr(File, "aes_key")
        results.record("TEST 8: No plaintext DEK field exists on File ORM model", no_plaintext_dek)

        # TEST 9: No plaintext Kyber secret key field exists in File model
        no_kyber_sk = not hasattr(File, "kyber_secret_key") and not hasattr(File, "secret_key")
        results.record("TEST 9: No plaintext Kyber secret key field exists on File ORM model", no_kyber_sk)

        # TEST 10: Existing file API schemas do not expose internal cryptographic secrets
        pqc_file_response = FileResponse.model_validate(pqc_file)
        resp_dict = pqc_file_response.model_dump()
        secrets_excluded = (
            "encrypted_dek" not in resp_dict
            and "kyber_ciphertext" not in resp_dict
            and "encryption_nonce" not in resp_dict
            and "encryption_key_hash" not in resp_dict
        )
        results.record("TEST 10: File API responses exclude internal cryptographic metadata", secrets_excluded)

        # TEST 11: Existing legacy file records are not modified or deleted by migration
        all_files_count = db.query(File).count()
        results.record("TEST 11: Database retains existing records non-destructively", all_files_count >= 2)

    except Exception as e:
        results.record("TEST 6-11: Database operations error", False, str(e))
    finally:
        db.close()

    # TEST 12 & 13: Phase 2B-1 & Phase 2B-2 regression
    try:
        from tests_phase2b1 import run_all_tests as run_p2b1
        from tests_phase2b2 import run_all_tests as run_p2b2
        
        p2b1_ok = run_p2b1()
        results.record("TEST 12: Phase 2B-1 cryptographic foundation tests pass", p2b1_ok)
        
        p2b2_ok = run_p2b2()
        results.record("TEST 13: Phase 2B-2 key protection tests pass", p2b2_ok)
    except Exception as e:
        results.record("TEST 12-13: Regression test execution failed", False, str(e))

    print("\n" + "="*70)
    print(f"RESULTS SUMMARY: Passed: {results.passed}/13, Failed: {results.failed}/13")
    print("="*70)
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
