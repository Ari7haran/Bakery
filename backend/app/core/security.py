import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from jose import jwt, JWTError
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None, role: str = "customer") -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Constant dummy bcrypt hash for timing attack mitigation during non-existent user login
DUMMY_BCRYPT_HASH = "$2b$12$e80yE6wI74L8Y1jE6zU1e.yF9O1E2x3z4a5b6c7d8e9f0g1h2i3j4"

def dummy_verify_password(plain_password: str = "dummy_password") -> bool:
    """Executes a standard bcrypt verify to ensure constant-time response when user is not found."""
    return verify_password(plain_password, DUMMY_BCRYPT_HASH)

def decode_token(token: str) -> Optional[dict]:
    if not token or not isinstance(token, str):
        return None
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded
    except (JWTError, Exception):
        return None
