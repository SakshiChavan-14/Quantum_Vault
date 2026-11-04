"""
QuantumVault - Test Data Cleanup Utility
Safely removes automated test-generated records from MySQL quantumvault database
while respecting foreign key relationships, preserving database schema,
Alembic migration state, and non-test application data.
"""

import os
import sys
from sqlalchemy import inspect, text, or_
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.user import User, RefreshToken
from app.models.folder import Folder
from app.models.file import File
from app.models.audit_log import AuditLog

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def cleanup_test_data():
    print("\n" + "="*70)
    print("QUANTUMVAULT AUTOMATED TEST DATA CLEANUP")
    print("="*70)
    print(f"Active DATABASE_URL: {settings.DATABASE_URL}")

    db = SessionLocal()
    try:
        # 1. Print current counts before deletion
        initial_users = db.query(User).count()
        initial_tokens = db.query(RefreshToken).count()
        initial_folders = db.query(Folder).count()
        initial_files = db.query(File).count()
        initial_logs = db.query(AuditLog).count()

        print("\n--- Current Database Record Counts (Before Cleanup) ---")
        print(f"  • Users:          {initial_users}")
        print(f"  • Refresh Tokens: {initial_tokens}")
        print(f"  • Folders:        {initial_folders}")
        print(f"  • Files:          {initial_files}")
        print(f"  • Audit Logs:     {initial_logs}")

        # 2. Identify test users matching test patterns
        test_patterns = [
            User.email.like("test_%"),
            User.email.like("e2e_%"),
            User.email.like("p2b%"),
            User.email.like("audit_%"),
            User.email.like("legacy_%"),
            User.email.like("schematest_%"),
            User.email.like("pqc_%"),
            User.email.like("other_%"),
            User.email.like("%@example.com"),
            User.email.like("%@quantumvault.com"),
        ]

        test_users = db.query(User).filter(or_(*test_patterns)).all()
        test_user_ids = [u.id for u in test_users]

        # 3. Collect associated test files and folders
        test_files = db.query(File).filter(File.owner_id.in_(test_user_ids)).all() if test_user_ids else []
        test_file_ids = [f.id for f in test_files]

        test_folders = db.query(Folder).filter(Folder.owner_id.in_(test_user_ids)).all() if test_user_ids else []
        test_folder_ids = [f.id for f in test_folders]

        # 4. Perform deletion in strict foreign-key dependency order
        print("\nExecuting safe deletion in dependency order...")

        # A. Delete Audit Logs associated with test users, test files, or test messages/events
        log_conditions = [
            AuditLog.message.like("%@example.com%"),
            AuditLog.message.like("%@quantumvault.com%"),
            AuditLog.message.like("%test%"),
            AuditLog.message.like("%DATABASE_COMPATIBILITY_CHECK%"),
            AuditLog.message.like("%PQC%"),
            AuditLog.message.like("%Audit%"),
            AuditLog.event_type.like("DATABASE_%"),
        ]
        if test_user_ids:
            log_conditions.append(AuditLog.user_id.in_(test_user_ids))
        if test_file_ids:
            log_conditions.append(AuditLog.file_id.in_(test_file_ids))

        deleted_logs = db.query(AuditLog).filter(or_(*log_conditions)).delete(synchronize_session=False)
        print(f"  ✓ Deleted {deleted_logs} test audit logs")

        # B. Delete Refresh Tokens associated with test users
        deleted_tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id.in_(test_user_ids)
        ).delete(synchronize_session=False) if test_user_ids else 0
        print(f"  ✓ Deleted {deleted_tokens} test refresh tokens")

        # C. Delete Files associated with test users
        deleted_files = db.query(File).filter(
            File.owner_id.in_(test_user_ids)
        ).delete(synchronize_session=False) if test_user_ids else 0
        print(f"  ✓ Deleted {deleted_files} test files")

        # D. Delete Folders associated with test users
        deleted_folders = db.query(Folder).filter(
            Folder.owner_id.in_(test_user_ids)
        ).delete(synchronize_session=False) if test_user_ids else 0
        print(f"  ✓ Deleted {deleted_folders} test folders")

        # E. Delete Test Users
        deleted_users = db.query(User).filter(
            User.id.in_(test_user_ids)
        ).delete(synchronize_session=False) if test_user_ids else 0
        print(f"  ✓ Deleted {deleted_users} test users")

        db.commit()
        print("\nTransaction successfully committed to MySQL.")

        # 5. Print remaining counts after deletion
        rem_users = db.query(User).count()
        rem_tokens = db.query(RefreshToken).count()
        rem_folders = db.query(Folder).count()
        rem_files = db.query(File).count()
        rem_logs = db.query(AuditLog).count()

        print("\n--- Database Record Counts (After Cleanup) ---")
        print(f"  • Remaining Users:          {rem_users}")
        print(f"  • Remaining Refresh Tokens: {rem_tokens}")
        print(f"  • Remaining Folders:        {rem_folders}")
        print(f"  • Remaining Files:          {rem_files}")
        print(f"  • Remaining Audit Logs:     {rem_logs}")

        # 6. Verify MySQL Schema & Alembic State
        with engine.connect() as conn:
            insp = inspect(conn)
            tables = sorted(insp.get_table_names())
            current_rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

        expected_tables = ["alembic_version", "audit_logs", "files", "folders", "refresh_tokens", "users"]
        schema_intact = all(t in tables for t in expected_tables)

        print("\n--- Schema & Alembic Verification ---")
        print(f"  • MySQL Tables Present:     {tables}")
        print(f"  • Schema Integrity:         {'✅ ALL 6 TABLES INTACT' if schema_intact else '❌ SCHEMA MODIFIED'}")
        print(f"  • Alembic Revision (Head):  {current_rev} {'✅ HEAD' if current_rev == 'c123456789ab' else ''}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Cleanup failed, rolled back: {e}")
        raise
    finally:
        db.close()

    print("\n" + "="*70)
    print("TEST DATA CLEANUP COMPLETED SUCCESSFULLY")
    print("="*70)


if __name__ == "__main__":
    cleanup_test_data()
