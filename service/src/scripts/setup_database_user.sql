-- 1. Проверяем существование пользователя wb
SELECT usename FROM pg_user WHERE usename = 'wb';

-- 2. Если пользователя нет, создаем его
-- CREATE USER wb WITH PASSWORD 'admin';

-- 3. Даем права на базу данных memory_book_UAT
GRANT CONNECT ON DATABASE memory_book_UAT TO wb;

-- 4. Даем права на использование схем
GRANT USAGE ON SCHEMA public TO wb;
GRANT USAGE ON SCHEMA sys TO wb;

-- 5. Даем права на существующие таблицы
-- Для public схемы
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO wb;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO wb;

-- Для sys схемы
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sys TO wb;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA sys TO wb;

-- 6. Даем права на будущие таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO wb;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO wb;

ALTER DEFAULT PRIVILEGES IN SCHEMA sys GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO wb;
ALTER DEFAULT PRIVILEGES IN SCHEMA sys GRANT USAGE ON SEQUENCES TO wb;

-- 7. Даем право на создание таблиц (если нужно)
-- GRANT CREATE ON SCHEMA public TO wb;
-- GRANT CREATE ON SCHEMA sys TO wb;

-- 8. Проверяем права
\dn+ public
\dn+ sys