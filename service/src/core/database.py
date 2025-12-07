"""
Настройка подключения к PostgreSQL для вашей БД memory_book_UAT
"""
import os
import sys
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, MetaData

# Добавляем корневую директорию в sys.path для импорта настроек
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config import settings
    print(f"✅ Настройки загружены из: {settings.DATABASE_URL}")
except ImportError:
    print("⚠️  Не удалось загрузить настройки, используем значения по умолчанию")
    
    # Создаем простые настройки
    class SimpleSettings:
        DATABASE_URL = "postgresql+asyncpg://wb:admin@localhost:5432/memory_book_UAT?search_path=public,sys"
        DEBUG = True
    
    settings = SimpleSettings()

class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Автоматически наследует схему из __table_args__
    """
    metadata = MetaData(schema="public")  # Схема по умолчанию

# Создаем асинхронный engine для PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    # Параметры подключения
    echo=settings.DEBUG,  # Логирование SQL запросов в консоль
    echo_pool=False,      # Логирование пула соединений
    pool_size=10,         # Размер пула соединений
    max_overflow=20,      # Максимальное количество соединений сверх pool_size
    pool_pre_ping=True,   # Проверять соединение перед использованием
    pool_recycle=3600,    # Пересоздавать соединения каждый час
    pool_timeout=30,      # Таймаут ожидания соединения из пула
    connect_args={
        "server_settings": {
            "application_name": "memory_book_service",
            "search_path": "public,sys"  # Указываем схемы для поиска
        }
    }
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не сбрасывать объекты после коммита
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии БД.
    
    Использование:
    ```python
    async def some_function(db: AsyncSession = Depends(get_db)):
        # работа с БД через db
    ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Автоматический коммит после успешного выполнения
        except Exception:
            await session.rollback()  # Откат при ошибке
            raise
        finally:
            await session.close()  # Всегда закрываем сессию

async def check_database_connection() -> bool:
    """
    Проверка подключения к базе данных.
    
    Возвращает:
        bool: True если подключение успешно, False в случае ошибки
    """
    try:
        async with engine.connect() as conn:
            # Выполняем простой запрос для проверки
            result = await conn.execute(text("SELECT 1"))
            data = result.scalar()
            
            if data == 1:
                print("✅ Подключение к PostgreSQL успешно")
                
                # Получаем дополнительную информацию
                db_info = await conn.execute(text(
                    "SELECT version(), current_database(), current_user"
                ))
                version, db_name, db_user = db_info.fetchone()
                
                print(f"   📊 Версия: {version.split(',')[0]}")
                print(f"   📁 База данных: {db_name}")
                print(f"   👤 Пользователь: {db_user}")
                
                # Проверяем схемы
                schemas = await conn.execute(text("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name IN ('public', 'sys')
                    ORDER BY schema_name
                """))
                
                available_schemas = [row[0] for row in schemas.fetchall()]
                print(f"   📋 Доступные схемы: {available_schemas}")
                
                return True
            else:
                print("❌ Неожиданный ответ от БД")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        return False

async def create_tables_if_not_exists():
    """
    Создание таблиц, если они не существуют.
    Безопасно для существующих таблиц.
    """
    try:
        async with engine.begin() as conn:
            # Проверяем существование таблицы users
            table_exists = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                )
            """))
            
            if not table_exists.scalar():
                print("📝 Создание таблиц...")
                
                # Создаем таблицу users
                await conn.execute(text("""
                    CREATE TABLE public.users (
                        id_user UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        email VARCHAR(255) UNIQUE NOT NULL,
                        username VARCHAR(100) UNIQUE,
                        full_name VARCHAR(100),
                        avatar_url TEXT,
                        password_hash VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT true,
                        is_verified BOOLEAN DEFAULT false,
                        last_login_at TIMESTAMPTZ,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """))
                print("✅ Таблица users создана")
                
                # Создаем таблицу refresh_tokens в схеме sys
                await conn.execute(text("""
                    CREATE SCHEMA IF NOT EXISTS sys
                """))
                
                await conn.execute(text("""
                    CREATE TABLE sys.refresh_tokens (
                        id_user_token UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES public.users(id_user) ON DELETE CASCADE,
                        token_hash VARCHAR(512) NOT NULL,
                        device_info TEXT,
                        ip_address INET,
                        expires_at TIMESTAMPTZ NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(user_id, device_info)
                    )
                """))
                print("✅ Таблица refresh_tokens создана")
                
                # Создаем индексы
                await conn.execute(text("""
                    CREATE INDEX idx_users_email ON public.users(email);
                    CREATE INDEX idx_users_username ON public.users(username);
                    CREATE INDEX idx_refresh_tokens_user_id ON sys.refresh_tokens(user_id);
                    CREATE INDEX idx_refresh_tokens_token_hash ON sys.refresh_tokens(token_hash);
                """))
                print("✅ Индексы созданы")
            else:
                print("✅ Таблицы уже существуют")
                
    except Exception as e:
        print(f"⚠️  Ошибка при создании таблиц: {e}")

async def close_database_connection():
    """
    Корректное закрытие соединений с базой данных.
    Вызывать при завершении работы приложения.
    """
    await engine.dispose()
    print("🔌 Соединения с БД закрыты")

# Тестовая функция для проверки
if __name__ == "__main__":
    import asyncio
    
    print("🔍 Тестирование подключения к PostgreSQL...")
    print(f"📡 URL подключения: {settings.DATABASE_URL}")
    
    async def test():
        # Проверяем подключение
        success = await check_database_connection()
        
        if success:
            # Создаем таблицы если нужно
            await create_tables_if_not_exists()
            
            # Тестируем сессию
            async with AsyncSessionLocal() as session:
                # Проверяем существующие таблицы
                result = await session.execute(text("""
                    SELECT table_schema, table_name 
                    FROM information_schema.tables 
                    WHERE table_schema IN ('public', 'sys')
                    ORDER BY table_schema, table_name
                """))
                
                tables = result.fetchall()
                print(f"\n📋 Таблицы в базе данных ({len(tables)}):")
                for schema, table in tables:
                    print(f"   {schema}.{table}")
        
        await close_database_connection()
    
    asyncio.run(test())