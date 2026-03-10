# LogFlow

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/MinIO-S3--Compatible-C72C48?logo=minio&logoColor=white)](https://min.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](#license)

Centralized log collection and storage service for automation pipelines. Collects structured logs via REST API, stores metadata in PostgreSQL and artifacts in MinIO (S3-compatible object storage).

## Architecture

```
                      ┌──────────────────┐
                      │   API Clients    │
                      │ (automation bots)│
                      └────────┬─────────┘
                               │
                    POST /api/v1/logs/batch
                    GET  /api/v1/runs
                    GET  /api/v1/runs/{id}/logs
                               │
                ┌──────────────▼──────────────┐
                │    FastAPI + Gunicorn        │
                │    (async, multi-worker)     │
                │                              │
                │  ┌─────────┐  ┌───────────┐ │
                │  │ Log API │  │ Runs API  │ │
                │  └────┬────┘  └─────┬─────┘ │
                │       │             │        │
                │  ┌────▼─────────────▼─────┐  │
                │  │   SQLAlchemy (async)    │  │
                │  └────┬───────────────────┘  │
                └───────┼──────────────────────┘
                        │
              ┌─────────┼─────────┐
              │                   │
        ┌─────▼──────┐    ┌──────▼───────┐
        │ PostgreSQL  │    │    MinIO     │
        │  (metadata) │    │ (artifacts)  │
        └────────────┘    └──────────────┘
```

## Features

- **Batch log ingestion** -- single endpoint accepts multiple log entries per request
- **Run tracking** -- automatic upsert of automation runs with status and metadata
- **Advanced filtering** -- query runs and logs by level, timestamp, task ID, profile, action
- **Async I/O** -- non-blocking database operations via asyncpg + SQLAlchemy 2.0
- **S3 storage** -- MinIO integration for log artifacts and long-term retention
- **Auto-migrations** -- Alembic runs on container startup
- **Multi-worker** -- Gunicorn with configurable worker count (auto-calculated from CPU)
- **Health check** -- built-in `/health` endpoint for orchestration

## Quick Start

### Prerequisites

- Docker and Docker Compose

### Run with Docker Compose

```bash
# Clone the repository
git clone https://github.com/mazamaka/5-google-logflow.git
cd 5-google-logflow

# Create .env from template
cp .env.example .env

# Start all services
docker compose up --build -d
```

Services will be available at:

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| MinIO Console | http://localhost:9002 |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/logs/batch` | Ingest a batch of log entries |
| `GET` | `/api/v1/runs` | List automation runs (filterable) |
| `GET` | `/api/v1/runs/{run_id}` | Get single run details |
| `GET` | `/api/v1/runs/{run_id}/logs` | Get logs for a specific run |

### Ingest Logs

```bash
curl -X POST http://localhost:8000/api/v1/logs/batch \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "run-001",
    "task_id": "task-abc",
    "profile_id": "profile-1",
    "action_name": "create_campaign",
    "task_data": {"campaign_type": "search"},
    "logs": [
      {
        "timestamp": "2025-10-01T12:00:00Z",
        "level": "INFO",
        "message": "Campaign created",
        "data": {"campaign_id": "camp-789"}
      },
      {
        "timestamp": "2025-10-01T12:00:05Z",
        "level": "ERROR",
        "message": "Budget update failed",
        "data": {"error": "Insufficient funds"}
      }
    ]
  }'
```

**Response:**
```json
{"status": "ok", "received_logs": 2}
```

### Query Runs

```bash
# List runs filtered by task
curl "http://localhost:8000/api/v1/runs?task_id=task-abc&limit=20"

# Get specific run
curl "http://localhost:8000/api/v1/runs/run-001"

# Get run logs filtered by level
curl "http://localhost:8000/api/v1/runs/run-001/logs?level=ERROR&limit=50"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `logflow` | Application name |
| `APP_PORT` | `8000` | Host port mapping |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `WORKERS` | `0` | Gunicorn workers (0 = auto: 2*CPU+1) |
| `POSTGRES_USER` | `logs` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `logs` | PostgreSQL password |
| `POSTGRES_DB` | `logs` | PostgreSQL database name |
| `POSTGRES_HOST` | `db` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port (host-side) |
| `MINIO_ENDPOINT_HOST` | `minio` | MinIO host |
| `MINIO_ENDPOINT_PORT` | `9000` | MinIO API port |
| `MINIO_ACCESS_KEY` | `minio` | MinIO access key |
| `MINIO_SECRET_KEY` | `minio12345` | MinIO secret key |
| `MINIO_SECURE` | `false` | Use HTTPS for MinIO |
| `MINIO_BUCKET` | `logs` | MinIO bucket name |
| `MINIO_API_PORT` | `9000` | MinIO API host port |
| `MINIO_CONSOLE_PORT` | `9002` | MinIO Console host port |

## Project Structure

```
logflow/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── logs.py              # POST /logs/batch
│   │   │   └── runs.py              # GET /runs, /runs/{id}, /runs/{id}/logs
│   │   └── deps.py                  # FastAPI dependencies
│   ├── core/
│   │   ├── config.py                # Pydantic Settings
│   │   └── logging_config.py        # Loguru setup
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy DeclarativeBase
│   │   └── session.py               # Async engine & session
│   ├── models/
│   │   ├── automation_run.py        # AutomationRun ORM model
│   │   └── log.py                   # Log ORM model
│   ├── schemas/
│   │   ├── automation_run.py        # AutomationRunRead schema
│   │   ├── batch.py                 # BatchRequest + LogEntry
│   │   ├── enums.py                 # LogLevel enum
│   │   └── log_read.py              # LogRead response schema
│   ├── services/
│   │   ├── db_logging.py            # Batch processing & upsert logic
│   │   └── minio_service.py         # MinIO client wrapper
│   └── main.py                      # FastAPI app with lifespan
├── alembic/                         # Database migrations
├── docker-compose.yml
├── Dockerfile
├── start.sh                         # Container entrypoint
├── requirements.txt
└── .env.example
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.110+ |
| ASGI/WSGI | Uvicorn + Gunicorn |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 (async) |
| Driver | asyncpg |
| Migrations | Alembic |
| Object Storage | MinIO (S3-compatible) |
| Validation | Pydantic 2.6+ |
| Settings | pydantic-settings |
| Logging | Loguru |
| Runtime | Python 3.12, Docker |

## Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure for local development
# Edit .env: POSTGRES_HOST=localhost, MINIO_ENDPOINT_HOST=localhost

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## License

Proprietary.

## Author

**Maksym Babenko**

- GitHub: [@mazamaka](https://github.com/mazamaka)
- Telegram: [@Mazamaka](https://t.me/Mazamaka)
