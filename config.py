"""
Корневой конфигурационный файл.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", 12))

    # CORS
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    ).split(",")

    # Environment
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Ports
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", 8000))
    AUTH_PORT: int = int(os.getenv("AUTH_PORT", 8001))
    MEMORY_PORT: int = int(os.getenv("MEMORY_PORT", 8002))
    ACCESS_PORT: int = int(os.getenv("ACCESS_PORT", 8003))

    # URLs
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    MEMORY_SERVICE_URL: str = os.getenv("MEMORY_SERVICE_URL", "http://localhost:8002")
    ACCESS_SERVICE_URL: str = os.getenv("ACCESS_SERVICE_URL", "http://localhost:8003")


config = BaseConfig()
