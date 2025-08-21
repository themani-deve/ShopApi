import datetime

from core.settings import *
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError


class JWTService:
    @staticmethod
    def create_access(payload: dict):
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_EXPIRED_MINUTES)

        data = payload.copy()
        data.update({"exp": exp, "type": "access"})

        return jwt.encode(data, key=JWT_PRIVATE, algorithm=JWT_ALGORITHM)

    @staticmethod
    def create_refresh(payload: dict):
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_EXPIRED_MINUTES)

        data = {"id": payload.get("id")}
        data.update({"exp": exp, "type": "refresh"})

        return jwt.encode(data, key=JWT_PRIVATE, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode(token: str):
        try:
            payload = jwt.decode(token=token, key=JWT_PUBLIC, algorithms=[JWT_ALGORITHM])

            if payload.get("type") == "refresh":
                raise JWTError("Token type not valid")

            return payload

        except ExpiredSignatureError:
            return None

        except JWTError:
            return None
