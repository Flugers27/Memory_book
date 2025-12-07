import asyncio
import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import engine, Base
from src.models.user import User
from src.models.token import RefreshToken

async def check_existing_tables():
    """Проверка существующих таблиц"""
    from sqlalchemy import inspect
    
    async with engine.connect() as conn:
        inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
        
        print("Проверка таблиц в схеме public:")
        tables_public = await conn.run_sync(lambda sync_conn: inspector.get_table_names(schema="public"))
        print(f"Найдены таблицы: {tables_public}")
        
        print("\nПроверка таблиц в схеме sys:")
        tables_sys = await conn.run_sync(lambda sync_conn: inspector.get_table_names(schema="sys"))
        print(f"Найдены таблицы: {tables_sys}")
        
        return tables_public, tables_sys

async def sync_models():
    """Синхронизация моделей с существующими таблицами (без создания новых)"""
    async with engine.begin() as conn:
        # Проверяем, существует ли таблица users
        inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
        existing_tables = await conn.run_sync(
            lambda sync_conn: inspector.get_table_names(schema="public")
        )
        
        if "users" not in existing_tables:
            print("Создание таблицы users...")
            await conn.run_sync(Base.metadata.create_all, tables=[User.__table__])
        else:
            print("Таблица users уже существует")
        
        if "refresh_tokens" not in await conn.run_sync(
            lambda sync_conn: inspector.get_table_names(schema="sys")
        ):
            print("Создание таблицы refresh_tokens...")
            await conn.run_sync(Base.metadata.create_all, tables=[RefreshToken.__table__])
        else:
            print("Таблица refresh_tokens уже существует")

if __name__ == "__main__":
    print("=== Проверка подключения к БД memory_book_UAT ===")
    asyncio.run(check_existing_tables())
    print("\n=== Синхронизация моделей ===")
    asyncio.run(sync_models())