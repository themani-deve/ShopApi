from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from .exceptions import *


async def cart_exception_handler(request: Request, exc: CartError):
    if isinstance(exc, CartNotFoundError):
        status_code = 404
    else:
        status_code = 400

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
