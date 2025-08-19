from contextlib import asynccontextmanager

import uvicorn
from db.database import Base, engine
from fastapi import FastAPI
from routes.user_routes import route as user_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=user_routes, prefix="/accounts")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
