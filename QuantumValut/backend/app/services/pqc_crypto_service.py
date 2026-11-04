"""
QuantumVault Post-Quantum Cryptographic Service (Version 2)
Implements Hybrid AES-256-GCM + CRYSTALS-Kyber1024 KEM + HKDF-SHA256 Key Wrapping
"""

from typing import Dict, Any, Optional, Union
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap, InvalidUnwrap
from cryptography.exceptions import InvalidTag

from app.exceptions.FileExceptions import EncryptionFailed, DecryptionFailed
from app.services.kyber_service import KyberService
from app.services.hash_service import HashService


# Versioning & Algorithm Identifiers
LEGACY_CRYPTO_VERSION = 1
LEGACY_ENCRYPTION_ALGORITHM = "AES-128-Fernet"

PQC_CRYPTO_VERSION = 2
PQC_ENCRYPTION_ALGORITHM = "AES-256-GCM+Kyber1024"

# Cryptographic Parameter Constants
AES_KEY_SIZE_BYTES = 32     # 256 bits
GCM_NONCE_SIZE_BYTES = 12   # 96 bits
KEK_SIZE_BYTES = 32         # 256 bits
HKDF_INFO_V2 = b"quantumvault-file-kek-v2"


# =============================================================================
# Core Primitives
# =============================================================================

def generate_dek() -> bytes:
    """
    Generate a cryptographically random 256-bit (32-byte) AES Data Encryption Key.
    
    Returns:
        32 random bytes
    """
    return AESGCM.generate_key(bit_length=256)


def generate_nonce() -> bytes:
    """
    Generate a cryptographically secure random 96-bit (12-byte) AES-GCM nonce.
    
    Returns:
        12 random bytes
    """
    return secrets.token_bytes(GCM_NONCE_SIZE_BYTES)


def encrypt_aes_gcm(
    plaintext: bytes,
    dek: bytes,
    nonce: Optional[bytes] = None,
    associated_data: Optional[bytes] = None
) -> Dict[str, bytes]:
    """
    Encrypt plaintext bytes using authenticated AES-256-GCM.
    
    Args:
        plaintext: Raw data bytes to encrypt
        dek: 32-byte AES-256 key
        nonce: Optional 12-byte nonce (generated if None)
        associated_data: Optional additional authenticated data (AAD)
        
    Returns:
        Dict with "ciphertext" (ciphertext + 16-byte tag) and "nonce" (12 bytes)
        
    Raises:
        EncryptionFailed: If inputs are invalid or encryption fails
    """
    if not isinstance(plaintext, (bytes, bytearray)):
        raise EncryptionFailed("Plaintext must be bytes")
    if not isinstance(dek, (bytes, bytearray)) or len(dek) != AES_KEY_SIZE_BYTES:
        raise EncryptionFailed(f"DEK must be exactly {AES_KEY_SIZE_BYTES} bytes")
    
    if nonce is None:
        nonce = generate_nonce()
    elif not isinstance(nonce, (bytes, bytearray)) or len(nonce) != GCM_NONCE_SIZE_BYTES:
        raise EncryptionFailed(f"Nonce must be exactly {GCM_NONCE_SIZE_BYTES} bytes")

    try:
        aesgcm = AESGCM(dek)
        ciphertext = aesgcm.encrypt(nonce, bytes(plaintext), associated_data)
        return {
            "ciphertext": ciphertext,
            "nonce": nonce
        }
    except Exception as e:
        raise EncryptionFailed(f"AES-256-GCM encryption failed: {str(e)}")


def decrypt_aes_gcm(
    ciphertext: bytes,
    dek: bytes,
    nonce: bytes,
    associated_data: Optional[bytes] = None
) -> bytes:
    """
    Decrypt and authenticate AES-256-GCM ciphertext.
    
    Args:
        ciphertext: Ciphertext with appended 16-byte authentication tag
        dek: 32-byte AES-256 key
        nonce: 12-byte nonce
        associated_data: Optional additional authenticated data (AAD)
        
    Returns:
        Decrypted original plaintext bytes
        
    Raises:
        DecryptionFailed: If authentication fails (tampering/wrong key) or inputs invalid
    """
    if not isinstance(ciphertext, (bytes, bytearray)):
        raise DecryptionFailed("Ciphertext must be bytes")
    if not isinstance(dek, (bytes, bytearray)) or len(dek) != AES_KEY_SIZE_BYTES:
        raise DecryptionFailed(f"DEK must be exactly {AES_KEY_SIZE_BYTES} bytes")
    if not isinstance(nonce, (bytes, bytearray)) or len(nonce) != GCM_NONCE_SIZE_BYTES:
        raise DecryptionFailed(f"Nonce must be exactly {GCM_NONCE_SIZE_BYTES} bytes")

    try:
        aesgcm = AESGCM(dek)
        plaintext = aesgcm.decrypt(nonce, bytes(ciphertext), associated_data)
        return plaintext
    except InvalidTag:
        raise DecryptionFailed("AES-256-GCM authentication failed: data tampered or invalid key/nonce")
    except Exception as e:
        raise DecryptionFailed(f"AES-256-GCM decryption failed: {str(e)}")


