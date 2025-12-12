# run_all.py
import subprocess
import time
import sys
import os
from threading import Thread

def run_service(command, name):
    """Запускает сервис в отдельном потоке"""
    print(f"🚀 Запуск {name}...")
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        
        # Выводим логи
        for line in iter(process.stdout.readline, ''):
            print(f"[{name}] {line}", end='')
        
        process.wait()
    except Exception as e:
        print(f"❌ Ошибка запуска {name}: {e}")

def main():
    print("=" * 50)
    print("🚀 Запуск всех сервисов Memory Book")
    print("=" * 50)
    
    # Команды для запуска сервисов
    services = [
        {
            "name": "Auth Service (8000)",
            "command": "uvicorn services.Auth.main:app --host 0.0.0.0 --port 8000"
        },
        {
            "name": "Memory Service (8001)", 
            "command": "uvicorn services.Memory.main:app --host 0.0.0.0 --port 8001"
        },
        {
            "name": "Gateway (8080)",
            "command": "uvicorn gateway:app --host 0.0.0.0 --port 8080"
        }
    ]
    
    # Запускаем все сервисы в отдельных потоках
    threads = []
    for service in services:
        thread = Thread(target=run_service, args=(service["command"], service["name"]))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(2)  # Небольшая задержка между запусками
    
    print("\n" + "=" * 50)
    print("✅ Все сервисы запущены!")
    print("=" * 50)
    print("\n📊 Доступные сервисы:")
    print("   • Auth Service:    http://localhost:8000")
    print("   • Memory Service:  http://localhost:8001")  
    print("   • Gateway:         http://localhost:8080")
    print("\n📚 Документация:")
    print("   • Auth Docs:       http://localhost:8000/docs")
    print("   • Memory Docs:     http://localhost:8001/docs")
    print("   • Gateway:         http://localhost:8080")
    print("\n🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Держим скрипт запущенным
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n👋 Остановка всех сервисов...")
        sys.exit(0)

if __name__ == "__main__":
    # Проверяем что мы в виртуальном окружении
    if not os.path.exists("venv"):
        print("❌ Виртуальное окружение не найдено!")
        print("   Сначала выполните: python -m venv venv")
        sys.exit(1)
    
    # Переходим в корень проекта
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    main()