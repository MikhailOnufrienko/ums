from datetime import datetime, timedelta

import redis
from django.conf import settings
from django.core.cache import cache
from jose import ExpiredSignatureError, JWTError, jwt


redis_location = settings.CACHES['default']['LOCATION']
host, port = redis_location.split('://')[1].split(':')
redis_client = redis.StrictRedis(host=host, port=int(port), db=0)


def generate_tokens(user_id: int, email: str) -> str:
    claims = {'sub': email, 'user_id': user_id}
    to_encode = prepare_data_for_generating_tokens(
        claims, settings.TOKEN_LIFE_IN_DAYS
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


def check_token_not_used_for_logout(token: str) -> bool:
    cursor, keys = redis_client.scan(b'0', match='invalid*')
    for key in keys:
        value = cache.get(key)
        if value == token.encode():
            return False
    return True


def get_id_by_token(token: str) -> int:
    claims = jwt.get_unverified_claims(token)
    return claims['user_id']


def get_email_by_token(token: str) -> str:
    claims = jwt.get_unverified_claims(token)
    return claims['sub']

def check_profile_view_permission(token: str, email: str) -> bool:
    viewer_email = get_email_by_token(token)
    if viewer_email == email:
        return True
    return False


def check_token_signature_valid(token: str) -> bool:
    try:
        decoded_token = jwt.decode(
            token, settings.TOKEN_SECRET_KEY, settings.JWT_ALGORITHM
        )
        if decoded_token:
            return True
    except ExpiredSignatureError:
        return False
    except JWTError:
        return False
