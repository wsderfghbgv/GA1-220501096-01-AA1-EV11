"""
Security module for device_systems.
Handles password hashing with passlib (bcrypt) and JWT token management with python-jose.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

# ─────────────────────────────────────────────────────────
# Passlib + bcrypt>=4.1 compatibility patch
# ─────────────────────────────────────────────────────────
# The passlib library is no longer maintained and is incompatible with
# bcrypt>=4.1 (removed __about__) and bcrypt>=5.0 (strict 72-byte limit).
# These patches are the standard community workaround.
import bcrypt as _bcrypt_module

# Patch 1: Restore __about__ attribute removed in bcrypt>=4.1
if not hasattr(_bcrypt_module, "__about__"):
    class _About:
        __version__ = _bcrypt_module.__version__
    _bcrypt_module.__about__ = _About()

# Patch 2: Auto-truncate passwords to 72 bytes for bcrypt>=5.0
_original_hashpw = _bcrypt_module.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, str):
        password = password.encode("utf-8")
    if isinstance(salt, str):
        salt = salt.encode("utf-8")
    return _original_hashpw(password[:72], salt)
_bcrypt_module.hashpw = _patched_hashpw

_original_checkpw = _bcrypt_module.checkpw
def _patched_checkpw(password, hashed_password):
    if isinstance(password, str):
        password = password.encode("utf-8")
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return _original_checkpw(password[:72], hashed_password)
_bcrypt_module.checkpw = _patched_checkpw

from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_in_production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing context using passlib with bcrypt scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using passlib with bcrypt.

    Args:
        password: The plain text password to hash.

    Returns:
        The bcrypt hash of the password as a string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password using passlib.

    Args:
        plain_password: The plain text password to verify.
        hashed_password: The bcrypt hash to verify against.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token.
        expires_delta: Optional custom expiration timedelta.

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token string to decode.

    Returns:
        Dictionary of decoded claims, or None if the token is invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
