import datetime
from fastapi import Response
from app.repositories.auth_repository import AuthRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.audit_log_service import AuditLogService
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token, verify_token
from app.core.cookies import set_auth_cookies, clear_auth_cookies
from app.exceptions import InvalidCredentials, UserAlreadyExists, UserNotFound, AuthenticationError

from app.services.kyber_service import KyberService
from app.services.key_protection_service import KeyProtectionService


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repo = repository
        self.audit_service = AuditLogService(AuditLogRepository(self.repo.db))

    def register_user(self, payload: RegisterRequest):
        existing_user = self.repo.get_user_by_email(payload.email)
        if existing_user:
            self.audit_service.log_auth_event(
                event_type="USER_REGISTRATION_FAILED",
                status="FAILURE",
                message=f"Registration failed: user with email '{payload.email}' already exists",
                metadata={"email": payload.email}
            )
            raise UserAlreadyExists("User with this email already exists")

        # Provision Kyber-1024 Post-Quantum keypair
        pk_hex, sk_hex = KyberService.generate_keypair()
        encrypted_sk = KeyProtectionService.encrypt_kyber_secret_key(sk_hex)

        user_data = {
            "full_name": payload.full_name,
            "email": payload.email,
            "password_hash": hash_password(payload.password),
            "is_active": True,
            "is_verified": False,
            "kyber_public_key": pk_hex,
            "kyber_secret_key_encrypted": encrypted_sk,
        }
        created_user = self.repo.create_user(user_data)

        self.audit_service.log_auth_event(
            event_type="USER_REGISTERED",
            status="SUCCESS",
            message=f"New user registered: {payload.email}",
            user_id=created_user.id,
            metadata={"email": payload.email, "full_name": payload.full_name}
        )

        return created_user

    def authenticate_user(self, payload: LoginRequest, response: Response):
        user = self.repo.get_user_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            self.audit_service.log_auth_event(
                event_type="USER_LOGIN_FAILED",
                status="FAILURE",
                message=f"Failed login attempt for email '{payload.email}' (invalid credentials)",
                metadata={"email": payload.email}
            )
            raise InvalidCredentials("Invalid email or password")
            
        if not user.is_active:
            self.audit_service.log_auth_event(
                event_type="USER_LOGIN_FAILED",
                status="FAILURE",
                message=f"Failed login attempt for email '{payload.email}' (account inactive)",
                user_id=user.id,
                metadata={"email": payload.email}
            )
            raise AuthenticationError("User account is inactive")
        
        # Using email as subject since repo only supports get_user_by_email
        access_token = create_access_token(subject=user.email)
        refresh_token = create_refresh_token(subject=user.email)

        token_payload = verify_token(refresh_token, "refresh")
        expires_at = datetime.datetime.fromtimestamp(token_payload["exp"], tz=datetime.timezone.utc)

        self.repo.create_refresh_token({
            "user_id": user.id,
            "token_hash": refresh_token,
            "expires_at": expires_at
        })

        set_auth_cookies(response, access_token, refresh_token)

        self.audit_service.log_auth_event(
            event_type="USER_LOGIN_SUCCESS",
            status="SUCCESS",
            message=f"User login successful for '{user.email}'",
            user_id=user.id,
            metadata={"email": user.email}
        )

        return user, access_token, refresh_token

    def logout_user(self, refresh_token: str, response: Response, user_id: str | None = None):
        if refresh_token:
            self.repo.revoke_refresh_token(refresh_token)
        clear_auth_cookies(response)
        self.audit_service.log_auth_event(
            event_type="USER_LOGOUT",
            status="SUCCESS",
            message="User logged out successfully",
            user_id=user_id
        )

    def refresh_session(self, refresh_token: str, response: Response):
        if not refresh_token:
            raise AuthenticationError("Refresh token missing")

        payload = verify_token(refresh_token, "refresh")
        db_token = self.repo.get_refresh_token(refresh_token)

        if not db_token or db_token.revoked:
            raise AuthenticationError("Refresh token is invalid or revoked")

        user = self.repo.get_user_by_email(payload["sub"])
        if not user or not user.is_active:
            raise AuthenticationError("User is inactive or not found")
        
        self.repo.revoke_refresh_token(refresh_token)
        
        new_access = create_access_token(subject=user.email)
        new_refresh = create_refresh_token(subject=user.email)
        
        new_token_payload = verify_token(new_refresh, "refresh")
        expires_at = datetime.datetime.fromtimestamp(new_token_payload["exp"], tz=datetime.timezone.utc)

        self.repo.create_refresh_token({
            "user_id": user.id,
            "token_hash": new_refresh,
            "expires_at": expires_at
        })
        
        set_auth_cookies(response, new_access, new_refresh)
        return user, new_access, new_refresh

    def get_current_user(self, access_token: str):
        payload = verify_token(access_token, "access")
        user = self.repo.get_user_by_email(payload["sub"])
        if not user:
            raise UserNotFound("User not found")
        return user
