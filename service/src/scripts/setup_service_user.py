import subprocess
import sys
import os

def setup_service_user():
    """Настройка пользователя wb в PostgreSQL"""
    
    print("🔧 Настройка пользователя wb для сервиса...")
    
    # Параметры подключения (администратор)
    admin_user = "postgres"
    admin_password = input("Введите пароль пользователя postgres: ")
    db_name = "memory_book_UAT"
    
    # SQL команды для настройки
    sql_commands = [
        f"\\c {db_name}",
        "-- Проверяем существование пользователя wb",
        "DO $$ ",
        "BEGIN ",
        "  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'wb') THEN ",
        "    CREATE USER wb WITH PASSWORD 'admin'; ",
        "    RAISE NOTICE 'Пользователь wb создан'; ",
        "  ELSE ",
        "    RAISE NOTICE 'Пользователь wb уже существует'; ",
        "  END IF; ",
        "END $$;",
        "",
        "-- Даем права на базу данных",
        f"GRANT CONNECT ON DATABASE {db_name} TO wb;",
        "",
        "-- Даем права на схемы",
        "GRANT USAGE ON SCHEMA public TO wb;",
        "GRANT USAGE ON SCHEMA sys TO wb;",
        "",
        "-- Даем права на все таблицы в public",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO wb;",
        "GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO wb;",
        "",
        "-- Даем права на все таблицы в sys",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sys TO wb;",
        "GRANT USAGE ON ALL SEQUENCES IN SCHEMA sys TO wb;",
        "",
        "-- Даем права на будущие таблицы",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO wb;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO wb;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA sys GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO wb;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA sys GRANT USAGE ON SEQUENCES TO wb;",
        "",
        "\\q"
    ]
    
    # Создаем временный SQL файл
    sql_file = "temp_setup.sql"
    with open(sql_file, "w") as f:
        f.write("\n".join(sql_commands))
    
    try:
        # Запускаем psql с паролем
        env = os.environ.copy()
        env['PGPASSWORD'] = admin_password
        
        print("🔧 Выполнение SQL команд...")
        result = subprocess.run(
            ["psql", "-U", admin_user, "-f", sql_file, "-h", "localhost"],
            env=env,
            capture_output=True,
            text=True
        )
        
        # Удаляем временный файл
        os.remove(sql_file)
        
        if result.returncode == 0:
            print("✅ Настройка пользователя wb завершена успешно!")
            print("\nДетали выполнения:")
            print(result.stdout)
        else:
            print("❌ Ошибка при настройке пользователя:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ Ошибка: psql не найден. Убедитесь, что PostgreSQL установлен и в PATH.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🛠️  Настройка пользователя сервиса wb в PostgreSQL")
    print("=" * 50)
    
    response = input("Вы хотите настроить пользователя wb? (y/n): ")
    if response.lower() == 'y':
        setup_service_user()
    else:
        print("Отмена настройки.")