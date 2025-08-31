from contextlib import asynccontextmanager

import uvicorn
from account.exception_handlers import account_exception_handler, auth_exception_handler
from account.exceptions import AccountError, AuthenticationError
from account.routes import route as account_routes
from cart.exception_handlers import cart_exception_handler
from cart.exceptions import CartError
from cart.routes import route as cart_routes
from db.database import Base, engine
from fastapi import FastAPI
from product.exception import ProductError
from product.exception_handlers import product_exception_handler
from product.routes import route as product_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=account_routes, prefix="/accounts")
app.include_router(router=product_routes, prefix="/products")
app.include_router(router=cart_routes, prefix="/cart")

app.add_exception_handler(AccountError, account_exception_handler)
app.add_exception_handler(AuthenticationError, auth_exception_handler)
app.add_exception_handler(ProductError, product_exception_handler)
app.add_exception_handler(CartError, cart_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
