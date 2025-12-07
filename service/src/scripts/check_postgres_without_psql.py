import sys
import os
import asyncio
from sqlalchemy import create_engine
from sqlalchemy import text

async def check_postgres_with_python():
    """Проверка PostgreSQL через SQLAlchemy без psql"""
    
    print("🔍 Проверка подключения к PostgreSQL через Python...")
    
    # URL подключения как в .env
    database_url = "postgresql+asyncpg://wb:admin@localhost:5432/memory_book_UAT"
    
    try:
        # Создаем синхронный engine для проверки
        sync_url = database_url.replace("+asyncpg", "+psycopg2")
        engine = create_engine(sync_url)
        
        with engine.connect() as conn:
            # 1. Проверяем версию PostgreSQL
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ PostgreSQL найден: {version.split(',')[0]}")
            
            # 2. Проверяем текущую базу данных
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✅ База данных: {db_name}")
            
            # 3. Проверяем пользователя
            result = conn.execute(text("SELECT current_user"))
            db_user = result.scalar()
            print(f"✅ Пользователь: {db_user}")
            
            # 4. Проверяем существование пользователя wb
            result = conn.execute(text("SELECT usename FROM pg_user WHERE usename = 'wb'"))
            wb_user = result.scalar()
            
            if wb_user:
                print(f"✅ Пользователь 'wb' существует")
            else:
                print(f"❌ Пользователь 'wb' не найден")
                print("\nДля создания пользователя выполните:")
                print("1. Запустите pgAdmin или другой клиент PostgreSQL")
                print("2. Подключитесь как postgres")
                print("3. Выполните: CREATE USER wb WITH PASSWORD 'admin';")
                return False
            
            # 5. Проверяем таблицы
            result = conn.execute(text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema IN ('public', 'sys')
                ORDER BY table_schema, table_name
            """))
            
            tables = result.fetchall()
            print(f"\n📋 Найдено таблиц: {len(tables)}")
            
            for schema, table in tables[:5]:  # Показываем первые 5
                print(f"   {schema}.{table}")
            
            if len(tables) > 5:
                print(f"   ... и еще {len(tables) - 5} таблиц")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        
        print("\n🔧 Устранение проблем:")
        print("1. Убедитесь, что PostgreSQL запущен")
        print("2. Проверьте правильность данных в .env файле")
        print("3. Установите драйвер: pip install psycopg2-binary asyncpg")
        
        return False

if __name__ == "__main__":
    # Устанавливаем psycopg2 если нет
    try:
        import psycopg2
    except ImportError:
        print("📦 Установка psycopg2-binary...")
        os.system(f"{sys.executable} -m pip install psycopg2-binary")
    
    asyncio.run(check_postgres_without_psql())