from db.database import get_db
from fastapi import Body, Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from schemas import *
from services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

route = APIRouter()


@route.post("/login", response_model=TokenSchema)
async def login(session: AsyncSession = Depends(get_db), data: LoginSchema = Body()):
    tokens = await UserService.login(session=session, email=data.email, password=data.password)

    if not tokens:
        raise HTTPException(status_code=400, detail="Email or password not valid")

    return tokens


@route.post("/register")
async def register(session: AsyncSession = Depends(get_db), data: RegisterSchema = Body()):
    if not data.is_equal:
        return HTTPException(status_code=400, detail="Password and confirm password not equal")

    user = await UserService.register(session=session, email=data.email, password=data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Email does exists")

    return {"detail": "User created successfuly"}


@route.post("/send-key")
async def send_key(session: AsyncSession = Depends(get_db), data: SendKeySchema = Body()):
    user = await UserService.send_key(session=session, email=data.email)

    if not user:
        raise HTTPException(status_code=400, detail="Email does not exists or account is active")

    return {"detail": "Key has been sent you"}


@route.post("/change-password/{key}")
async def change_password(key: str, session: AsyncSession = Depends(get_db), data: ChangePasswordSchema = Body()):
    if not data.is_equal:
        return HTTPException(status_code=400, detail="Password and confirm password not equal")

    user = await UserService.change_password(session=session, key=key, new_pass=data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Key not valid")

    return {"detail": "Your password changed successfuly"}


@route.get("/activate/{active_key}")
async def activate(key: str, session: AsyncSession = Depends(get_db)):
    user = await UserService.activate(session=session, key=key)

    if not user:
        raise HTTPException(status_code=400, detail="Key not valid or account is activated")

    return {"detail": "Your account has been activated"}
