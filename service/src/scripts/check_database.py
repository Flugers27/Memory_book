import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в путь Python
project_root = Path(__file__).parent.parent  # service/
sys.path.insert(0, str(project_root))

print(f"🔍 Путь к проекту: {project_root}")
print(f"📁 Содержимое директории: {os.listdir(project_root)}")

# Проверяем, есть ли директория src или scr
source_dir = None
if (project_root / "src").exists():
    source_dir = "src"
    print("✅ Найдена директория: src")
elif (project_root / "scr").exists():
    source_dir = "scr"
    print("✅ Найдена директория: scr (переименуйте в src)")
    # Автоматически добавляем scr в путь
    sys.path.insert(0, str(project_root / "scr"))
else:
    print("❌ Не найдена директория src или scr!")
    print("📁 Доступные директории:")
    for item in project_root.iterdir():
        if item.is_dir():
            print(f"   📂 {item.name}")

try:
    # Пробуем импортировать из src
    if source_dir == "src":
        from src.core.database import engine
    elif source_dir == "scr":
        from scr.core.database import engine  # Импорт из scr
    else:
        raise ImportError("Не найдена директория с исходным кодом")
    
    print("✅ Модуль database успешно загружен")
    
    from sqlalchemy import text
    import asyncio
    
    async def check_connection():
        async with engine.connect() as conn:
            # Проверяем версию PostgreSQL
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ PostgreSQL: {version.split(',')[0]}")
            
            # Проверяем текущую базу данных
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✅ База данных: {db_name}")
            
            # Проверяем пользователя
            result = await conn.execute(text("SELECT current_user"))
            db_user = result.scalar()
            print(f"✅ Пользователь: {db_user}")
            
            return True
    
    print("\n🔍 Проверка подключения к БД...")
    asyncio.run(check_connection())
    
except ImportError as e:
    print(f"\n❌ Ошибка импорта: {e}")
    
    # Создаем минимальный файл для теста
    print("\n🛠️  Создаю минимальный файл database.py для теста...")
    
    # Создаем директорию если нет
    db_dir = project_root / "src" / "core"
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем минимальный database.py
    db_file = db_dir / "database.py"
    db_file.write_text("""
from sqlalchemy.ext.asyncio import create_async_engine

# SQLite для теста
engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)

print("✅ Создан тестовый engine для SQLite")
""")
    
    print(f"✅ Создан файл: {db_file}")
    print("🔄 Перезапустите скрипт...")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")