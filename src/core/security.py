from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from src.config.settings import get_settings

_hasher = PasswordHasher()


class SecurityService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return _hasher.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        return _hasher.hash(password)

    @staticmethod
    def create_access_token(
        subject: Any,
        expires_delta: timedelta | None = None,
    ) -> str:
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "access",
        }

        return jwt.encode(
            to_encode,
            get_settings().SECRET_KEY,
            algorithm=get_settings().ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token=token,
                key=get_settings().SECRET_KEY,
                algorithms=[get_settings().ALGORITHM],
            )
            return payload
        except JWTError:
            return None


security_service = SecurityService()
