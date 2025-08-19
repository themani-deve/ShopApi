import os

from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Database settings.

DB = {
    "HOST": "postgres_db",
    "NAME": os.getenv("POSTGRES_DB"),
    "USER": os.getenv("POSTGRES_USER"),
    "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    "PORT": 5432,
}

DATABASE_URL = f"postgresql+asyncpg://{DB["USER"]}:{DB["PASSWORD"]}@{DB["HOST"]}:{DB["PORT"]}/{DB['NAME']}"

# JWT Token settings.

with open(os.getenv("JWT_PRIVATE_PATH"), "rb") as f:
    JWT_PRIVATE = f.read().decode("utf-8")

with open(os.getenv("JWT_PUBLIC_PATH"), "rb") as f:
    JWT_PUBLIC = f.read().decode("utf-8")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

ACCESS_EXPIRED_MINUTES = 30
REFRESH_EXPIRED_MINUTES = 60

# Hash password settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])
