# Unified Communication Platform (AI UCaaS)

A multi-tenant SaaS that unifies WhatsApp, Email, and Web Chat (MVP) into a single
AI-powered inbox, with CRM, ticketing, broadcasts, voice, and analytics planned
post-MVP. Built as a **modular monolith** (FastAPI) + **worker services** (Celery)
with a **Next.js** frontend.

> **Status:** MVP in progress. See `specs/001-unified-comms-platform/tasks.md` for the
> live task checklist and `plan.md` for architecture.

## Tech Stack

| Layer       | Tech                                                        |
|-------------|-------------------------------------------------------------|
| Backend     | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2  |
| Frontend    | Next.js 16 (App Router), TypeScript, Tailwind, shadcn/ui    |
| Database    | PostgreSQL (Neon) + Row-Level Security for tenant isolation |
| Cache/Queue | Redis 7 (cache + Celery broker + WebSocket pub/sub)         |
| Workers     | Celery                                                      |
| AI          | OpenAI Agents SDK (read-only tools in MVP)                  |

## Architecture (why post-MVP stays easy)

Every business capability is its own module folder under `backend/src/modules/`
(`auth`, `inbox`, `channels`, `contacts`, `tickets`, `campaigns`, `ai`, `knowledge`,
`analytics`, `voice`). MVP only fills in `auth`, `inbox`, `channels`, `ai`,
`knowledge`, and basic `contacts`. Post-MVP features are added by filling in the
remaining folders — **no restructuring required**.

## Quickstart

1. **Prerequisites:** Docker + Docker Compose, a [Neon](https://neon.tech) Postgres database.
2. Copy env and fill in your Neon `DATABASE_URL` (only one URL needed — the sync URL
   for migrations is auto-derived). Use the **asyncpg** driver with `ssl=require`:
   ```bash
   cp .env.example .env
   # edit .env -> DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST/DB?ssl=require
   ```
3. Start the stack:
   ```bash
   docker-compose up --build
   ```
4. Run database migrations (first time):
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
5. Open:
   - Frontend: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - Health:   http://localhost:8000/health

## Repository Layout

```
backend/    FastAPI modular monolith + Celery workers + Alembic migrations
frontend/   Next.js App Router app
specs/      Spec-Driven Development artifacts (spec, plan, tasks, contracts)
history/    Prompt History Records (PHR) and ADRs
```

## Development without Docker

Backend uses [uv](https://docs.astral.sh/uv/) for dependency management (creates an
isolated `.venv`, no global conflicts):

```bash
# Backend
cd backend
uv sync                      # creates .venv + installs from uv.lock
uv run alembic upgrade head  # run migrations
uv run uvicorn src.main:app --reload
# add a package later: uv add <package>

# Frontend
cd frontend
npm install
npm run dev
```
