# Deployment Guide

Unified Communication Platform — modular monolith (FastAPI) + Celery workers + Next.js
frontend, backed by Neon Postgres and Redis.

## Architecture at a glance

```
                    ┌────────────┐     ┌─────────────┐
  Channels ───────▶ │  FastAPI   │ ──▶ │   Redis     │ ◀── Celery workers
 (WhatsApp/Email/   │  (API+WS)  │     │ (queue+pub) │     (msg, ai, docs)
  Web Chat)         └─────┬──────┘     └─────────────┘
                          │                   │
                          ▼                   ▼
                    ┌──────────────────────────────┐
                    │   Neon Postgres (+ pgvector)  │  RLS multi-tenant
                    └──────────────────────────────┘
        Next.js frontend ──▶ FastAPI (HTTP + WebSocket, cookie auth)
```

## Environments

| Env | DB | Notes |
|-----|----|-------|
| development | Neon (or local) | `DEBUG=true`, `SESSION_COOKIE_SECURE=false` |
| staging | Neon branch | mirror of prod, separate secrets |
| production | Neon | `DEBUG=false`, `SESSION_COOKIE_SECURE=true`, real secrets |

Each environment gets its own `.env` (never committed). Only `DATABASE_URL` is
required for the DB (the sync URL for Alembic is auto-derived).

## Required environment variables

See `.env.example`. Minimum for prod:
- `ENVIRONMENT=production`, `DEBUG=false`
- `SECRET_KEY` (long random; rotating invalidates sessions + channel credentials)
- `DATABASE_URL` (asyncpg, `?ssl=require`)
- `REDIS_URL`
- `OPENAI_API_KEY`
- `FRONTEND_ORIGIN` (exact https origin — used by CORS + CSRF)
- `SESSION_COOKIE_SECURE=true`
- Channel secrets as needed (`WHATSAPP_*`, SMTP/SendGrid)
- Optional: `SENTRY_DSN`, `OTEL_EXPORTER_ENDPOINT`

## Build & run (Docker)

```bash
# Backend image (also used by the worker)
docker build -t ucaas-backend:latest ./backend
# Frontend production image
docker build -f frontend/Dockerfile.prod -t ucaas-frontend:latest ./frontend

# Or the whole local stack:
docker-compose up --build
```

## Database migrations (zero-downtime)

Migrations are additive (no destructive column drops in the same release as code that
needs them). Apply before/with rollout:

```bash
docker-compose run --rm backend uv run alembic upgrade head
# rollback one step if needed:
docker-compose run --rm backend uv run alembic downgrade -1
```

pgvector must be enabled once per database: `CREATE EXTENSION IF NOT EXISTS vector;`
(migration `0003` attempts this automatically).

## Processes to run in production

| Process | Command |
|---------|---------|
| API + WebSocket | `uv run uvicorn src.main:app --host 0.0.0.0 --port 8000` |
| Worker (all queues) | `uv run celery -A src.celery_app.celery_app worker -Q messages,webhooks,ai,email,default` |
| Beat (scheduled) | `uv run celery -A src.celery_app.celery_app beat` |
| Flower (monitoring) | `uv run celery -A src.celery_app.celery_app flower` |

Scale workers horizontally per queue (e.g., dedicated `ai` workers). The API and
workers are stateless — all shared state is in Postgres/Redis.

## Scaling notes

- **WebSocket**: each instance keeps only local connections; events fan out via Redis
  pub/sub, so you can run N API instances behind a sticky-or-not load balancer.
- **Workers**: add replicas; queues isolate workloads (`ai` is the heaviest).
- **DB**: Neon autoscales; use the pooled endpoint (asyncpg `statement_cache_size=0`
  already configured for PgBouncer compatibility).

## CI/CD

`.github/workflows/ci.yml` runs on push/PR: backend lint + import + migrations (against
a pgvector Postgres service) + tests; frontend lint + build. Extend with a deploy job
targeting your platform (Fly.io / Render / ECS / Kubernetes).

---

## Google Cloud Run — Production Deployment

### One-time Setup (already done)

