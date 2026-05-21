import sys
sys.path.append('.')
from database.engine import engine

with engine.connect() as conn:
    # Проверяем существование таблицы media
    result = conn.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'media'
    """)
    if result.fetchone():
        print("Таблица media существует")
        # Получаем колонки
        cols = conn.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'media'
            ORDER BY ordinal_position
        """)
        for col in cols:
            print(f"{col.column_name} ({col.data_type}) {'NULL' if col.is_nullable == 'YES' else 'NOT NULL'}")
    else:
        print("Таблица media не существует")