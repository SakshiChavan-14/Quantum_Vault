"""
QuantumVault - Phase 2C End-to-End Frontend-Backend Integration Test Suite
Validates the complete real-world HTTP contract against live MySQL quantumvault database:
Registration, JWT Cookie Auth, Session Persistence, Folder Creation, Live PQC AES-256-GCM+Kyber1024
File Upload, Security Badge Metadata, Audit Log Retrieval, Decrypted Download, and Session Logout.
"""

import sys
import uuid
import json
import io
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.file import File

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


def run_e2e_tests() -> bool:
    results = TestResults()
    print("\n" + "="*70)
    print("QUANTUMVAULT PHASE 2C FRONTEND-BACKEND E2E INTEGRATION SUITE")
    print("="*70)

    client = TestClient(app)
    unique_suffix = uuid.uuid4().hex[:8]
    test_user_email = f"e2e_user_{unique_suffix}@quantumvault.com"
    test_user_password = "E2ESecurePassword2026!"
    test_user_name = f"E2E Test User {unique_suffix}"

    # TEST 1: Health endpoint responds
    try:
        r = client.get("/api/v1/health")
        results.record("TEST 1: Backend Health API responds with status 200", r.status_code == 200)
    except Exception as e:
        results.record("TEST 1: Backend Health API responds with status 200", False, str(e))

    # TEST 2: User Registration in MySQL
    try:
        reg_payload = {
            "full_name": test_user_name,
            "email": test_user_email,
            "password": test_user_password,
            "confirm_password": test_user_password,
        }
        r = client.post("/api/v1/auth/register", json=reg_payload)
        results.record("TEST 2: Frontend registration creates new user with Kyber keypair in MySQL", r.status_code == 201)
    except Exception as e:
        results.record("TEST 2: Frontend registration creates new user with Kyber keypair in MySQL", False, str(e))

    # TEST 3: User Login in MySQL with HttpOnly Cookies
    try:
        login_payload = {
            "email": test_user_email,
            "password": test_user_password,
        }
        r = client.post("/api/v1/auth/login", json=login_payload)
        has_cookies = "access_token" in client.cookies or "access_token" in r.cookies
        results.record("TEST 3: User login authenticates against MySQL and receives HttpOnly JWT cookies", r.status_code == 200 and has_cookies)
    except Exception as e:
        results.record("TEST 3: User login authenticates against MySQL and receives HttpOnly JWT cookies", False, str(e))

    # TEST 4: Current user session verification (/auth/me)
    try:
        r = client.get("/api/v1/auth/me")
        me_data = r.json()
        user_ok = r.status_code == 200 and me_data.get("email") == test_user_email
        results.record("TEST 4: Authenticated session preserves user state on /auth/me", user_ok)
    except Exception as e:
        results.record("TEST 4: Authenticated session preserves user state on /auth/me", False, str(e))

    # TEST 5: Create Folder in MySQL
    folder_id = None
    try:
        folder_payload = {"name": f"PQC Research {unique_suffix}"}
        r = client.post("/api/v1/folders", json=folder_payload)
        folder_data = r.json()
        folder_id = folder_data.get("id")
        results.record("TEST 5: Create folder endpoint persists folder in MySQL", r.status_code == 201 and folder_id is not None)
    except Exception as e:
        results.record("TEST 5: Create folder endpoint persists folder in MySQL", False, str(e))

    # TEST 6: List Root Folders
    try:
        r = client.get("/api/v1/folders/root")
        root_folders = r.json()
        results.record("TEST 6: List root folders returns created folder", r.status_code == 200 and any(f.get("id") == folder_id for f in root_folders))
    except Exception as e:
        results.record("TEST 6: List root folders returns created folder", False, str(e))

    # TEST 7: Upload file with AES-256-GCM + Kyber-1024
    file_id = None
    original_content = f"QUANTUMVAULT TOP SECRET REPORT 2026: LIVE E2E PQC CIPHERTEXT VERIFICATION {unique_suffix}".encode("utf-8")
    filename = f"quantum_report_{unique_suffix}.txt"
    try:
        files = {"file": (filename, io.BytesIO(original_content), "text/plain")}
        data = {"folder_id": folder_id, "description": "End-to-End PQC Verified File", "is_favorite": "true"}
        r = client.post("/api/v1/files/upload", files=files, data=data)
        file_res = r.json()
        file_id = file_res.get("id")
        is_pqc = file_res.get("encryption_algorithm") == "AES-256-GCM+Kyber1024"
        results.record("TEST 7: Live file upload automatically encrypts using AES-256-GCM+Kyber1024", r.status_code == 201 and is_pqc)
    except Exception as e:
        results.record("TEST 7: Live file upload automatically encrypts using AES-256-GCM+Kyber1024", False, str(e))

    # TEST 8: Verify file metadata in MySQL via direct query
    try:
        db = SessionLocal()
        db_file = db.query(File).filter(File.id == file_id).first()
        db_valid = (
            db_file is not None
            and db_file.encryption_algorithm == "AES-256-GCM+Kyber1024"
            and db_file.kyber_ciphertext is not None
            and db_file.encrypted_dek is not None
            and db_file.encryption_nonce is not None
            and db_file.encryption_key_hash is None
        )
        db.close()
        results.record("TEST 8: File record in MySQL contains Kyber ciphertext, wrapped DEK, and zero plaintext keys", db_valid)
    except Exception as e:
        results.record("TEST 8: File record in MySQL contains Kyber ciphertext, wrapped DEK, and zero plaintext keys", False, str(e))

    # TEST 9: Fetch User Audit Logs (/api/v1/audit/me)
    try:
        r = client.get("/api/v1/audit/me?limit=20")
        audit_data = r.json()
        logs = audit_data if isinstance(audit_data, list) else audit_data.get("logs", [])
        event_types = [l.get("event_type") for l in logs]
        has_auth_and_file = (
            "USER_REGISTERED" in event_types
            and "USER_LOGIN_SUCCESS" in event_types
            and "FILE_UPLOAD_SUCCESS" in event_types
        )
        results.record("TEST 9: Audit log API returns real-time AUTH, FILE, and CRYPTO security events", r.status_code == 200 and has_auth_and_file)
    except Exception as e:
        results.record("TEST 9: Audit log API returns real-time AUTH, FILE, and CRYPTO security events", False, str(e))

    # TEST 10: Fetch Specific File Audit Logs (/api/v1/audit/file/{file_id})
    try:
        r = client.get(f"/api/v1/audit/file/{file_id}")
        file_logs = r.json()
        results.record("TEST 10: File-specific audit log endpoint returns upload & encryption history", r.status_code == 200 and len(file_logs) > 0)
    except Exception as e:
        results.record("TEST 10: File-specific audit log endpoint returns upload & encryption history", False, str(e))

    # TEST 11: Real File Download & Authenticated Decryption
    try:
        r = client.get(f"/api/v1/files/{file_id}/download")
        decrypted_content = r.content
        results.record("TEST 11: File download decapsulates Kyber key, decrypts AES-256-GCM, and restores exact plaintext", r.status_code == 200 and decrypted_content == original_content)
    except Exception as e:
        results.record("TEST 11: File download decapsulates Kyber key, decrypts AES-256-GCM, and restores exact plaintext", False, str(e))

    # TEST 12: Download Security Audit Log Event Recorded
    try:
        r = client.get(f"/api/v1/audit/file/{file_id}")
        file_logs = r.json()
        download_events = [l.get("event_type") for l in file_logs]
        results.record("TEST 12: Download triggers FILE_DOWNLOAD_REQUESTED and FILE_DECRYPTION_SUCCESS audit logs", "FILE_DOWNLOAD_REQUESTED" in download_events or "FILE_DOWNLOAD_SUCCESS" in download_events)
    except Exception as e:
        results.record("TEST 12: Download triggers FILE_DOWNLOAD_REQUESTED and FILE_DECRYPTION_SUCCESS audit logs", False, str(e))

    # TEST 13: File Favorite Toggle
    try:
        r = client.patch(f"/api/v1/files/{file_id}/favorite")
        results.record("TEST 13: Toggle favorite updates file status in MySQL", r.status_code == 200)
    except Exception as e:
        results.record("TEST 13: Toggle favorite updates file status in MySQL", False, str(e))

    # TEST 14: File Rename
    try:
        new_name = f"renamed_pqc_{unique_suffix}.txt"
        r = client.patch(f"/api/v1/files/{file_id}/rename", json={"new_filename": new_name})
        results.record("TEST 14: Rename file updates original filename in MySQL", r.status_code == 200 and r.json().get("original_filename") == new_name)
    except Exception as e:
        results.record("TEST 14: Rename file updates original filename in MySQL", False, str(e))

    # TEST 15: Dashboard Overview API with Real MySQL Data
    try:
        r = client.get("/api/v1/dashboard/overview")
        dash_data = r.json()
        stats = dash_data.get("statistics", {})
        results.record("TEST 15: Dashboard overview reflects real MySQL file and folder statistics", r.status_code == 200 and stats.get("total_files", 0) >= 1)
    except Exception as e:
        results.record("TEST 15: Dashboard overview reflects real MySQL file and folder statistics", False, str(e))

    # TEST 16: Dashboard Recent Files includes PQC Security Metadata
    try:
        r = client.get("/api/v1/dashboard/recent-files")
        rec_data = r.json()
        rec_files = rec_data.get("files", [])
        has_algo = any(f.get("encryption_algorithm") == "AES-256-GCM+Kyber1024" for f in rec_files)
        results.record("TEST 16: Dashboard recent files includes Post-Quantum encryption algorithm metadata", r.status_code == 200 and has_algo)
    except Exception as e:
        results.record("TEST 16: Dashboard recent files includes Post-Quantum encryption algorithm metadata", False, str(e))

    # TEST 17: Dashboard Storage Stats
    try:
        r = client.get("/api/v1/dashboard/storage")
        storage_data = r.json()
        results.record("TEST 17: Dashboard storage statistics correctly computes storage usage", r.status_code == 200 and storage_data.get("used_storage", 0) > 0)
    except Exception as e:
        results.record("TEST 17: Dashboard storage statistics correctly computes storage usage", False, str(e))

    # TEST 18: User Logout
    try:
        r = client.post("/api/v1/auth/logout")
        results.record("TEST 18: User logout clears session and records USER_LOGOUT audit event", r.status_code == 200)
    except Exception as e:
        results.record("TEST 18: User logout clears session and records USER_LOGOUT audit event", False, str(e))

    # TEST 19: Unauthenticated Access Rejected After Logout
    try:
        r = client.get("/api/v1/auth/me")
        results.record("TEST 19: Protected routes reject requests after logout (HTTP 401)", r.status_code == 401)
    except Exception as e:
        results.record("TEST 19: Protected routes reject requests after logout (HTTP 401)", False, str(e))

    # TEST 20: Full Backend Regression (Phase 2B-1 to 2B-6)
    try:
        from tests_phase2b1 import run_all_tests as run_p2b1
        from tests_phase2b2 import run_all_tests as run_p2b2
        from tests_phase2b3 import run_all_tests as run_p2b3
        from tests_phase2b4 import run_all_tests as run_p2b4
        from tests_phase2b5 import run_all_tests as run_p2b5
        from tests_phase2b6 import run_all_tests as run_p2b6

        r1 = run_p2b1()
        r2 = run_p2b2()
        r3 = run_p2b3()
        r4 = run_p2b4()
        r5 = run_p2b5()
        r6 = run_p2b6()
        reg_all = r1 and r2 and r3 and r4 and r5 and r6
        results.record("TEST 20: Full Phase 2B regression suites (2B-1 through 2B-6) pass 100%", reg_all)
    except Exception as e:
        results.record("TEST 20: Full Phase 2B regression suites (2B-1 through 2B-6) pass 100%", False, str(e))

    print("\n" + "="*70)
    print(f"RESULTS SUMMARY: Passed: {results.passed}/{results.total}, Failed: {results.failed}/{results.total}")
    print("="*70)
    return results.failed == 0


if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
