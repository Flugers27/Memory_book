# Auth Service

## Назначение

Сервис Auth отвечает за аутентификацию и управление пользователями. Он предоставляет REST API для:

- регистрации новых пользователей;
- входа в систему (JWT access + refresh токены);
- обновления access-токена по refresh-токену;
- выхода из системы (отзыв refresh-токенов);
- подтверждения email через JWT-токен;
- сброса и восстановления пароля;
- получения и обновления профиля пользователя;
- смены пароля и email;
- удаления (деактивации) аккаунта;
- просмотра и отзыва активных refresh-токенов;
- валидации JWT-токена (для внутреннего использования другими сервисами).

## Основные модули

- `main.py` — точка входа FastAPI-приложения.
- `config.py` — конфигурация сервиса (порт, JWT-ключи, сроки токенов, CORS).
- `auth_logic.py` — создание и верификация JWT-токенов (access, refresh, verification, password-reset), хеширование паролей (Argon2), аутентификация пользователя.
- `crud.py` — операции с пользователями в БД (создание, обновление пароля, удаление, активация, верификация email).
- `dependencies.py` — FastAPI-зависимости: получение текущего пользователя (`get_current_user`), активного пользователя (`get_current_active_user`), администратора (`get_current_admin_user`).
- `schemas.py` — Pydantic-схемы запросов и ответов.
- `utils.py` — вспомогательные функции (отправка email для верификации).
- `routers/auth.py` — маршруты аутентификации (регистрация, вход, refresh, logout, verify-email, password-reset, validate).
- `routers/users.py` — маршруты управления профилем (GET/PUT /me, смена пароля/email, удаление аккаунта, управление токенами).
- `routers/health.py` — health-check.

## Роуты

### Аутентификация (`/auth`)

- `POST /auth/register` — регистрация нового пользователя.
- `POST /auth/login` — вход в систему (OAuth2 password flow), возвращает access + refresh токены.
- `POST /auth/refresh` — обновление access-токена по refresh-токену.
- `POST /auth/logout` — выход из системы (отзыв refresh-токена).
- `GET /auth/verify-email` — подтверждение email по JWT-токену.
- `POST /auth/password-reset/request` — запрос сброса пароля (в dev-режиме возвращает токен).
- `POST /auth/password-reset/confirm` — подтверждение сброса пароля и установка нового.
- `POST /auth/validate` — валидация access-токена (для внутреннего использования).

### Пользователи (`/users`)

- `GET /users/me` — информация о текущем пользователе.
- `PUT /users/me` — обновление профиля (email, username, full_name).
- `PUT /users/me/password` — смена пароля.
- `PUT /users/me/email` — смена email.
- `DELETE /users/me` — деактивация аккаунта.
- `GET /users/me/tokens` — список активных refresh-токенов.
- `POST /users/me/tokens/revoke-all` — отзыв всех refresh-токенов.

### Health

- `GET /health` — проверка состояния сервиса.

## Авторизация

Сервис использует JWT (access + refresh). Access-токен передаётся в заголовке `Authorization: Bearer <token>`. Refresh-токен используется для получения новой пары токенов. Пароли хешируются алгоритмом Argon2. Для защищённых маршрутов используются зависимости `get_current_user` / `get_current_active_user` / `get_current_admin_user`, которые декодируют JWT и извлекают пользователя из БД.

## Запуск

Из корня проекта:

```bash
cd services/Auth
python run.py
```

Или через FastAPI/uvicorn:

```bash
python -m uvicorn services.Auth.main:app --reload
```

## Примечания

- Все маршруты, кроме `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/password-reset/*`, `/auth/validate` и `/health`, требуют авторизации (JWT-токен в заголовке `Authorization: Bearer <token>`).
- Refresh-токены хранятся в БД (таблица `refresh_tokens`) с привязкой к устройству и IP-адресу.
- Верификация email в текущей реализации закомментирована (токен создаётся, но письмо не отправляется).
- Для локального развёртывания важно, чтобы переменные окружения (`SECRET_KEY`, `DATABASE_URL`, `AUTH_PORT`) были правильно заданы.
- Сервис работает на порту **8001** по умолчанию.