from core.dependencies.user import get_user
from db.database import get_db
from fastapi import Body, Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import *
from .services import AccountService, StringResponse

route = APIRouter()


@route.post("/register", response_model=StringResponse, tags=["Account"])
async def register(db: AsyncSession = Depends(get_db), data: CreateUser = Body()):
    service = AccountService(db=db)
    return await service.create_user(data=data)


@route.post("/login", response_model=Token, tags=["Account"])
async def login(db: AsyncSession = Depends(get_db), data: LoginUser = Body()):
    service = AccountService(db=db)
    return await service.login_user(data=data)


@route.post("/send-key", response_model=StringResponse, tags=["Account"])
async def send_key(db: AsyncSession = Depends(get_db), data: SendKeyInput = Body()):
    service = AccountService(db=db)
    return await service.send_key(data=data)


@route.post("/change-password/{key}", response_model=StringResponse, tags=["Account"])
async def change_password(key, db: AsyncSession = Depends(get_db), data: ChangePassword = Body()):
    service = AccountService(db=db)
    return await service.change_password(key=key, data=data)


@route.get("/activate/{key}", response_model=StringResponse, tags=["Account"])
async def activate_account(key: str, db: AsyncSession = Depends(get_db)):
    service = AccountService(db=db)
    return await service.activate_account(key=key)


@route.delete("/delete", response_model=StringResponse, tags=["Account"])
async def delete_account(db: AsyncSession = Depends(get_db), user: TokenData = Depends(get_user)):
    services = AccountService(db=db)
    return await services.delete_account(user=user)
