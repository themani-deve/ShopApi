from typing import Any, Optional

from pydantic import BaseModel


class ServiceResult(BaseModel):
    success: bool
    message: Optional[str] = None
    status_code: Optional[int] = None
    data: Optional[Any] = None
