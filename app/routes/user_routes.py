from db.database import get_db
from fastapi import Body, Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from schemas import SendActiveKeySchema, TokenSchema, UserSchema
from services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

route = APIRouter()


@route.post("/login", response_model=TokenSchema)
async def login(session: AsyncSession = Depends(get_db), data: UserSchema = Body()):
    tokens = await UserService.login(session=session, email=data.email, password=data.password)

    if not tokens:
        raise HTTPException(status_code=400, detail="Email or password not valid")

    return tokens


@route.post("/register")
async def register(session: AsyncSession = Depends(get_db), data: UserSchema = Body()):
    user = await UserService.register(session=session, email=data.email, password=data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Email does exists")

    return {"detail": "User created successfuly"}


@route.post("/send-key")
async def send_key(session: AsyncSession = Depends(get_db), data: SendActiveKeySchema = Body()):
    user = await UserService.send_key(session=session, email=data.email)

    if not user:
        raise HTTPException(status_code=400, detail="Email does not exists or account is active")

    return {"detail": "Active key has been sent you"}


@route.post("/activate/{active_key}")
async def activate(active_key: str, session: AsyncSession = Depends(get_db)):
    user = await UserService.activate(session=session, active_key=active_key)

    if not user:
        raise HTTPException(status_code=400, detail="Active key not valid")

    return {"detail": "Your account has been activated"}
