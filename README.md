# LogFlow - Centralized Log Collection Service

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-00a60e?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/MinIO-Latest-C72C48?logo=minio)](https://min.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docs.docker.com/compose/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)

A high-performance, scalable log collection and storage service built with FastAPI, PostgreSQL, and MinIO S3-compatible object storage.

## Features

- **Batch Log Ingestion** - Efficient API for collecting logs from multiple sources
- **Structured Storage** - PostgreSQL for indexed queries and metadata
- **Object Storage** - MinIO for log artifacts and long-term retention
- **Advanced Filtering** - Query logs by level, timestamp, task ID, profile ID, and action
- **Async Operations** - Non-blocking I/O with asyncio and asyncpg
- **Database Migrations** - Alembic for versioned schema management
- **Health Checks** - Built-in endpoint for monitoring and orchestration

## Architecture

```
┌─────────────────┐
│  API Client     │
└────────┬────────┘
         │ POST /api/v1/logs/batch
         │ GET  /api/v1/runs
         │ GET  /api/v1/runs/{run_id}
         │
    ┌────▼─────────────────────────────────┐
    │  FastAPI Application (Port 8000)      │
    │  ├─ Batch Log Processing              │
    │  ├─ Run Queries & Filtering           │
    │  └─ Health Monitoring                 │
    └────┬──────────────┬───────────────────┘
         │              │
    ┌────▼──────┐  ┌───▼────────────┐
    │ PostgreSQL │  │     MinIO      │
    │ (Logs DB)  │  │  (S3 Storage)  │
    └───────────┘  └────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Using Docker Compose

1. Clone and navigate to the project:

```bash
git clone <repository-url>
cd 5-google-logflow
```

2. Create `.env` from template:

```bash
cp .env.example .env
```

3. Start all services:

```bash
docker compose up --build
```

The application will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9002 (credentials in `.env`)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/logs/batch` | Ingest batch of logs |
| `GET` | `/api/v1/runs` | List automation runs (with filtering) |
| `GET` | `/api/v1/runs/{run_id}` | Get run details |
| `GET` | `/api/v1/runs/{run_id}/logs` | Get logs for specific run |

### Example: Submit Logs

```bash
curl -X POST http://localhost:8000/api/v1/logs/batch \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "run-123",
    "task_id": "task-abc",
    "profile_id": "profile-1",
    "action_name": "create_ads",
    "logs": [
      {
        "timestamp": "2026-03-10T14:30:00Z",
        "level": "INFO",
        "message": "Campaign created successfully",
        "data": {"campaign_id": "camp-789"}
      },
      {
        "timestamp": "2026-03-10T14:30:05Z",
        "level": "ERROR",
        "message": "Failed to update budget",
        "data": {"error": "Insufficient funds", "status": 402}
      }
    ]
  }'
```

Response:
```json
{
  "status": "ok",
  "received_logs": 2
}
```

### Example: Query Runs

```bash
# List all runs for a task
curl "http://localhost:8000/api/v1/runs?task_id=task-abc&limit=20"

# Get specific run
curl "http://localhost:8000/api/v1/runs/run-123"

# Get run logs with filtering
curl "http://localhost:8000/api/v1/runs/run-123/logs?level=ERROR&limit=50"
```

## Configuration

Environment variables in `.env`:

```env
# Application
APP_PORT=8000

# PostgreSQL
POSTGRES_DB=logs
POSTGRES_USER=logs
POSTGRES_PASSWORD=logs
POSTGRES_PORT=5432

# MinIO S3
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=minio12345
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9002
MINIO_BROWSER_REDIRECT_URL=
```

## Database Schema

### Tables

**automation_runs**
```sql
CREATE TABLE automation_runs (
  run_id VARCHAR(255) PRIMARY KEY,
  task_id VARCHAR(255) NOT NULL,
  profile_id VARCHAR(255),
  action_name VARCHAR(100) NOT NULL,
  status VARCHAR(20) DEFAULT 'running',
  task_data JSONB,
  start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**logs**
```sql
CREATE TABLE logs (
  log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  run_id VARCHAR(255) NOT NULL REFERENCES automation_runs(run_id) ON DELETE CASCADE,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  level VARCHAR(20) NOT NULL,
  message TEXT,
  data JSONB NOT NULL
);
```

## Project Structure

```
5-google-logflow/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── logs.py         # Log ingestion endpoint
│   │   │   └── runs.py         # Run query endpoints
│   │   └── deps.py             # Dependency injection
│   ├── core/
│   │   ├── config.py           # Settings (Pydantic)
│   │   └── logging_config.py   # Loguru configuration
│   ├── db/
│   │   ├── base.py             # SQLAlchemy base
│   │   └── session.py          # Database session
│   ├── models/
│   │   ├── log.py              # Log ORM model
│   │   └── automation_run.py   # AutomationRun ORM model
│   ├── schemas/
│   │   ├── batch.py            # BatchRequest schema
│   │   ├── log.py              # Log request schema
│   │   ├── log_read.py         # Log response schema
│   │   ├── automation_run.py   # AutomationRun schemas
│   │   └── enums.py            # LogLevel enum
│   ├── services/
│   │   ├── db_logging.py       # Batch processing logic
│   │   └── minio_service.py    # S3 storage service
│   └── main.py                 # FastAPI app initialization
├── alembic/
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic configuration
├── docker-compose.yml          # Service orchestration
├── Dockerfile                  # Application container
├── start.sh                    # Container entrypoint
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Development

### Local Setup

1. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure `.env` for local services:

```env
DB_HOST=localhost
MINIO_ENDPOINT_HOST=localhost
```

3. Run migrations:

```bash
alembic upgrade head
```

4. Start development server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database Migrations

Create new migration:
```bash
docker compose run --rm app alembic revision -m "Add new column"
```

Apply migrations:
```bash
docker compose run --rm app alembic upgrade head
```

View migration history:
```bash
docker compose run --rm app alembic history
```

### Viewing Logs

```bash
docker compose logs --tail=200 -f app
```

## Tech Stack

- **Framework**: FastAPI 0.110+
- **ASGI Server**: Uvicorn 0.23+ / Gunicorn 21.2+
- **Database**: PostgreSQL 16 + SQLAlchemy 2.0 + asyncpg
- **Migrations**: Alembic 1.12+
- **Object Storage**: MinIO 7.2+ (S3-compatible)
- **Validation**: Pydantic 2.6+
- **Logging**: Loguru 0.7+
- **Configuration**: Pydantic Settings 2.2+

## License

Proprietary
