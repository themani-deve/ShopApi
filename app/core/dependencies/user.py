from typing import Optional

from account.schemas import TokenData
from account.services import JWTService
from core.settings import oauth2_scheme
from fastapi import Depends, Header
from fastapi.exceptions import HTTPException


def verify_token(token: str, require_admin: bool = False):
    payload = JWTService.decode(token=token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if require_admin and not payload.get("is_staff", False):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this endpoint",
        )

    return TokenData(**payload)


def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token=token)


def is_admin(token: str = Depends(oauth2_scheme)):
    return verify_token(token=token, require_admin=True)


def login_optional(authorization: Optional[str] = Header(None)):
    if authorization:
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=401, detail="Invalid authentication scheme")
            return verify_token(token=token)
        except:
            return None
    return None
