# PrintingHouse

Проект "PrintingHouse" — веб-приложение для расчёта и управления печатными заказами (backend на Python/FastAPI, frontend на React, PostgreSQL).

## Быстрый старт (Docker)
Требуется: Docker и Docker Compose.

1. Создайте файл `.env` в корне проекта (см. раздел "Переменные окружения").
2. Собрать и запустить контейнеры:

   docker-compose up --build

3. Frontend будет доступен на порту 80. Он обращается к backend через nginx внутри контейнера `ph_ui`: запросы на `/api/` и `/auth/` проксируются на `ph_backend:8080`. Порт 8080 остаётся открытым для прямого доступа к backend и Swagger (`http://<host>:8080/docs`). PostgreSQL — на хост-порту 9742.

> Docker-compose уже выполняет миграции Alembic перед запуском backend.

## Переменные окружения
Пример значений в файле `.env`:

SERVER_PORT=8080
SERVER_HOST=0.0.0.0
DB_USER=ph_user
DB_PASSWORD=ph_password
DB_HOST=ph_db
DB_PORT=5432
DB_NAME=ph_db
JWT_SECRET_KEY=change-this-in-real-env
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-in-real-env

Обязательные `JWT_SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` нужны, когда таблица `users` пуста: при старте создаётся один пользователь. Пустой или отсутствующий `JWT_SECRET_KEY`, а также пустые `ADMIN_USERNAME` / `ADMIN_PASSWORD` при пустой таблице `users` не дают процессу поднять HTTP-сервер.

Примечание: для локального запуска фронтенда запустите backend на `localhost:8080` и выполните `npm start` в `frontend/`. Dev-сервер CRA проксирует запросы к API на `http://localhost:8080` (поле `proxy` в `frontend/package.json`). Переменные окружения не нужны.

## Миграции
Миграции выполняются с помощью Alembic. Для ручного применения:

alembic -c backend/storage/alembic.ini upgrade head

Команда создаёт схему хранения для `new_core`: каталоги оборудования и операторов, заказы, тиражи, справочные материалы. Подключение к PostgreSQL берётся из переменных окружения `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` (см. раздел «Переменные окружения»).

После `upgrade head` таблицы пустые: строк в каталогах и заказах нет. Миграция не переносит данные из удалённой схемы Workplace и не копирует старые заказы.

## AI-агенты
Настройка AI-агентов и структура `.agents/`: [.agents/docs/onboarding.md](.agents/docs/onboarding.md).
