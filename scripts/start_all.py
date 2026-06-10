#!/usr/bin/env python3
"""
Запуск всех сервисов через subprocess
"""
import subprocess
import sys
import os
import time
import signal

def start_service(name, path, port):
    """Запускает сервис в отдельном процессе"""
    print(f"🚀 Starting {name} on port {port}...")
    
    # Команда для запуска
    cmd = [sys.executable, "run.py"]
    
    # Запускаем процесс
    proc = subprocess.Popen(
        cmd,
        cwd=path,
        stdout=open(f"logs/{name.lower()}.log", "w"),
        stderr=subprocess.STDOUT,
        shell=True
    )
    
    # Даем время на запуск
    time.sleep(2)
    
    return proc

def main():
    # Создаем папку для логов
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    print("=" * 50)
    print("Starting Memory Book API System")
    print("=" * 50)
    
    processes = []
    
    try:
        # Запускаем Auth Service
        auth_proc = start_service(
            "Auth Service",
            "services/Auth",
            8001
        )
        processes.append(auth_proc)
        
        # Запускаем Memory Service
        memory_proc = start_service(
            "Memory Service",
            "services/Memory",
            8002
        )
        processes.append(memory_proc)
        
        # Запускаем Access Service
        access_proc = start_service(
            "Access Service",
            "services/Acces_Memory",
            8003
        )
        processes.append(access_proc)
        
        # Запускаем Family Tree Service
        family_proc = start_service(
            "Family Tree Service",
            "services/Family_Tree",
            8005
        )
        processes.append(family_proc)
        
        # Даем время сервисам на запуск
        print("\n⏳ Waiting for services to start...")
        time.sleep(5)
        
        # Запускаем Gateway
        print("\n🚀 Starting API Gateway on port 8000...")
        print("=" * 50)
        
        gateway_cmd = [sys.executable, "gateway/run.py"]
        subprocess.run(gateway_cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all services...")
    finally:
        # Останавливаем все процессы
        for proc in processes:
            if proc:
                proc.terminate()
                proc.wait()
        
        print("✅ All services stopped.")

if __name__ == "__main__":
    main()