"""
QuantumVault - Phase 2B-2 Test Suite
Server-Side Master Key & User Kyber Key Persistence Verification
Validates: CRYPTO_MASTER_KEY configuration, KeyProtectionService, User ORM fields,
User registration provisioning, API schema exclusion, and Existing User lazy provisioning.
"""

import sys
import uuid
from cryptography.fernet import Fernet

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.services.kyber_service import KyberService
from app.services.key_protection_service import KeyProtectionService
from app.services.auth_service import AuthService
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import RegisterRequest, UserResponse
from app.exceptions.SecurityExceptions import (
    MasterKeyConfigurationError,
    KeyProtectionError,
    UserKyberKeyUnavailable
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
    print("QUANTUMVAULT PHASE 2B-2 SERVER-SIDE KEY PROTECTION TESTS")
    print("="*70)

    # TEST 1: CRYPTO_MASTER_KEY loads successfully from test environment
    try:
        master_key = settings.CRYPTO_MASTER_KEY
        cipher = KeyProtectionService._get_fernet_cipher()
        results.record(
            "TEST 1: CRYPTO_MASTER_KEY configuration validation",
            bool(master_key) and isinstance(cipher, Fernet)
        )
    except Exception as e:
        results.record("TEST 1: CRYPTO_MASTER_KEY configuration validation", False, str(e))

    # TEST 2: A Kyber secret key can be encrypted
    pk_hex, sk_hex = KyberService.generate_keypair()
    try:
        encrypted_sk = KeyProtectionService.encrypt_kyber_secret_key(sk_hex)
        results.record(
            "TEST 2: Kyber secret key encryption under master key",
            bool(encrypted_sk) and isinstance(encrypted_sk, str) and len(encrypted_sk) > 0
        )
    except Exception as e:
        results.record("TEST 2: Kyber secret key encryption under master key", False, str(e))

    # TEST 3: The encrypted Kyber secret key can be decrypted to the exact original value
    try:
        decrypted_sk = KeyProtectionService.decrypt_kyber_secret_key(encrypted_sk)
        results.record(
            "TEST 3: Encrypted Kyber secret key exact round-trip decryption",
            decrypted_sk == sk_hex
        )
    except Exception as e:
        results.record("TEST 3: Encrypted Kyber secret key exact round-trip decryption", False, str(e))

    # TEST 4: Encrypted database value is different from plaintext secret key
    try:
        results.record(
            "TEST 4: Plaintext Kyber secret key is never stored raw",
            encrypted_sk != sk_hex and sk_hex not in encrypted_sk
        )
    except Exception as e:
        results.record("TEST 4: Plaintext Kyber secret key is never stored raw", False, str(e))

    # TEST 5: Malformed encrypted secret key fails safely
    try:
        malformed_caught = False
        try:
            KeyProtectionService.decrypt_kyber_secret_key("malformed_garbage_encrypted_token")
        except KeyProtectionError:
            malformed_caught = True
        results.record("TEST 5: Malformed encrypted secret key fails safely", malformed_caught)
    except Exception as e:
        results.record("TEST 5: Malformed encrypted secret key fails safely", False, str(e))

    # TEST 6: Wrong master key cannot correctly decrypt the stored secret key
    try:
        wrong_master_key = Fernet.generate_key().decode("utf-8")
        wrong_caught = False
        try:
            KeyProtectionService.decrypt_kyber_secret_key(encrypted_sk, master_key=wrong_master_key)
        except KeyProtectionError:
            wrong_caught = True
        results.record("TEST 6: Wrong master key fails closed on decryption", wrong_caught)
    except Exception as e:
        results.record("TEST 6: Wrong master key fails closed on decryption", False, str(e))

    # TEST 7 & 8: New user registration provisioning & plaintext absence in DB
    db = SessionLocal()
    try:
        test_email = f"test_pqc_user_{uuid.uuid4().hex[:8]}@example.com"
        auth_service = AuthService(AuthRepository(db))
        req = RegisterRequest(
            full_name="PQC User Test",
            email=test_email,
            password="SecurePassword123!",
            confirm_password="SecurePassword123!"
        )
        new_user = auth_service.register_user(req)

        # Refresh from database directly to inspect stored fields
        db_user = db.query(User).filter(User.id == new_user.id).first()
        
        has_public_key = bool(db_user.kyber_public_key and len(db_user.kyber_public_key) >= 3000)
        has_encrypted_secret = bool(db_user.kyber_secret_key_encrypted and len(db_user.kyber_secret_key_encrypted) > 0)
        
        # Verify secret key decrypts correctly
        recovered_sk = KeyProtectionService.get_user_kyber_secret_key(db_user)
        valid_sk = bool(recovered_sk and len(recovered_sk) >= 6000)

        results.record(
            "TEST 7: User registration automatically provisions Kyber keypair",
            has_public_key and has_encrypted_secret and valid_sk
        )

        # TEST 8: Verify no plaintext secret key is stored on user model or table
        user_dict_vals = [str(v) for v in db_user.__dict__.values()]
        plaintext_in_db = any(recovered_sk in v for v in user_dict_vals if v != recovered_sk)
        has_no_raw_sk_col = not hasattr(User, "kyber_secret_key")

        results.record(
            "TEST 8: Plaintext Kyber secret key is never saved in database",
            has_no_raw_sk_col and not plaintext_in_db
        )

        # TEST 9: User API response schema does not expose the Kyber secret key
        user_response = UserResponse.model_validate(db_user)
        response_dict = user_response.model_dump()
        response_keys = list(response_dict.keys())
        results.record(
            "TEST 9: Public User API response schema excludes Kyber secret key",
            "kyber_secret_key_encrypted" not in response_keys and "kyber_secret_key" not in response_keys
        )

        # TEST 10: Existing user without Kyber keys remains compatible & lazily provisionable
        legacy_user = User(
            id=str(uuid.uuid4()),
            full_name="Legacy User Without Kyber",
            email=f"legacy_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="mock_hash",
            kyber_public_key=None,
            kyber_secret_key_encrypted=None
        )
        db.add(legacy_user)
        db.commit()
        db.refresh(legacy_user)

        # Check that lazy provisioning works smoothly without breaking user
        prov_pk, prov_sk = KeyProtectionService.get_or_provision_user_kyber_keys(legacy_user, db_session=db)
        db.refresh(legacy_user)
        
        results.record(
            "TEST 10: Existing user without Kyber keys compatible with lazy provisioning",
            bool(legacy_user.kyber_public_key) and bool(legacy_user.kyber_secret_key_encrypted) and len(prov_sk) > 0
        )

    except Exception as e:
        results.record("TEST 7-10: User provisioning & schema validation", False, str(e))
    finally:
        db.close()

    print("\n" + "="*70)
    print(f"RESULTS SUMMARY: Passed: {results.passed}/10, Failed: {results.failed}/10")
    print("="*70)
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
