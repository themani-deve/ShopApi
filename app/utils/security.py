from core.settings import pwd_context
from passlib.exc import InvalidHashError


def hashed_password(plain_pass: str):
    return pwd_context.hash(plain_pass)


def verify_password(plain_pass: str, hashed_pass: str):
    try:
        return pwd_context.verify(plain_pass, hashed_pass)
    except InvalidHashError:
        return False
    except InvalidHashError:
        return False
