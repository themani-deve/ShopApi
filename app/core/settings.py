import os

from dotenv import load_dotenv

load_dotenv()

DB = {
    "HOST": "postgres_db",
    "NAME": os.getenv("POSTGRES_DB"),
    "USER": os.getenv("POSTGRES_USER"),
    "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    "PORT": 5432,
}

DATABASE_URL = f"postgresql+asyncpg://{DB["USER"]}:{DB["PASSWORD"]}@{DB["HOST"]}:{DB["PORT"]}/{DB['NAME']}"
