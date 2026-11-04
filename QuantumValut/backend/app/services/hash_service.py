"""
Hash Service for SHA-256 File Integrity Verification
Handles calculation and verification of file hashes for integrity checking
"""

import hashlib
from typing import Tuple


class HashService:
    """
    Service for file hashing and integrity verification.
    
    Current implementation uses SHA-256 which provides:
    - 256-bit (32-byte) hash values
    - Collision resistance
    - Integrity verification on download
    - Deduplication detection
    """

    ALGORITHM = "SHA256"
    HASH_LENGTH = 64  # 256 bits = 64 hex characters
    CHUNK_SIZE = 65536  # 64 KB chunks for memory efficiency

    @staticmethod
    def calculate_file_hash(file_content: bytes) -> str:
        """
        Calculate SHA-256 hash of file content.
        
        Args:
            file_content: Raw file bytes
            
        Returns:
            Hex-encoded SHA-256 hash (64 characters)
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_content)
        return sha256_hash.hexdigest()

    @staticmethod
    def calculate_file_hash_streaming(file_path: str) -> str:
        """
        Calculate SHA-256 hash of file using streaming (memory efficient).
        
        For large files, this reads in chunks to avoid loading entire file in memory.
        
        Args:
            file_path: Path to file to hash
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(HashService.CHUNK_SIZE)
                if not chunk:
                    break
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    @staticmethod
    def verify_file_hash(file_content: bytes, expected_hash: str) -> bool:
        """
        Verify that file content matches expected hash.
        
        Args:
            file_content: Raw file bytes to verify
            expected_hash: Hex-encoded hash to compare against
            
        Returns:
            True if hashes match, False otherwise
        """
        calculated_hash = HashService.calculate_file_hash(file_content)
        return calculated_hash.lower() == expected_hash.lower()

    @staticmethod
    def verify_file_hash_streaming(file_path: str, expected_hash: str) -> bool:
        """
        Verify file hash using streaming (memory efficient).
        
        Args:
            file_path: Path to file to verify
            expected_hash: Hex-encoded hash to compare against
            
        Returns:
            True if hashes match, False otherwise
        """
        calculated_hash = HashService.calculate_file_hash_streaming(file_path)
        return calculated_hash.lower() == expected_hash.lower()

    @staticmethod
    def hash_content(content: bytes) -> str:
        """
        Hash arbitrary content (not just files).
        
        Args:
            content: Bytes to hash
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def validate_hash_format(hash_value: str) -> bool:
        """
        Validate that a string is a valid SHA-256 hash.
        
        Args:
            hash_value: String to validate
            
        Returns:
            True if valid SHA-256 hash format, False otherwise
        """
        # SHA-256 hash should be exactly 64 hex characters
        if not hash_value:
            return False

        if len(hash_value) != HashService.HASH_LENGTH:
            return False

        # Check if all characters are valid hex
        try:
            int(hash_value, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_hash_info() -> dict:
        """
        Get information about current hash implementation.
        
        Returns:
            Dictionary with hash details
        """
        return {
            "algorithm": HashService.ALGORITHM,
            "hash_length_bits": 256,
            "hash_length_hex_chars": HashService.HASH_LENGTH,
            "hash_length_bytes": 32,
            "chunk_size_bytes": HashService.CHUNK_SIZE,
            "use_cases": {
                "file_integrity": "Verify files haven't been modified",
                "deduplication": "Detect duplicate files",
                "tampering_detection": "Detect unauthorized changes",
            },
            "properties": {
                "collision_resistance": "Computationally infeasible to find collisions",
                "preimage_resistance": "Cannot find input from hash",
                "avalanche_effect": "Small input change = large hash change",
            },
        }

    @staticmethod
    def compare_hashes(hash1: str, hash2: str) -> bool:
        """
        Safely compare two hash values (case-insensitive).
        
        Args:
            hash1: First hash
            hash2: Second hash
            
        Returns:
            True if hashes are equal
        """
        return hash1.lower() == hash2.lower()

    @staticmethod
    def get_hash_summary(file_hash: str, display_length: int = 8) -> str:
        """
        Get a short summary of a hash for display.
        
        Args:
            file_hash: Full SHA-256 hash
            display_length: Number of characters to show
            
        Returns:
            Short hash summary (e.g., "a1b2c3d4...")
        """
        if not file_hash or len(file_hash) < display_length:
            return file_hash

        return f"{file_hash[:display_length//2]}...{file_hash[-display_length//2:]}"
