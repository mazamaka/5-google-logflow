# LogFlow — сервис сбора логов

Стек: FastAPI, SQLAlchemy (async), PostgreSQL, Alembic, MinIO, Docker Compose. Python 3.12.

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и при необходимости измените значения.
2. Запустите:

```bash
docker compose up --build
```

Сервис поднимется на `http://localhost:${APP_PORT}`. Документация Swagger: `http://localhost:${APP_PORT}/docs`.

MinIO консоль: `http://localhost:${MINIO_CONSOLE_PORT}` (логин/пароль из `.env`).

### Конфигурация портов

Все хостовые порты настраиваются в `.env` и используются в `docker-compose.yml`:

- `APP_PORT` (по умолчанию 8000) — внешний порт API
- `POSTGRES_PORT` (по умолчанию 5432) — внешний порт PostgreSQL
- `MINIO_API_PORT` (по умолчанию 9000) — внешний порт MinIO API (S3 endpoint)
- `MINIO_CONSOLE_PORT` (по умолчанию 9002) — внешний порт MinIO Console

Пример доступа:

- API: `http://localhost:${APP_PORT}`
- MinIO API (S3): `http://localhost:${MINIO_API_PORT}`
- MinIO Console: `http://localhost:${MINIO_CONSOLE_PORT}`

## Структура

- `app/` — приложение FastAPI, модели, схемы, БД, сервисы
- `alembic/` — миграции Alembic
- `start.sh` — старт сервиса в Docker (ожидание БД, миграции, Gunicorn)

## Миграции

Создать новую миграцию:

```bash
docker compose run --rm app alembic revision -m "message"
```

Применить миграции вручную:

```bash
docker compose run --rm app alembic upgrade head
```

## Локальный запуск (без Docker)

1) Установите зависимости:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Скопируйте `.env.example` в `.env` и укажите подключения к сервисам, которые запущены докером локально:

```env
DB_HOST=localhost
MINIO_ENDPOINT=localhost:${MINIO_API_PORT}
```

3) Примените миграции вручную:

```bash
alembic upgrade head
```

4) Запустите приложение руками (пример):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

start.sh используется только в Docker-контейнере.

## API (этап 1)

- `POST /api/v1/logs/batch` — принимает пачку логов для одного запуска. На этапе 1 сохраняет данные в лог контейнера и возвращает `{ "status": "ok", "received_logs": N }`.

Пример запроса:

```bash
curl -X POST http://localhost:8000/api/v1/logs/batch \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "run-123",
    "task_id": "task-xyz",
    "profile_id": "p-1",
    "action_name": "create_ads",
    "logs": [
      {"timestamp": "2025-09-23T14:30:00Z", "level": "INFO", "message": "step 1", "data": {"k": 1}},
      {"timestamp": "2025-09-23T14:30:05Z", "level": "ERROR", "message": "step 2 failed", "data": {"err": "boom"}}
    ]
  }'
```

Посмотреть логи приложения:

```bash
docker compose logs --tail=200 app
```

