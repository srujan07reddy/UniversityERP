import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import bcrypt
import jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationException

# Production Argon2id configuration (OWASP recommended parameters)
_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MiB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using Argon2id.
    Never stores plaintext passwords in the database.
    """
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plaintext password against stored hash.
    Supports Argon2id natively and falls back to bcrypt for legacy compatibility.
    """
    if not plain_password or not hashed_password:
        return False

    if hashed_password.startswith("$argon2"):
        try:
            return _hasher.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False
        except Exception:
            return False

    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    return False


def generate_secure_token(nbytes: int = 32) -> str:
    """
    Generates a cryptographically strong URL-safe token.
    Used for account activation, password reset, and recovery.
    """
    return secrets.token_urlsafe(nbytes)


def hash_token(token: str) -> str:
    """
    Hashes a sensitive token using SHA-256 for secure database storage.
    Ensures that stolen database dumps cannot be used to activate or reset accounts.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ==============================================================================
# JWT Authentication Tokens
# ==============================================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Creates a signed JWT Access Token with expiration, claims, and unique JTI.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    jti = to_encode.pop("jti", str(uuid.uuid4()))
    to_encode.update({
        "iat": now,
        "exp": expire,
        "jti": jti,
        "type": "access",
    })
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Creates a signed JWT Refresh Token with extended expiration and unique JTI.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    jti = to_encode.pop("jti", str(uuid.uuid4()))
    to_encode.update({
        "iat": now,
        "exp": expire,
        "jti": jti,
        "type": "refresh",
    })
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT signature and expiration.
    Raises AuthenticationException on expiration or invalid format.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "jti", "sub"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Authentication token has expired.")
    except jwt.InvalidTokenError as e:
        raise AuthenticationException(f"Invalid authentication token: {str(e)}")
