import datetime
import uuid
from typing import Any

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# TODO: remove passlib dependency as it is deprecated: https://github.com/pyca/bcrypt/issues/684 [USe bcrypt directly]

ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: datetime.timedelta) -> str:
    expire = datetime.datetime.now(datetime.UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_token(subject: str, expires_delta: datetime.timedelta) -> str:
    now = datetime.datetime.now(datetime.UTC)
    exp = (now + expires_delta).timestamp()
    token = jwt.encode(
        {
            "exp": exp,
            "nbf": now.timestamp(),
            "sub": subject,
        },
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return token


def verify_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None


def generate_confirmation_token(user_id: str) -> str:
    expires_delta = datetime.timedelta(hours=settings.CONFIRMATION_TOKEN_EXPIRE_HOURS)
    return generate_token(user_id, expires_delta)


def generate_password_reset_token(email: str) -> str:
    expires_delta = datetime.timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    return generate_token(email, expires_delta)

