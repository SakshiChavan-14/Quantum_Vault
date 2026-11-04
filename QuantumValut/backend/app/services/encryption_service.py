"""
Encryption Service for AES-256 File Encryption
Handles secure file encryption and decryption using Fernet (AES-128 with authentication)
For Phase 4: Can be upgraded to full AES-256 and Kyber key encryption
"""

import os
from typing import Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets

from app.exceptions.FileExceptions import EncryptionFailed, DecryptionFailed


class EncryptionService:
    """
    Service for file encryption and decryption.
    
    Current implementation uses Fernet (symmetric encryption with authentication)
    which is built on AES-128. This provides:
    - AES-128-CBC encryption
    - HMAC authentication
    - Timestamp verification
    
    Phase 4 roadmap:
    - Upgrade to full AES-256
    - Add Kyber key encryption for AES keys
    - Multi-layer key protection
    """

    # Fernet uses AES-128 (128-bit keys)
    # Keys must be 32 bytes (base64 encoded, becomes ~44 bytes)
    ALGORITHM = "AES-128-Fernet"  # Will upgrade to AES-256 in Phase 4
    ENCODING = "utf-8"

    # PBKDF2 settings for key derivation
    KEY_DERIVATION_ALGORITHM = "PBKDF2"
    HASH_ALGORITHM = "SHA256"
    KEY_ITERATIONS = 100000  # NIST recommendation
    SALT_LENGTH = 32  # 256 bits

    def __init__(self):
        """Initialize encryption service."""
        self.algorithm = self.ALGORITHM
        self.key_derivation = self.KEY_DERIVATION_ALGORITHM

    @staticmethod
    def generate_encryption_key() -> str:
        """
        Generate a random encryption key for a file.
        
        Returns:
            Base64-encoded Fernet key (44 bytes)
        """
        try:
            # Fernet.generate_key() returns a URL-safe base64-encoded key
            key = Fernet.generate_key()
            return key.decode(EncryptionService.ENCODING)
        except Exception as e:
            raise EncryptionFailed(f"Failed to generate encryption key: {str(e)}")

    @staticmethod
    def generate_salt() -> str:
        """
        Generate a random salt for key derivation.
        
        Returns:
            Hex-encoded salt (64 characters for 32 bytes)
        """
        try:
            salt = secrets.token_bytes(EncryptionService.SALT_LENGTH)
            return salt.hex()
        except Exception as e:
            raise EncryptionFailed(f"Failed to generate salt: {str(e)}")

    @staticmethod
    def derive_key_from_password(password: str, salt: str) -> str:
        """
        Derive an encryption key from a password using PBKDF2.
        
        This is used for user-provided passwords in future implementations.
        
        Args:
            password: User password
            salt: Hex-encoded salt
            
        Returns:
            Base64-encoded Fernet key
        """
        try:
            # Convert salt from hex back to bytes
            salt_bytes = bytes.fromhex(salt)

            # Use PBKDF2HMAC with SHA256
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits for Fernet key
                salt=salt_bytes,
                iterations=EncryptionService.KEY_ITERATIONS,
            )

            # Derive key from password
            derived_key = kdf.derive(password.encode(EncryptionService.ENCODING))

            # Encode to base64 for Fernet
            fernet_key = base64.urlsafe_b64encode(derived_key)
            return fernet_key.decode(EncryptionService.ENCODING)
        except Exception as e:
            raise EncryptionFailed(f"Failed to derive key from password: {str(e)}")

    @staticmethod
    def encrypt_file(
        file_content: bytes,
        encryption_key: str = None
    ) -> Tuple[bytes, str, str]:
        """
        Encrypt file content using Fernet (AES-128 with authentication).
        
        If no key is provided, a random one is generated.
        
        Args:
            file_content: Raw file bytes to encrypt
            encryption_key: Base64-encoded Fernet key (optional)
            
        Returns:
            Tuple of (encrypted_content, encryption_key, algorithm)
            
        Raises:
            EncryptionFailed: If encryption fails
        """
        try:
            # Generate key if not provided
            if not encryption_key:
                encryption_key = EncryptionService.generate_encryption_key()

            # Create Fernet cipher with the key
            cipher = Fernet(encryption_key.encode(EncryptionService.ENCODING))

            # Encrypt the file content
            encrypted_content = cipher.encrypt(file_content)

            return encrypted_content, encryption_key, EncryptionService.ALGORITHM
        except Exception as e:
            raise EncryptionFailed(f"File encryption failed: {str(e)}")

    @staticmethod
    def decrypt_file(encrypted_content: bytes, encryption_key: str) -> bytes:
        """
        Decrypt file content using Fernet.
        
        Args:
            encrypted_content: Encrypted file bytes
            encryption_key: Base64-encoded Fernet key
            
        Returns:
            Decrypted file content
            
        Raises:
            DecryptionFailed: If decryption fails
        """
        try:
            # Create Fernet cipher with the key
            cipher = Fernet(encryption_key.encode(EncryptionService.ENCODING))

            # Decrypt the file content
            decrypted_content = cipher.decrypt(encrypted_content)

            return decrypted_content
        except Exception as e:
            raise DecryptionFailed(f"File decryption failed: {str(e)}")

    @staticmethod
    def encrypt_key_with_password(
        encryption_key: str,
        password: str,
        salt: str = None
    ) -> Tuple[str, str]:
        """
        Encrypt the AES key with a password-derived key.
        
        This provides double encryption:
        1. File encrypted with random AES key
        2. AES key encrypted with password-derived key
        
        Phase 4: This will use Kyber for post-quantum safety.
        
        Args:
            encryption_key: Base64-encoded file encryption key
            password: User password
            salt: Hex-encoded salt (generated if not provided)
            
        Returns:
            Tuple of (encrypted_key_hex, salt)
        """
        try:
            # Generate salt if not provided
            if not salt:
                salt = EncryptionService.generate_salt()

            # Derive key from password
            password_key = EncryptionService.derive_key_from_password(password, salt)

            # Create cipher with password-derived key
            cipher = Fernet(password_key.encode(EncryptionService.ENCODING))

            # Encrypt the encryption key
            encrypted_key = cipher.encrypt(encryption_key.encode(EncryptionService.ENCODING))

            # Convert to hex for storage
            encrypted_key_hex = encrypted_key.hex()

            return encrypted_key_hex, salt
        except Exception as e:
            raise EncryptionFailed(f"Key encryption failed: {str(e)}")

    @staticmethod
    def decrypt_key_with_password(
        encrypted_key_hex: str,
        password: str,
        salt: str
    ) -> str:
        """
        Decrypt the AES key using password-derived key.
        
        Args:
            encrypted_key_hex: Hex-encoded encrypted key
            password: User password
            salt: Hex-encoded salt
            
        Returns:
            Base64-encoded decrypted encryption key
        """
        try:
            # Derive key from password
            password_key = EncryptionService.derive_key_from_password(password, salt)

            # Create cipher with password-derived key
            cipher = Fernet(password_key.encode(EncryptionService.ENCODING))

            # Convert hex back to bytes
            encrypted_key_bytes = bytes.fromhex(encrypted_key_hex)

            # Decrypt the encryption key
            decrypted_key = cipher.decrypt(encrypted_key_bytes)

            return decrypted_key.decode(EncryptionService.ENCODING)
        except Exception as e:
            raise DecryptionFailed(f"Key decryption failed: {str(e)}")

    @staticmethod
    def verify_encryption_status(
        is_encrypted: bool,
        encryption_algorithm: str = None
    ) -> bool:
        """
        Verify that encryption metadata is valid.
        
        Args:
            is_encrypted: Whether file should be encrypted
            encryption_algorithm: Algorithm used (if encrypted)
            
        Returns:
            True if valid, False otherwise
        """
        if not is_encrypted:
            return True  # No encryption needed

        # If encrypted, algorithm must be specified
        if not encryption_algorithm:
            return False

        # Check if algorithm is supported
        supported_algorithms = [
            "AES-128-Fernet",
            "AES-256",  # For Phase 4
            "AES-256-Kyber",  # For Phase 4
        ]

        return encryption_algorithm in supported_algorithms

    @staticmethod
    def get_encryption_info() -> dict:
        """
        Get information about current encryption implementation.
        
        Returns:
            Dictionary with encryption details
        """
        return {
            "algorithm": EncryptionService.ALGORITHM,
            "current_phase": 3,
            "key_derivation": EncryptionService.KEY_DERIVATION_ALGORITHM,
            "hash_algorithm": EncryptionService.HASH_ALGORITHM,
            "iterations": EncryptionService.KEY_ITERATIONS,
            "salt_length_bytes": EncryptionService.SALT_LENGTH,
            "features": {
                "symmetric_encryption": True,
                "authenticated_encryption": True,
                "password_based_encryption": True,
                "post_quantum_ready": False,  # Will be True in Phase 4
            },
            "roadmap": {
                "phase_3": "AES-128-Fernet with PBKDF2 key derivation",
                "phase_4": "Full AES-256 with Kyber post-quantum encryption",
            },
        }
