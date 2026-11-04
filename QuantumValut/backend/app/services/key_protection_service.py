"""
Key Protection Service for QuantumVault.
Handles application-level server-side envelope protection for User Kyber-1024 Secret Keys
using the configured CRYPTO_MASTER_KEY.
"""

from typing import Tuple, Optional, Any
from cryptography.fernet import Fernet, InvalidToken
import base64

from app.core.config import settings
from app.exceptions.SecurityExceptions import (
    MasterKeyConfigurationError,
    KeyProtectionError,
    UserKyberKeyUnavailable
)
from app.services.kyber_service import KyberService


class KeyProtectionService:
    """
    Service for protecting and managing user post-quantum secret keys.
    
    Security Architecture:
    - User Kyber Public Key: Persisted in plaintext in the database.
    - User Kyber Secret Key: NEVER persisted in plaintext; encrypted with CRYPTO_MASTER_KEY.
    - CRYPTO_MASTER_KEY: Kept strictly in server environment, never stored in DB or logged.
    - Plaintext Kyber Secret Key: Held only ephemerally in memory during cryptographic operations.
    """

    @staticmethod
    def _get_fernet_cipher(master_key: Optional[str] = None) -> Fernet:
        """
        Instantiate Fernet cipher using the provided or configured master key.
        
        Args:
            master_key: Optional override master key (e.g. for testing)
            
        Returns:
            Fernet cipher instance
            
        Raises:
            MasterKeyConfigurationError: If master key is missing or invalid
        """
        raw_key = master_key if master_key is not None else settings.CRYPTO_MASTER_KEY
        
        if not raw_key or not isinstance(raw_key, str) or len(raw_key.strip()) == 0:
            raise MasterKeyConfigurationError("CRYPTO_MASTER_KEY is missing or empty")

        key_str = raw_key.strip()

        # Check if key is already a valid 32-byte URL-safe base64 string
        try:
            key_bytes = key_str.encode("utf-8")
            decoded = base64.urlsafe_b64decode(key_bytes)
            if len(decoded) == 32:
                return Fernet(key_bytes)
        except Exception:
            pass

        # If key is 64 hex characters (32 bytes), convert to URL-safe base64
        try:
            hex_bytes = bytes.fromhex(key_str)
            if len(hex_bytes) == 32:
                b64_key = base64.urlsafe_b64encode(hex_bytes)
                return Fernet(b64_key)
        except Exception:
            pass

        raise MasterKeyConfigurationError(
            "CRYPTO_MASTER_KEY must be a valid 32-byte base64 or 64-character hex key"
        )

    @classmethod
    def encrypt_kyber_secret_key(
        cls,
        secret_key_hex: str,
        master_key: Optional[str] = None
    ) -> str:
        """
        Encrypt a user's Kyber secret key using CRYPTO_MASTER_KEY.
        
        Args:
            secret_key_hex: Hex-encoded Kyber secret key (3168 bytes / 6336 hex chars)
            master_key: Optional override master key
            
        Returns:
            Encrypted token string for safe persistence in database
            
        Raises:
            KeyProtectionError: If encryption fails
        """
        if not secret_key_hex or not isinstance(secret_key_hex, str):
            raise KeyProtectionError("Secret key must be a non-empty hex string")

        try:
            cipher = cls._get_fernet_cipher(master_key)
            encrypted_bytes = cipher.encrypt(secret_key_hex.encode("utf-8"))
            return encrypted_bytes.decode("utf-8")
        except MasterKeyConfigurationError:
            raise
        except Exception as e:
            raise KeyProtectionError(f"Failed to encrypt Kyber secret key: {str(e)}")

    @classmethod
    def decrypt_kyber_secret_key(
        cls,
        encrypted_secret_key: str,
        master_key: Optional[str] = None
    ) -> str:
        """
        Decrypt a user's Kyber secret key using CRYPTO_MASTER_KEY.
        
        Args:
            encrypted_secret_key: Encrypted token string from database
            master_key: Optional override master key
            
        Returns:
            Decrypted hex-encoded Kyber secret key
            
        Raises:
            KeyProtectionError: If decryption or authentication fails
        """
        if not encrypted_secret_key or not isinstance(encrypted_secret_key, str):
            raise KeyProtectionError("Encrypted secret key must be a non-empty string")

        try:
            cipher = cls._get_fernet_cipher(master_key)
            decrypted_bytes = cipher.decrypt(encrypted_secret_key.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            raise KeyProtectionError("Failed to decrypt Kyber secret key: invalid master key or corrupted ciphertext")
        except MasterKeyConfigurationError:
            raise
        except Exception as e:
            raise KeyProtectionError(f"Failed to decrypt Kyber secret key: {str(e)}")

    @classmethod
    def provision_user_kyber_keys(
        cls,
        user: Any,
        db_session: Optional[Any] = None,
        master_key: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate and provision a new Kyber-1024 keypair for a user.
        
        Args:
            user: User ORM instance
            db_session: Optional SQLAlchemy session to commit changes
            master_key: Optional override master key
            
        Returns:
            Tuple of (public_key_hex, plaintext_secret_key_hex)
        """
        pk_hex, sk_hex = KyberService.generate_keypair()
        encrypted_sk = cls.encrypt_kyber_secret_key(sk_hex, master_key=master_key)

        user.kyber_public_key = pk_hex
        user.kyber_secret_key_encrypted = encrypted_sk

        if db_session is not None:
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)

        return pk_hex, sk_hex

    @classmethod
    def get_or_provision_user_kyber_keys(
        cls,
        user: Any,
        db_session: Optional[Any] = None,
        master_key: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Retrieve existing Kyber keys for a user, or lazily provision them if absent.
        
        Args:
            user: User ORM instance
            db_session: Optional SQLAlchemy session to commit changes if provisioning
            master_key: Optional override master key
            
        Returns:
            Tuple of (public_key_hex, plaintext_secret_key_hex)
        """
        if user.kyber_public_key and user.kyber_secret_key_encrypted:
            sk_hex = cls.decrypt_kyber_secret_key(
                user.kyber_secret_key_encrypted, master_key=master_key
            )
            return user.kyber_public_key, sk_hex

        # Controlled Lazy Provisioning for existing users
        return cls.provision_user_kyber_keys(user, db_session=db_session, master_key=master_key)

    @classmethod
    def get_user_kyber_secret_key(
        cls,
        user: Any,
        master_key: Optional[str] = None
    ) -> str:
        """
        Retrieve and decrypt a user's Kyber secret key for internal cryptographic operations.
        
        Args:
            user: User ORM instance
            master_key: Optional override master key
            
        Returns:
            Decrypted Kyber secret key hex string
            
        Raises:
            UserKyberKeyUnavailable: If user does not have an encrypted secret key
            KeyProtectionError: If decryption fails
        """
        if not getattr(user, "kyber_secret_key_encrypted", None):
            raise UserKyberKeyUnavailable("User does not have an encrypted Kyber secret key provisioned")

        return cls.decrypt_kyber_secret_key(
            user.kyber_secret_key_encrypted, master_key=master_key
        )
