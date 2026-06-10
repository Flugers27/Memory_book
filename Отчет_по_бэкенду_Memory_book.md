# Отчет по бекэнду проекта Memory Book

## 1. Общий обзор

Проект Memory Book использует микросервисную архитектуру на базе FastAPI и SQLAlchemy. Основной бекэнд состоит из:

- API Gateway — единая точка входа для внешних запросов;
- Auth Service — аутентификация, авторизация, токены, профиль пользователя;
- Memory Service — хранение и управление агентами, страницами и публичными memory page;
- Access Management Service — управление доступом к страницам;
- Media Service — загрузка, подтверждение и управление медиафайлами.

Внутри проекта также есть вспомогательные сервисные директории и база данных с SQLAlchemy-моделями.

---

## 2. Архитектура и взаимодействие сервисов

### 2.1 API Gateway

Gateway реализован в [gateway/main.py](gateway/main.py) и является основным входом для клиентского фронтенда.

Его функции:
- принимает все запросы через общий маршрут /{service}/{path:path};
- проверяет доступность сервисов через /health и /health/all;
- выполняет базовую проверку аутентификации;
- проксирует запросы к микросервисам через [gateway/proxy.py](gateway/proxy.py);
- логирует запросы и собирает метрики через [gateway/middleware.py](gateway/middleware.py).

Ключевые настройки Gateway находятся в [gateway/config.py](gateway/config.py):
- порт по умолчанию: 8000;
- базовые сервисные URL: Auth = 8001, Memory = 8002;
- список публичных маршрутов;
- маршруты проксирования сервисов.

### 2.2 Микросервисы

#### Auth Service
Реализован в [services/Auth/main.py](services/Auth/main.py).

Отвечает за:
- регистрацию пользователей;
- вход по email/паролю;
- выпуск access/refresh токенов;
- обновление и отзыв токенов;
- работу с профилем пользователя.

Основные роутеры:
- [services/Auth/routers/auth.py](services/Auth/routers/auth.py) — /auth/register, /auth/login, /auth/refresh, /auth/logout, /auth/validate;
- [services/Auth/routers/users.py](services/Auth/routers/users.py) — /users/me, /users/me/password, /users/me/tokens, /users/me/tokens/revoke-all.

#### Memory Service
Реализован в [services/Memory/main.py](services/Memory/main.py).

Отвечает за:
- список и управление агентами;
- список и управление страницами памяти;
- публичные memory page, доступные без авторизации;
- приватные страницы пользователя.

Основные роутеры:
- [services/Memory/routers/agents.py](services/Memory/routers/agents.py);
- [services/Memory/routers/pages.py](services/Memory/routers/pages.py);
- [services/Memory/routers/memory_pages.py](services/Memory/routers/memory_pages.py);
- [services/Memory/routers/health.py](services/Memory/routers/health.py).

#### Access Management Service
Реализован в [services/Acces_Memory/main.py](services/Acces_Memory/main.py).

Отвечает за:
- предоставление и отзыв доступа к страницам памяти;
- проверку прав просмотра/редактирования;
- просмотр списка доступов текущего пользователя и предоставленных им доступов.

Основной роутер:
- [services/Acces_Memory/routers/access.py](services/Acces_Memory/routers/access.py).

#### Media Service
Реализован в [services/Media/main.py](services/Media/main.py).

Отвечает за:
- загрузку медиафайлов;
- временные и постоянные файлы;
- подтверждение временных файлов;
- просмотр и удаление медиа;
- очистку устаревших временных файлов.

Основной роутер:
- [services/Media/routers/media.py](services/Media/routers/media.py).

---

## 3. Основные эндпоинты

### 3.1 Gateway

Gateway предоставляет следующие ключевые точки входа:
- GET / — информация о gateway и доступных сервисах;
- GET /health — проверка живости gateway;
- GET /health/all — проверка живости всех зарегистрированных сервисов;
- все остальные запросы идут через общий маршрут /{service}/{path:path}.

Подход проксирования:
- /auth/... → Auth Service;
- /memory/... → Memory Service;
- /agent/... и /page/... → Memory Service.

Важно: в текущей конфигурации Gateway напрямую не маршрутизирует Access Service и Media Service. Они запускаются отдельно и не входят в основной список маршрутов gateway.

### 3.2 Auth Service

Публичные:
- POST /auth/register — регистрация пользователя;
- POST /auth/login — вход и выдача токенов;
- POST /auth/refresh — обновление refresh-token;
- POST /auth/logout — выход;
- POST /auth/validate — проверка токена.

Защищённые:
- GET /users/me — профиль текущего пользователя;
- PUT /users/me — обновление профиля;
- PUT /users/me/password — смена пароля;
- GET /users/me/tokens — список активных refresh-токенов;
- POST /users/me/tokens/revoke-all — отзыв всех токенов.

### 3.3 Memory Service

Публичные memory page:
- GET /public_memory_page_list — список публичных memory page;
- GET /public_memory_page/{agent_id} — публичная memory page по агенту.

Личный контур пользователя:
- GET /memory_page_list — список собственных страниц;
- GET /memory_page/{agent_id} — данные страницы и связанных агентов.

