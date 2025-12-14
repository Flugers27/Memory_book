# services/Memory/run.py
import uvicorn
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

if __name__ == "__main__":
    print(f"🚀 Starting Memory Service...")
    print(f"📡 Host: 0.0.0.0")
    print(f"🔌 Port: 8002")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )