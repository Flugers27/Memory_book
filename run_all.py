# run_all.py в корне проекта
import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
    def start_service(self, name: str, path: str, port: int):
        """Запускает сервис в отдельном процессе"""
        print(f"🚀 Starting {name} on port {port}...")
        
        service_path = self.base_dir / path
        log_file = self.base_dir / "logs" / f"{name.lower().replace(' ', '_')}.log"
        
        # Убедимся, что папка для логов существует
        log_file.parent.mkdir(exist_ok=True)
        
        # Команда для запуска
        cmd = [sys.executable, "run.py"]
        
        # Запускаем процесс
        try:
            with open(log_file, 'w') as log:
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(service_path),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                )
            
            self.processes.append((name, proc))
            return proc
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return None
    
    def stop_all(self):
        """Останавливает все сервисы"""
        print("\n🛑 Stopping all services...")
        for name, proc in self.processes:
            if proc and proc.poll() is None:
                print(f"Stopping {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("✅ All services stopped.")
    
    def check_health(self):
        """Проверяет здоровье сервисов"""
        import requests
        
        services = [
            ("Auth", "http://localhost:8001/health"),
            ("Memory", "http://localhost:8002/health"),
            ("Gateway", "http://localhost:8000/health")
        ]
        
        print("\n📊 Service Health Check:")
        print("-" * 40)
        
        for name, url in services:
            try:
                response = requests.get(url, timeout=2)
                status = "✅ Healthy" if response.status_code == 200 else "❌ Unhealthy"
                print(f"{name}: {status} ({url})")
            except Exception as e:
                print(f"{name}: ❌ Unreachable ({str(e)})")

def main():
    manager = ServiceManager()
    
    print("=" * 50)
    print("Memory Book API System")
    print("=" * 50)
    
    try:
        # Запускаем сервисы
        manager.start_service("Auth Service", "services/Auth", 8001)
        time.sleep(2)
        
        manager.start_service("Memory Service", "services/Memory", 8002)
        time.sleep(2)
        
        print("\n⏳ Waiting for services to start...")
        time.sleep(3)
        
        # Проверяем здоровье
        manager.check_health()
        
        print("\n" + "=" * 50)
        print("🚀 Starting API Gateway...")
        print("=" * 50)
        
        # Запускаем Gateway в основном процессе
        gateway_path = manager.base_dir / "gateway"
        os.chdir(gateway_path)
        
        # Импортируем и запускаем Gateway
        import sys
        sys.path.insert(0, str(gateway_path))
        
        import uvicorn
        from gateway.config import settings
        
        uvicorn.run(
            "gateway.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Received interrupt signal")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        manager.stop_all()

if __name__ == "__main__":
    main()