from db.database import get_db
from fastapi import Body, Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from schemas import TokenSchema, UserSchema
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