| Resource | Name |
|----------|------|
| GCP Project | `cpaas-500610` |
| Artifact Registry | `asia-south1-docker.pkg.dev/cpaas-500610/ucaas-backend/api` |
| Cloud Run API service | `ucaas-api` (region: `asia-south1`) |
| Cloud Run Worker service | `ucaas-worker` (region: `asia-south1`) |
| Secret Manager secrets | `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `GEMINI_API_KEY` |

### Local vs Cloud — Same Architecture, Alag Tools

Locally `docker-compose up` chal raha tha jisme 4 containers the:
`redis`, `backend` (API), `worker` (Celery), `frontend` — sab ek saath.

Cloud pe wahi cheez alag Cloud Run services ke roop mein hai:
- `ucaas-api` = local ka `backend` container
- `ucaas-worker` = local ka `worker` container
- Redis = Upstash (already cloud pe tha)

**Dono same Docker image use karte hain** — sirf start command alag hai:
- API command: `uvicorn src.main:app` (HTTP server)
- Worker command: `celery worker` (background queue processor)

### Backend Code Update karne ke baad — Redeploy Steps

Image ek hai isliye **dono services ko** naya image dena padta hai.
Steps hamesha yahi rahenge — sirf 3 commands:

```bash
# Step 1 — Naya Docker image build karo (backend folder se)
docker build -t asia-south1-docker.pkg.dev/cpaas-500610/ucaas-backend/api:latest ./backend

# Step 2 — Image cloud pe push karo
docker push asia-south1-docker.pkg.dev/cpaas-500610/ucaas-backend/api:latest

# Step 3 — Dono services ko naya image do
gcloud run deploy ucaas-api \
  --image="asia-south1-docker.pkg.dev/cpaas-500610/ucaas-backend/api:latest" \
  --region=asia-south1 \
  --project=cpaas-500610

gcloud run deploy ucaas-worker \
  --image="asia-south1-docker.pkg.dev/cpaas-500610/ucaas-backend/api:latest" \
  --region=asia-south1 \
  --project=cpaas-500610
```

> **Note (important):** Step 3 mein sirf `--image` flag dena kaafi hai.
> Baaki settings (secrets, env vars, memory, CPU) Cloud Run mein pehle se
> save hain — woh automatically reuse hoti hain, dobara likhne ki zaroorat nahi.

### Database Migration (agar schema change ho)

```bash
# Cloud Run job se migration run karo
gcloud run jobs create ucaas-migrate \
  --image="asia-south1-docker.pkg.dev/cpaas-500610/ucaas-backend/api:latest" \
  --region=asia-south1 \
  --project=cpaas-500610 \
  --set-secrets="DATABASE_URL=DATABASE_URL:latest" \
  --command="uv" \
  --args="run,alembic,upgrade,head"

gcloud run jobs execute ucaas-migrate --region=asia-south1 --project=cpaas-500610 --wait
```

### Secret Update karna (e.g., naya API key)

```bash
# Naya version add karo — Cloud Run automatically latest use karta hai
echo -n "NEW_VALUE_HERE" | gcloud secrets versions add SECRET_NAME \
  --data-file=- \
  --project=cpaas-500610

# Phir service redeploy karo taake naya secret load ho
gcloud run deploy ucaas-api \
  --image="asia-south1-docker.pkg.dev/cpaas-500610/ucaas-backend/api:latest" \
  --region=asia-south1 \
  --project=cpaas-500610
```

### Logs Dekhna

```bash
# Live logs stream karo
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=ucaas-api" \
  --project=cpaas-500610

# Worker logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=ucaas-worker" \
  --project=cpaas-500610

# Last 50 error lines
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50 --project=cpaas-500610
```

### Service URLs

| Service | URL |
|---------|-----|
| Backend API | `https://ucaas-api-919679113744.asia-south1.run.app` |
| API Docs (Swagger) | `https://ucaas-api-919679113744.asia-south1.run.app/docs` |
| Health Check | `https://ucaas-api-919679113744.asia-south1.run.app/health` |
| Celery Worker | `https://ucaas-worker-919679113744.asia-south1.run.app` (internal only) |

### Worker kya hai aur kyun alag hai?

**Celery Worker** ek background job processor hai. API ke saath deploy nahi hota kyunke:
- API: HTTP requests handle karta hai (fast, stateless)
- Worker: heavy/slow kaam karta hai background mein (email sync, AI document processing,
  WhatsApp webhook processing, knowledge base embedding)

Dono same Docker image use karte hain, lekin **alag commands** se start hote hain:

```
API Command:    uvicorn src.main:app --host 0.0.0.0 --port 8000
Worker Command: celery -A src.celery_app.celery_app worker --loglevel=info
```

Worker ke bina ye features kaam nahi karenge:
- Email channel sync (IMAP)
- WhatsApp incoming messages
- AI Knowledge Base document upload/processing
- Message retry on failure
