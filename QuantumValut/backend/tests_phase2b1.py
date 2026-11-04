"""
QuantumVault - Phase 2B-1 Test Suite
Cryptographic Foundation Verification
Validates: AES-256-GCM, Kyber1024 KEM, HKDF-SHA256, AES Key Wrap, Full PQC Pipeline, and Legacy Fernet
"""

import os
import sys

from app.services.pqc_crypto_service import (
    PQCCryptoService,
    generate_dek,
    generate_nonce,
    encrypt_aes_gcm,
    decrypt_aes_gcm,
    derive_kek,
    wrap_dek,
    unwrap_dek,
    AES_KEY_SIZE_BYTES,
    GCM_NONCE_SIZE_BYTES,
    KEK_SIZE_BYTES,
    PQC_CRYPTO_VERSION,
    PQC_ENCRYPTION_ALGORITHM,
)
from app.services.kyber_service import KyberService
from app.services.encryption_service import EncryptionService
from app.services.hash_service import HashService
from app.exceptions.FileExceptions import DecryptionFailed, EncryptionFailed


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
    print("QUANTUMVAULT PHASE 2B-1 CRYPTOGRAPHIC FOUNDATION TESTS")
    print("="*70)

    # TEST 1: AES-256-GCM encrypt -> decrypt roundtrip
    try:
        sample_plaintext = b"Confidential QuantumVault Data Block 2026."
        dek = generate_dek()
        enc = encrypt_aes_gcm(sample_plaintext, dek)
        decrypted = decrypt_aes_gcm(enc["ciphertext"], dek, enc["nonce"])
        results.record("TEST 1: AES-256-GCM encrypt -> decrypt roundtrip", decrypted == sample_plaintext)
    except Exception as e:
        results.record("TEST 1: AES-256-GCM encrypt -> decrypt roundtrip", False, str(e))

    # TEST 2: Every generated DEK is exactly 32 bytes
    try:
        deks = [generate_dek() for _ in range(25)]
        all_32_bytes = all(isinstance(k, bytes) and len(k) == AES_KEY_SIZE_BYTES for k in deks)
        all_unique = len(set(deks)) == 25
        results.record("TEST 2: DEK generation (exactly 32 unique bytes)", all_32_bytes and all_unique)
    except Exception as e:
        results.record("TEST 2: DEK generation (exactly 32 unique bytes)", False, str(e))

    # TEST 3: Every encryption uses a valid fresh nonce (12 bytes)
    try:
        dek = generate_dek()
        nonces = [encrypt_aes_gcm(b"Data", dek)["nonce"] for _ in range(25)]
        all_12_bytes = all(isinstance(n, bytes) and len(n) == GCM_NONCE_SIZE_BYTES for n in nonces)
        all_unique = len(set(nonces)) == 25
        results.record("TEST 3: Fresh 12-byte GCM nonces per encryption", all_12_bytes and all_unique)
    except Exception as e:
        results.record("TEST 3: Fresh 12-byte GCM nonces per encryption", False, str(e))

    # TEST 4: Tampered AES-GCM ciphertext fails decryption
    try:
        dek = generate_dek()
        enc = encrypt_aes_gcm(b"Secret Document", dek)
        # Tamper with the ciphertext payload
        corrupted_ct = bytearray(enc["ciphertext"])
        corrupted_ct[0] ^= 0xFF
        tamper_caught = False
        try:
            decrypt_aes_gcm(bytes(corrupted_ct), dek, enc["nonce"])
        except DecryptionFailed:
            tamper_caught = True
        results.record("TEST 4: Tampered AES-GCM ciphertext fails closed", tamper_caught)
    except Exception as e:
        results.record("TEST 4: Tampered AES-GCM ciphertext fails closed", False, str(e))

    # TEST 5: Kyber encapsulate -> decapsulate produces matching shared secrets
    try:
        pk_hex, sk_hex = KyberService.generate_keypair()
        ct_hex, ss_enc = KyberService.encapsulate(pk_hex)
        ss_dec = KyberService.decapsulate(ct_hex, sk_hex)
        results.record("TEST 5: Kyber1024 encapsulation & decapsulation shared secret match", ss_enc == ss_dec and len(ss_enc) == 32)
    except Exception as e:
        results.record("TEST 5: Kyber1024 encapsulation & decapsulation shared secret match", False, str(e))

    # TEST 6: HKDF produces matching KEKs for the same shared secret
    try:
        shared_secret = os.urandom(32)
        kek1 = derive_kek(shared_secret)
        kek2 = derive_kek(shared_secret)
        different_kek = derive_kek(os.urandom(32))
        results.record("TEST 6: HKDF-SHA256 reproducible KEK derivation (32 bytes)", kek1 == kek2 and len(kek1) == KEK_SIZE_BYTES and kek1 != different_kek)
    except Exception as e:
        results.record("TEST 6: HKDF-SHA256 reproducible KEK derivation (32 bytes)", False, str(e))

    # TEST 7: Wrap DEK -> unwrap DEK returns the exact original 32-byte DEK
    try:
        kek = os.urandom(KEK_SIZE_BYTES)
        dek = generate_dek()
        wrapped = wrap_dek(kek, dek)
        unwrapped = unwrap_dek(kek, wrapped)
        # Test wrong KEK unwrap failure
        wrong_kek = os.urandom(KEK_SIZE_BYTES)
        wrong_caught = False
        try:
            unwrap_dek(wrong_kek, wrapped)
        except DecryptionFailed:
            wrong_caught = True
        results.record("TEST 7: AES Key Wrap / Unwrap with wrong KEK rejection", unwrapped == dek and len(wrapped) == 40 and wrong_caught)
    except Exception as e:
        results.record("TEST 7: AES Key Wrap / Unwrap with wrong KEK rejection", False, str(e))

    # TEST 8: Full new crypto pipeline end-to-end round trip
    try:
        original_file_bytes = b"TOP SECRET: Post-Quantum File Content For QuantumVault Storage System (2026)."
        user_pk, user_sk = KyberService.generate_keypair()
        
        # 1. Full Encrypt Pipeline
        encrypted_bundle = PQCCryptoService.encrypt_file_pqc(original_file_bytes, user_pk)
        
        # Verify bundle contents
        assert "encrypted_file_bytes" in encrypted_bundle
        assert "nonce" in encrypted_bundle
        assert "kyber_ciphertext" in encrypted_bundle
        assert "wrapped_dek" in encrypted_bundle
        assert "file_hash" in encrypted_bundle
        assert encrypted_bundle["algorithm"] == PQC_ENCRYPTION_ALGORITHM
        assert encrypted_bundle["version"] == PQC_CRYPTO_VERSION

        # 2. Full Decrypt Pipeline
        recovered_file_bytes = PQCCryptoService.decrypt_file_pqc(
            encrypted_file_bytes=encrypted_bundle["encrypted_file_bytes"],
            nonce=encrypted_bundle["nonce"],
            kyber_ciphertext=encrypted_bundle["kyber_ciphertext"],
            wrapped_dek=encrypted_bundle["wrapped_dek"],
            recipient_kyber_secret_key=user_sk,
        )

        # 3. Verify SHA-256 integrity match
        recovered_hash = HashService.calculate_file_hash(recovered_file_bytes)
        integrity_ok = (recovered_hash == encrypted_bundle["file_hash"])

        results.record("TEST 8: Full V2 PQC Pipeline (AES-256-GCM + Kyber1024 + HKDF + Key Wrap)", recovered_file_bytes == original_file_bytes and integrity_ok)
    except Exception as e:
        results.record("TEST 8: Full V2 PQC Pipeline (AES-256-GCM + Kyber1024 + HKDF + Key Wrap)", False, str(e))

    # TEST 9: Legacy Fernet functionality remains untouched
    try:
        legacy_data = b"Legacy file encrypted under Phase 3 Fernet format."
        enc_legacy, key, algo = EncryptionService.encrypt_file(legacy_data)
        assert algo == "AES-128-Fernet"
        dec_legacy = EncryptionService.decrypt_file(enc_legacy, key)
        results.record("TEST 9: Legacy Fernet AES-128 backward compatibility", dec_legacy == legacy_data)
    except Exception as e:
        results.record("TEST 9: Legacy Fernet AES-128 backward compatibility", False, str(e))

    print("\n" + "="*70)
    print(f"RESULTS SUMMARY: Passed: {results.passed}/9, Failed: {results.failed}/9")
    print("="*70)
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
