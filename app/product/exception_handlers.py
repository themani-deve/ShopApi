from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from .exception import ProductError, ProductNotFoundError


async def product_exception_handler(request: Request, exc: ProductError):
    if isinstance(exc, ProductNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
