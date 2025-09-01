from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from .exceptions import *


async def cart_exception_handler(request: Request, exc: CartError):
    if isinstance(exc, CartNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, GatewayError):
        status_code = status.HTTP_502_BAD_GATEWAY
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
