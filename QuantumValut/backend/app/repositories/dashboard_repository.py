import json
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.models.user import User
from app.models.file import File
from app.models.folder import Folder
from app.models.audit_log import AuditLog

class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_summary(self, user_id: str) -> dict:
        stmt = select(User).where(User.id == user_id)
        user = self.db.execute(stmt).scalar_one_or_none()
        
        if not user:
            return {}
            
        total_files = self.db.execute(
            select(func.count(File.id)).where(File.owner_id == user_id, File.deleted_at.is_(None))
        ).scalar() or 0

        total_folders = self.db.execute(
            select(func.count(Folder.id)).where(Folder.owner_id == user_id, Folder.deleted_at.is_(None))
        ).scalar() or 0

        favorites = self.db.execute(
            select(func.count(File.id)).where(File.owner_id == user_id, File.is_favorite == True, File.deleted_at.is_(None))
        ).scalar() or 0

        shared_files = self.db.execute(
            select(func.count(File.id)).where(File.owner_id == user_id, File.is_shared == True, File.deleted_at.is_(None))
        ).scalar() or 0

        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "is_verified": user.is_verified,
            "statistics": {
                "total_files": total_files,
                "total_folders": total_folders,
                "favorites": favorites,
                "shared_files": shared_files
            }
        }

    def get_storage_summary(self, user_id: str) -> dict:
        total_quota = 5 * 1024 * 1024 * 1024  # 5 GB quota
        used_storage = self.db.execute(
            select(func.coalesce(func.sum(File.file_size), 0)).where(File.owner_id == user_id, File.deleted_at.is_(None))
        ).scalar() or 0
        
        available = max(0, total_quota - used_storage)
        pct = round((used_storage / total_quota * 100), 2) if total_quota > 0 else 0.0

        return {
            "used_storage": used_storage,
            "available_storage": available,
            "total_storage": total_quota,
            "percentage_used": pct
        }

    def get_recent_files(self, user_id: str) -> list:
        stmt = (
            select(File)
            .where(File.owner_id == user_id, File.deleted_at.is_(None))
            .order_by(File.created_at.desc())
            .limit(10)
        )
        files = self.db.execute(stmt).scalars().all()
        return [
            {
                "id": f.id,
                "name": f.original_filename,
                "size": f.file_size,
                "mime_type": f.mime_type,
                "created_at": f.created_at,
                "updated_at": f.updated_at,
                "is_starred": f.is_favorite,
                "encryption_algorithm": f.encryption_algorithm,
                "file_hash": f.file_hash,
            }
            for f in files
        ]

    def get_recent_activity(self, user_id: str) -> list:
        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.created_at))
            .limit(10)
        )
        logs = self.db.execute(stmt).scalars().all()
        if logs:
            activities = []
            for log in logs:
                target = None
                if log.file and log.file.original_filename:
                    target = log.file.original_filename
                elif log.metadata_json:
                    try:
                        meta = json.loads(log.metadata_json)
                        target = meta.get("filename") or meta.get("new_filename")
                    except Exception:
                        pass

                action_name = log.event_type.replace("_", " ").lower()
                if "upload" in action_name:
                    action_name = "Uploaded"
                elif "download" in action_name:
                    action_name = "Downloaded"
                elif "rename" in action_name:
                    action_name = "Renamed"
                elif "move" in action_name:
                    action_name = "Moved"
                elif "delete" in action_name:
                    action_name = "Deleted"
                elif "login" in action_name:
                    action_name = "Logged In"
                elif "register" in action_name:
                    action_name = "Account Created"
                else:
                    action_name = log.event_type.replace("_", " ").title()

                activities.append({
                    "id": str(log.id),
                    "action": action_name,
                    "target_name": target,
                    "created_at": log.created_at
                })
            return activities

        # Fallback to recent files if no audit logs exist
        stmt = (
            select(File)
            .where(File.owner_id == user_id, File.deleted_at.is_(None))
            .order_by(desc(File.created_at))
            .limit(5)
        )
        files = self.db.execute(stmt).scalars().all()
        return [
            {
                "id": f"act_{f.id}",
                "action": "Uploaded",
                "target_name": f.original_filename,
                "created_at": f.created_at
            }
            for f in files
        ]
