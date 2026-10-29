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

Примечание: для локального запуска фронтенда запустите backend на `localhost:8080` и выполните `npm start` в `frontend/`. Dev-сервер CRA проксирует запросы к API на `http://localhost:8080` (поле `proxy` в `frontend/package.json`). Переменные окружения не нужны.

## Миграции
Миграции выполняются с помощью Alembic. Для ручного применения:

alembic -c backend/storage/alembic.ini upgrade head

Upgrade копирует строки старых заказов в таблицы Workplace, если в `"order"` есть строки, а таблицы Workplace пустые. Если в таблицах Workplace уже есть строки, upgrade останавливается и старые таблицы не меняет.

## AI-агенты
Настройка AI-агентов и структура `.agents/`: [.agents/docs/onboarding.md](.agents/docs/onboarding.md).
