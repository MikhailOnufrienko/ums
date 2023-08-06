from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from jose import jwt


def generate_tokens(email: str) -> str:
    subject_id = {'sub': email}
    to_encode = prepare_data_for_generating_tokens(
        subject_id, settings.TOKEN_LIFE_IN_DAYS
    )
    encoded_jwt = jwt.encode(
        to_encode, settings.TOKEN_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def prepare_data_for_generating_tokens(data: dict, expires_delta: int) -> dict:
    to_encode = data.copy()
    expire_in_days = datetime.utcnow() + timedelta(days=expires_delta)
    to_encode.update({'exp': expire_in_days})
    return to_encode


def add_invalid_token_to_cache(token: str) -> None:
    current_datetime = datetime.now()
    redis_key = f'invalid:{current_datetime}'
    expires: int = settings.TOKEN_LIFE_IN_DAYS * 86400  # in seconds
    cache.set(redis_key, token, expires)