Управление агентами:
- GET /agent_list;
- GET /agent/{agent_id};
- POST /agent/add;
- PUT /agent/update/{agent_id};
- DELETE /agent/del/{agent_id}.

Управление страницами:
- GET /page_list/{agent_id};
- GET /page/{page_id};
- POST /page/add;
- PUT /page/update/{page_id};
- DELETE /page/del/{page_id}.

### 3.4 Access Management Service

- GET /access/my — страницы, к которым есть доступ у текущего пользователя;
- GET /access/granted — страницы, к которым пользователь сам дал доступ;
- GET /access/page/{page_id}/check — проверка доступа к конкретной странице;
- GET /access/page/{page_id}/full — полная информация по странице и доступу;
- POST /access/grant — выдача доступа;
- PUT /access/{access_id} — обновление доступа;
- DELETE /access/{access_id} — отзыв доступа;
- DELETE /access/hard/{access_id} — полное удаление записи доступа.

### 3.5 Media Service

- POST /media/upload — загрузка файла;
- GET /media/{media_id} — сведения о медиа;
- GET /media/ — список медиа с фильтрами;
- GET /media/temp/my — временные медиа текущего пользователя;
- POST /media/{media_id}/confirm — подтверждение и привязка временного файла к странице;
- PUT /media/{media_id} — обновление метаданных;
- DELETE /media/{media_id} — удаление медиа;
- POST /media/cleanup/temp — очистка старых временных файлов;
- GET /media/page/{page_id} — медиа конкретной страницы.

---

## 4. Структуры данных и доменные модели

Основная модель данных бекэнда сосредоточена в [database/models](database/models).

### 4.1 Пользователи и токены

Из [database/models/auth.py](database/models/auth.py):
- UserRole — роли пользователей и права;
- User — пользователь с email, username, full_name, password_hash, role_id, статусами активности и верификации;
- RefreshToken — refresh-токены, привязанные к пользователю и устройству;
- EmailVerificationToken — токены подтверждения email.

### 4.2 Агенты и страницы памяти

Из [database/models/memory.py](database/models/memory.py):
- AgentBD — агент памяти (имя, пол, даты жизни, avatar_url, is_human);
- PageBD — страница памяти (epitaph, biography, is_public, is_draft, agent_id, user_id).

Связь между ними:
- один агент имеет много страниц;
- каждая страница принадлежит пользователю и агенту.

### 4.3 Доступ к страницам

Из [database/models/access.py](database/models/access.py):
- PageAccessControl — запись о доступе к странице.

Поле описывает:
- page_id;
- user_id — кому выдан доступ;
- can_view, can_edit — права;
- granted_by — кто выдал доступ;
- expires_at — срок действия;
- is_active — активен ли доступ.

### 4.4 Медиа

Из [database/models/media.py](database/models/media.py):
- MediaBD — запись о медиафайле.

Хранит:
- user_id, page_id;
- file_extension, file_size, media_type, mime_type;
- width, height, duration;
- is_public, is_temp;
- created_at, updated_at.

---

## 5. Технологические особенности

### 5.1 Аутентификация и авторизация

- JWT используется для access/refresh токенов;
- gateway проверяет токен через свои зависимости;
- сервис Auth отвечает за генерацию и валидацию токенов;
- сервисы Memory/Access/Media используют текущий user_id из зависимостей для проверки доступа.

### 5.2 Прокси и маршрутизация

Gateway построен как прокси-слой:
- перенаправляет запросы к микросервисам;
- передаёт заголовки и user-info;
- умеет работать с multipart/form-data для загрузки файлов.

### 5.3 Работа с БД

Все сервисы используют единый слой базы данных:
- [database/engine.py](database/engine.py);
- [database/session.py](database/session.py);
- [database/base.py](database/base.py).

Это позволяет сервисам совместно работать с SQLAlchemy-моделями и общими таблицами.

---

## 6. Ключевые выводы по текущему состоянию

1. Бекэнд уже реализован как набор ориентированных на домен сервисов, а не как один монолит.
2. Gateway действительно выполняет роль единого входа, но в текущем варианте маршрутизирует в основном Auth и Memory сервисы.
3. Access Management и Media — отдельные самостоятельные сервисы, которые запускаются отдельно и не подключены к gateway через основной маршрут.
4. Система данных достаточно зрелая: есть чёткие модели для пользователей, страниц, доступа и медиа.
5. Аргумент в пользу архитектуры: каждый сервис отвечает за свою зону ответственности, что подходит для будущего масштабирования.

---

## 7. Итог

Текущая бек-часть проекта — это работающий каркас микросервисной системы с:
- FastAPI-сервисами;
- JWT-аутентификацией;
- SQLAlchemy-моделями;
- центральным API Gateway;
- отдельными модулями для памяти, доступа и медиа.

На текущем этапе проект уже имеет полноценную основу для дальнейшего развития, но для более зрелой production-архитектуры стоит дополнительно:
- подключить Access Service и Media Service в Gateway;
- унифицировать маршрутизацию и документацию;
- привести конфигурации сервисов к единому стандарту;
- усилить проверку прав доступа и обработку ошибок.
