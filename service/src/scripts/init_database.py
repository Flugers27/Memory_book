"""
Скрипт для инициализации базы данных
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def init_database():
    """Инициализация базы данных"""
    print("🔄 Инициализация базы данных PostgreSQL...")
    
    try:
        from src.core.database import (
            check_database_connection, 
            create_tables_if_not_exists,
            close_database_connection
        )
        
        # Проверяем подключение
        connected = await check_database_connection()
        if not connected:
            print("❌ Не удалось подключиться к БД")
            return False
        
        # Создаем таблицы
        await create_tables_if_not_exists()
        
        # Закрываем соединения
        await close_database_connection()
        
        print("✅ База данных инициализирована")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Инициализация Memory Book Database")
    print("=" * 50)
    
    success = asyncio.run(init_database())
    
    if success:
        print("\n🎉 База данных готова к работе!")
        print("🚀 Запустите сервис: python main.py")
    else:
        print("\n❌ Не удалось инициализировать базу данных")
        print("Проверьте:")
        print("1. Запущен ли PostgreSQL?")
        print("2. Правильный ли пароль в DATABASE_URL?")
        print("3. Существует ли БД memory_book_UAT?")
        
        # Предлагаем команду для создания БД
        print("\n💡 Создайте БД если её нет:")
        print("createdb -U postgres memory_book_UAT")
    
    input("\nНажмите Enter для выхода...")