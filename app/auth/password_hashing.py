"""Password hashing helpers using only the Python standard library."""

import hashlib
import hmac
import secrets

HASH_ALGORITHM = "pbkdf2_sha256"


def hash_password(password: str, iterations: int = 260000) -> str:
    """Hash a non-empty password using PBKDF2-HMAC-SHA256."""
    if not password:
        raise ValueError("Password cannot be empty.")
    salt_hex = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        iterations,
    ).hex()
    return f"{HASH_ALGORITHM}${iterations}${salt_hex}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    try:
        algorithm, iterations_text, salt_hex, hash_hex = stored_hash.split("$", 3)
        iterations = int(iterations_text)
        if algorithm != HASH_ALGORITHM or iterations <= 0:
            return False
        expected_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            iterations,
        ).hex()
    except (AttributeError, TypeError, ValueError):
        return False
    return hmac.compare_digest(expected_hash, hash_hex)
