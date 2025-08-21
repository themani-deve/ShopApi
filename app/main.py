from contextlib import asynccontextmanager

import uvicorn
from db.database import Base, engine
from fastapi import FastAPI
from routes.product import route as product_routes
from routes.user import route as user_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=user_routes, prefix="/accounts")
app.include_router(router=product_routes, prefix="/products")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
