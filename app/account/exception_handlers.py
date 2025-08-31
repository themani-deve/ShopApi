from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from .exceptions import *


async def account_exception_handler(request: Request, exc: AccountError):
    if isinstance(exc, InvalidCredentialsError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, UserNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, UserIsNotAdminError):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


async def auth_exception_handler(requesr: Request, exc: AuthenticationError):
    if isinstance(exc, TokenExpiredError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, InvalidTokenError):
        status_code = status.HTTP_403_FORBIDDEN
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