def derive_kek(
    shared_secret: bytes,
    salt: Optional[bytes] = None,
    info: bytes = HKDF_INFO_V2
) -> bytes:
    """
    Derive a 256-bit Key Encryption Key (KEK) from a Kyber shared secret using HKDF-SHA256.
    
    Args:
        shared_secret: 32-byte KEM shared secret
        salt: Optional salt bytes (None for default zero-filled salt per RFC 5869)
        info: Context application info string
        
    Returns:
        32-byte derived KEK
        
    Raises:
        EncryptionFailed: If key derivation fails
    """
    if not isinstance(shared_secret, (bytes, bytearray)) or len(shared_secret) < 32:
        raise EncryptionFailed("Shared secret must be at least 32 bytes")

    try:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=KEK_SIZE_BYTES,
            salt=salt,
            info=info,
        )
        return hkdf.derive(bytes(shared_secret))
    except Exception as e:
        raise EncryptionFailed(f"HKDF-SHA256 key derivation failed: {str(e)}")


def wrap_dek(kek: bytes, dek: bytes) -> bytes:
    """
    Wrap a 32-byte AES DEK using a 32-byte KEK via RFC 3394 AES Key Wrap.
    
    Args:
        kek: 32-byte Key Encryption Key
        dek: 32-byte Data Encryption Key
        
    Returns:
        40-byte wrapped DEK
        
    Raises:
        EncryptionFailed: If key wrapping fails
    """
    if not isinstance(kek, (bytes, bytearray)) or len(kek) != KEK_SIZE_BYTES:
        raise EncryptionFailed(f"KEK must be exactly {KEK_SIZE_BYTES} bytes")
    if not isinstance(dek, (bytes, bytearray)) or len(dek) != AES_KEY_SIZE_BYTES:
        raise EncryptionFailed(f"DEK must be exactly {AES_KEY_SIZE_BYTES} bytes")

    try:
        return aes_key_wrap(bytes(kek), bytes(dek))
    except Exception as e:
        raise EncryptionFailed(f"AES key wrapping failed: {str(e)}")


def unwrap_dek(kek: bytes, wrapped_dek: bytes) -> bytes:
    """
    Unwrap an AES DEK using KEK via RFC 3394 AES Key Unwrap.
    
    Args:
        kek: 32-byte Key Encryption Key
        wrapped_dek: 40-byte wrapped DEK
        
    Returns:
        Original 32-byte DEK
        
    Raises:
        DecryptionFailed: If unwrap fails or integrity check fails
    """
    if not isinstance(kek, (bytes, bytearray)) or len(kek) != KEK_SIZE_BYTES:
        raise DecryptionFailed(f"KEK must be exactly {KEK_SIZE_BYTES} bytes")
    if not isinstance(wrapped_dek, (bytes, bytearray)):
        raise DecryptionFailed("Wrapped DEK must be bytes")

    try:
        return aes_key_unwrap(bytes(kek), bytes(wrapped_dek))
    except InvalidUnwrap:
        raise DecryptionFailed("AES Key Unwrap failed: invalid KEK or corrupted wrapped key data")
    except Exception as e:
        raise DecryptionFailed(f"AES Key Unwrap error: {str(e)}")


# =============================================================================
# Unified Post-Quantum Cryptographic Service
# =============================================================================

