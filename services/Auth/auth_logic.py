from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.models.auth import User, RefreshToken
from .config import config
from .utils import get_password_hash, verify_password


from .crud import get_user_by_email, get_user_by_username
from argon2 import PasswordHasher

ph = PasswordHasher()

_REVOKED_TOKENS: set[str] = set()


def _token_fingerprint(token: str) -> str:
    """Возвращает устойчивый идентификатор JWT для списка отозванных токенов."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def revoke_token(token: str) -> None:
    """Отзывает JWT: добавляет его в локальный blacklist на время работы процесса."""
    try:
        jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM], options={"verify_exp": False})
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    _REVOKED_TOKENS.add(_token_fingerprint(token))


def is_token_revoked(token: str) -> bool:
    """Проверяет, был ли JWT отозван в текущем процессе."""
    return _token_fingerprint(token) in _REVOKED_TOKENS

# pwd_context = CryptContext(
#     schemes=["argon2"],
#     deprecated="auto",
#     argon2__time_cost=config.BCRYPT_ROUNDS,
#     argon2__memory_cost=102400,
#     argon2__parallelism=8
# )

# # ===== PASSWORD =====

# def verify_password(plain: str, hashed: str) -> bool:
#     return pwd_context.verify(plain, hashed)


# ===== JWT =====

def _create_token(user_id: uuid.UUID, email: str, token_type: str, expires_delta: timedelta) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expires_delta
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

def create_access_token(user_id: uuid.UUID, email: str) -> str:
    return _create_token(
        user_id,
        email,
        "access",
        timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(user_id: uuid.UUID, email: str) -> str:
    return _create_token(
        user_id,
        email,
        "refresh",
        timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    )

def verify_token(token: str, token_type: str) -> dict:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token revoked")
        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ===== AUTH =====

def authenticate_user(db: Session, username_or_email: str, password: str):
    """Аутентификация пользователя по username или email"""
    if "@" in username_or_email:
        user = get_user_by_email(db, username_or_email)
    else:
        user = get_user_by_username(db, username_or_email)
    
    if not user:
        return None

    try:
        ph.verify(user.password_hash, password)
    except:
        return None
    
    return user

# ===== REFRESH TOKENS =====

def save_refresh_token(
    db: Session,
    user_id: uuid.UUID,
    refresh_token: str,
    device_info: str | None,
    ip_address: str | None
):
    token_hash = get_password_hash(refresh_token)

    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()

    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
        )
    )
    db.commit()

def verify_refresh_token(
    db: Session,
    refresh_token: str,
    user_id: uuid.UUID,
    device_info: str | None
) -> bool:
    # Ищем токен по user_id и сроку действия, игнорируя device_info
    token = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()

    if not token:
        return False

    return verify_password(refresh_token, token.token_hash)


def create_verification_token(user_id: uuid.UUID, expires_minutes: int = 60) -> str:
    payload = {
        "sub": str(user_id),
        "type": "email_verification",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


def create_password_reset_token(user_id: uuid.UUID, email: str, expires_minutes: int = 30) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "password_reset",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


def verify_password_reset_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
        if is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token revoked")
        return uuid.UUID(payload.get("sub"))
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=400, detail="Token expired") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid token") from exc

def verify_verification_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("type") != "email_verification":
            raise HTTPException(status_code=400, detail="Invalid token type")
        return uuid.UUID(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token")