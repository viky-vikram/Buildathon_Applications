from __future__ import annotations

import hashlib
import hmac
import secrets


PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 120_000
MIN_PASSWORD_LENGTH = 6


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), PASSWORD_ITERATIONS)
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, iterations_raw, salt, expected = stored_hash.split("$", 3)
        iterations = int(iterations_raw)
    except (AttributeError, ValueError):
        return False
    if scheme != PASSWORD_SCHEME:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), iterations).hex()
    return hmac.compare_digest(digest, expected)


def validate_password(password: str) -> str:
    cleaned = password.strip()
    if len(cleaned) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    return cleaned
