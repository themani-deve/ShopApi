from fastapi import Depends
from fastapi.exceptions import HTTPException
from routes.user import oauth2_scheme
from schemas.user import TokenDataSchema
from services.jwt import JWTService


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

    return TokenDataSchema(**payload)


def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)


def is_admin(token: str = Depends(oauth2_scheme)):
    return verify_token(token, require_admin=True)