class PQCCryptoService:
    """
    Unified Cryptographic Service for QuantumVault Version 2 (PQC).
    
    Combines:
    - AES-256-GCM symmetric payload encryption
    - CRYSTALS-Kyber1024 post-quantum key encapsulation
    - HKDF-SHA256 key derivation
    - RFC 3394 AES key wrapping
    - SHA-256 plaintext integrity hashing
    """

    VERSION = PQC_CRYPTO_VERSION
    ALGORITHM = PQC_ENCRYPTION_ALGORITHM

    @staticmethod
    def encrypt_file_pqc(
        file_content: bytes,
        recipient_kyber_public_key: str
    ) -> Dict[str, Any]:
        """
        Execute full Version 2 Post-Quantum Encryption Pipeline.
        
        Steps:
        1. Calculate SHA-256 integrity hash over plaintext
        2. Generate fresh 256-bit AES DEK and 96-bit GCM Nonce
        3. Encrypt file payload with AES-256-GCM
        4. Encapsulate with recipient's Kyber-1024 public key -> (ct, shared_secret)
        5. Derive 256-bit KEK from shared secret via HKDF-SHA256
        6. Wrap DEK with KEK via AES Key Wrap
        
        Args:
            file_content: Raw plaintext file bytes
            recipient_kyber_public_key: Recipient's Kyber-1024 public key (hex string)
            
        Returns:
            Dict containing:
            - encrypted_file_bytes: bytes (AES-256-GCM ciphertext + tag)
            - nonce: bytes (12 bytes)
            - kyber_ciphertext: str (hex string)
            - wrapped_dek: str (hex string)
            - file_hash: str (SHA-256 hex string)
            - algorithm: str ("AES-256-GCM+Kyber1024")
            - version: int (2)
        """
        # 1. Plaintext SHA-256 integrity hash
        file_hash = HashService.calculate_file_hash(file_content)

        # 2. Key & nonce generation
        dek = generate_dek()
        nonce = generate_nonce()

        # 3. Payload encryption
        gcm_res = encrypt_aes_gcm(file_content, dek, nonce)

        # 4. Post-quantum encapsulation
        kyber_ct_hex, shared_secret = KyberService.encapsulate(recipient_kyber_public_key)

        # 5. KEK derivation
        kek = derive_kek(shared_secret)

        # 6. DEK wrapping
        wrapped_dek_bytes = wrap_dek(kek, dek)

        return {
            "encrypted_file_bytes": gcm_res["ciphertext"],
            "nonce": gcm_res["nonce"],
            "kyber_ciphertext": kyber_ct_hex,
            "wrapped_dek": wrapped_dek_bytes.hex(),
            "file_hash": file_hash,
            "algorithm": PQC_ENCRYPTION_ALGORITHM,
            "version": PQC_CRYPTO_VERSION,
        }

    @staticmethod
    def decrypt_file_pqc(
        encrypted_file_bytes: bytes,
        nonce: bytes,
        kyber_ciphertext: str,
        wrapped_dek: str,
        recipient_kyber_secret_key: str
    ) -> bytes:
        """
        Execute full Version 2 Post-Quantum Decryption Pipeline.
        
        Steps:
        1. Decapsulate Kyber ciphertext using recipient's Kyber secret key -> shared_secret
        2. Derive KEK from shared secret via HKDF-SHA256
        3. Unwrap DEK using KEK via AES Key Unwrap
        4. Decrypt file payload with AES-256-GCM using recovered DEK and nonce
        
        Args:
            encrypted_file_bytes: AES-256-GCM ciphertext + tag
            nonce: 12-byte nonce
            kyber_ciphertext: Hex-encoded Kyber ciphertext
            wrapped_dek: Hex-encoded wrapped DEK
            recipient_kyber_secret_key: Recipient's Kyber secret key (hex string)
            
        Returns:
            Decrypted plaintext file bytes
            
        Raises:
            DecryptionFailed: If any cryptographic verification or decryption step fails
        """
        try:
            wrapped_dek_bytes = bytes.fromhex(wrapped_dek)
        except ValueError:
            raise DecryptionFailed("Invalid hex encoding for wrapped DEK")

        # 1. Decapsulate shared secret
        shared_secret = KyberService.decapsulate(kyber_ciphertext, recipient_kyber_secret_key)

        # 2. Derive KEK
        kek = derive_kek(shared_secret)

        # 3. Unwrap DEK
        dek = unwrap_dek(kek, wrapped_dek_bytes)

        # 4. Decrypt payload
        plaintext = decrypt_aes_gcm(encrypted_file_bytes, dek, nonce)

        return plaintext
