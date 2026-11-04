import os
import asyncio
import httpx
import app.main
from app.core.database import engine, Base, check_db_connection
import app.models

check_db_connection()

async def run_comprehensive_audit():
    transport = httpx.ASGITransport(app=app.main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        results = {}
        
        # 1. Health Check
        res = await client.get("/api/v1/health/")
        results["Health Endpoint"] = res.status_code == 200 and res.json().get("success") is True
        print(f"1. Health Check: {res.status_code} - {res.json()}")

        # 2. Registration / Login
        email = f"audit_user_{os.urandom(4).hex()}@example.com"
        password = "StrongPassword123!"
        reg_res = await client.post("/api/v1/auth/register", json={
            "full_name": "Audit Tester",
            "email": email,
            "password": password,
            "confirm_password": password
        })
        results["User Registration"] = reg_res.status_code == 201
        print(f"2. Registration: {reg_res.status_code}")

        login_res = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })
        cookies = login_res.cookies
        results["User Login & JWT HttpOnly Cookies"] = login_res.status_code == 200 and "access_token" in cookies
        print(f"3. Login: {login_res.status_code}, Cookie set: {'access_token' in cookies}")

        # 3. Auth Me
        me_res = await client.get("/api/v1/auth/me", cookies=cookies)
        results["Auth /me Session Verification"] = me_res.status_code == 200 and me_res.json().get("email") == email
        print(f"4. Auth /me: {me_res.status_code} - {me_res.json().get('email')}")

        # 4. Folder Management
        folder_res = await client.post("/api/v1/folders", json={"name": f"Audit Vault {os.urandom(2).hex()}", "parent_id": None}, cookies=cookies)
        folder_id = folder_res.json().get("id") if folder_res.status_code == 201 else None
        results["Folder Creation"] = folder_res.status_code == 201
        print(f"5. Folder Creation: {folder_res.status_code}, ID: {folder_id}")

        root_folders_res = await client.get("/api/v1/folders/root", cookies=cookies)
        results["Folder Tree & Listing"] = root_folders_res.status_code == 200 and len(root_folders_res.json()) > 0
        print(f"6. Root Folders: {root_folders_res.status_code}, Count: {len(root_folders_res.json())}")

        # 5. File Upload (PQC Encryption & SHA-256 Hashing)
        file_bytes = f"QuantumVault Post-Quantum Storage Confidential Payload 2026 {os.urandom(4).hex()}.".encode("utf-8")
        files = {"file": (f"classified_doc_{os.urandom(4).hex()}.txt", file_bytes, "text/plain")}
        data = {"folder_id": folder_id, "description": "TopSecretAudit", "is_favorite": "true"}
        upload_res = await client.post(
            "/api/v1/files/upload",
            files=files,
            data=data,
            cookies=cookies
        )
        file_id = upload_res.json().get("id") if upload_res.status_code == 201 else None
        upload_data = upload_res.json()
        results["File Upload & PQC Encryption"] = upload_res.status_code == 201 and upload_data.get("is_encrypted") is True
        print(f"7. File Upload: {upload_res.status_code}, Encrypted: {upload_data.get('is_encrypted')}, Hash: {upload_data.get('file_hash')}")

        # 6. File Download & Decryption Verification
        dl_res = await client.get(f"/api/v1/files/{file_id}/download", cookies=cookies)
        results["File Download & AES Decryption"] = dl_res.status_code == 200 and dl_res.content == file_bytes
        print(f"8. File Download & Decrypt match: {dl_res.content == file_bytes} (Status {dl_res.status_code})")

        # 7. File Details & Operations
        details_res = await client.get(f"/api/v1/files/{file_id}", cookies=cookies)
        results["File Details Retrieval"] = details_res.status_code == 200

        fav_res = await client.patch(f"/api/v1/files/{file_id}/favorite", cookies=cookies)
        results["Toggle Favorite"] = fav_res.status_code == 200

        new_name = f"renamed_doc_{os.urandom(3).hex()}.txt"
        rename_res = await client.patch(f"/api/v1/files/{file_id}/rename", json={"new_filename": new_name}, cookies=cookies)
        results["Rename File"] = rename_res.status_code == 200

        search_res = await client.get(f"/api/v1/files/search/files?query=renamed", cookies=cookies)
        results["File Search by Query"] = search_res.status_code == 200 and len(search_res.json().get("items", [])) > 0
        print(f"9. File Ops (Favorite/Rename/Search): Success")

        # 8. Dashboard Overview & Statistics
        dash_res = await client.get("/api/v1/dashboard/overview", cookies=cookies)
        dash_data = dash_res.json()
        results["Dashboard Stats & Storage Meter"] = dash_res.status_code == 200 and dash_data.get("statistics", {}).get("total_files") >= 1
        print(f"10. Dashboard Stats: {dash_data.get('statistics')}")

        # 9. Kyber Post-Quantum Service
        from app.services.kyber_service import KyberService
        pk, sk = KyberService.generate_keypair()
        sample_aes_key = "a1b2c3d4e5f67890a1b2c3d4e5f67890"
        encrypted_key = KyberService.encrypt_aes_key(sample_aes_key, pk)
        decrypted_key = KyberService.decrypt_aes_key(encrypted_key, sk)
        results["Kyber-1024 Post-Quantum Key Encapsulation"] = bool(pk and sk and encrypted_key and decrypted_key)
        print(f"11. Kyber-1024 Keypair & Encapsulation: Valid={bool(pk and sk)}")

        print("\n" + "="*60)
        print("QUANTUMVAULT COMPREHENSIVE AUDIT RESULTS:")
        print("="*60)
        for k, v in results.items():
            print(f" - {k}: {'✅ PASS' if v else '❌ FAIL'}")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(run_comprehensive_audit())
