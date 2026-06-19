# PrintingHouse

Проект "PrintingHouse" — веб-приложение для расчёта и управления печатными заказами (backend на Python/FastAPI, frontend на React, PostgreSQL).

## Быстрый старт (Docker)
Требуется: Docker и Docker Compose.

1. Создайте файл `.env` в корне проекта (см. раздел "Переменные окружения").
2. Собрать и запустить контейнеры:

   docker-compose up --build

3. Backend будет доступен на порту 8080, frontend — на порту 80, PostgreSQL — на хост-порту 9742.

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
BACKEND_URL=http://ph_backend:8080

Примечание: для локального запуска фронтенда установите REACT_APP_BACKEND_URL, например `http://localhost:8080`.

## Миграции
Миграции выполняются с помощью Alembic. Для ручного применения:

alembic -c backend/storage/alembic.ini upgrade head
