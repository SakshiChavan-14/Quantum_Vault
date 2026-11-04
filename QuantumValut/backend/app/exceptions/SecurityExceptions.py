"""
Security and Cryptographic Exceptions for QuantumVault.
"""

class SecurityException(Exception):
    """Base exception for cryptographic security errors."""
    pass


class MasterKeyConfigurationError(SecurityException):
    """Raised when CRYPTO_MASTER_KEY is missing, malformed, or invalid."""
    pass


class KeyProtectionError(SecurityException):
    """Raised when master key encryption/decryption of a secret key fails."""
    pass


class UserKyberKeyUnavailable(SecurityException):
    """Raised when a user's Kyber keys are missing or cannot be retrieved."""
    pass
