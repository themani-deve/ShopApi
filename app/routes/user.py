from core.dependencies.user import get_current_user
from db.database import get_db
from fastapi import Body, Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer
from schemas.user import *
from services.user import UserService
from sqlalchemy.ext.asyncio import AsyncSession

route = APIRouter()


@route.post("/login", response_model=TokenSchema, tags=["Account"])
async def login(session: AsyncSession = Depends(get_db), data: LoginSchema = Body()):
    response = await UserService.login(session=session, email=data.email, password=data.password)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return response.data


@route.post("/register", tags=["Account"])
async def register(session: AsyncSession = Depends(get_db), data: RegisterSchema = Body()):
    response = await UserService.register(session=session, email=data.email, password=data.password)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return {"detail": response.message}


@route.post("/send-key", tags=["Account"])
async def send_key(session: AsyncSession = Depends(get_db), data: SendKeySchema = Body()):
    response = await UserService.send_key(session=session, email=data.email)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return {"detail": response.message}


@route.post("/change-password/{key}", tags=["Account"])
async def change_password(key: str, session: AsyncSession = Depends(get_db), data: ChangePasswordSchema = Body()):
    response = await UserService.change_password(session=session, key=key, new_pass=data.password)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return {"detail": response.message}


@route.get("/activate/{key}", tags=["Account"])
async def activate(key: str, session: AsyncSession = Depends(get_db)):
    response = await UserService.activate(session=session, key=key)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return {"detail": response.message}


@route.delete("/delete", tags=["Account"])
async def delete(session: AsyncSession = Depends(get_db), user: TokenDataSchema = Depends(get_current_user)):
    response = await UserService.delete(session=session, user=user)

    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.message)

    return {"detail": response.message}
