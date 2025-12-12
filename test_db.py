# test_db.py
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="memory_book_UAT",
        user="wb",
        password="admin",
        host="localhost",
        port="5432"
    )
    print("✅ Подключение к PostgreSQL успешно!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Версия PostgreSQL: {db_version[0]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")