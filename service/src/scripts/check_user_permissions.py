import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.core.database import engine

async def check_user_permissions():
    """Проверка прав пользователя wb в БД"""
    try:
        async with engine.connect() as conn:
            # 1. Проверяем текущего пользователя
            result = await conn.execute(text("SELECT current_user"))
            current_user = result.scalar()
            print(f"✅ Текущий пользователь: {current_user}")
            
            # 2. Проверяем доступные схемы
            result = await conn.execute(text("""
                SELECT nspname 
                FROM pg_namespace 
                WHERE nspname IN ('public', 'sys')
                ORDER BY nspname
            """))
            schemas = [row[0] for row in result.fetchall()]
            print(f"✅ Доступные схемы: {schemas}")
            
            # 3. Проверяем права на схемы
            for schema in ['public', 'sys']:
                result = await conn.execute(text(f"""
                    SELECT has_schema_privilege('{schema}', 'USAGE') as has_usage,
                           has_schema_privilege('{schema}', 'CREATE') as has_create
                """))
                row = result.fetchone()
                print(f"🔑 Права на схему '{schema}':")
                print(f"   USAGE: {'✅' if row[0] else '❌'}")
                print(f"   CREATE: {'✅' if row[1] else '❌'}")
            
            # 4. Проверяем права на существующие таблицы
            result = await conn.execute(text("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema IN ('public', 'sys')
                ORDER BY table_schema, table_name
            """))
            
            tables = result.fetchall()
            print(f"\n📋 Проверка прав на таблицы:")
            
            for schema, table in tables:
                result = await conn.execute(text(f"""
                    SELECT 
                        has_table_privilege('{schema}.{table}', 'SELECT') as can_select,
                        has_table_privilege('{schema}.{table}', 'INSERT') as can_insert,
                        has_table_privilege('{schema}.{table}', 'UPDATE') as can_update,
                        has_table_privilege('{schema}.{table}', 'DELETE') as can_delete
                """))
                row = result.fetchone()
                
                permissions = []
                if row[0]: permissions.append("SELECT")
                if row[1]: permissions.append("INSERT")
                if row[2]: permissions.append("UPDATE")
                if row[3]: permissions.append("DELETE")
                
                print(f"   {schema}.{table}: {', '.join(permissions) if permissions else '❌ Нет прав'}")
            
            # 5. Проверяем возможность создания таблиц
            result = await conn.execute(text("""
                SELECT has_database_privilege(current_database(), 'CREATE') as can_create_db,
                       has_database_privilege(current_database(), 'TEMPORARY') as can_create_temp
            """))
            row = result.fetchone()
            print(f"\n🏗️  Права в БД:")
            print(f"   CREATE DATABASE: {'✅' if row[0] else '❌'}")
            print(f"   CREATE TEMP TABLES: {'✅' if row[1] else '❌'}")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка проверки прав: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Проверка прав пользователя wb в БД memory_book_UAT")
    print("=" * 60)
    
    success = asyncio.run(check_user_permissions())
    
    print("=" * 60)
    if success:
        print("✅ Проверка прав завершена")
    else:
        print("❌ Есть проблемы с правами доступа")
        sys.exit(1)