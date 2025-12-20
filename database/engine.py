"""
Подключение к PostgreSQL.
"""
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL не задан")

def get_engine():
    return create_engine(
        DATABASE_URL,
        echo=DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_pre_ping=True,
        future=True,
    )

engine = get_engine()
