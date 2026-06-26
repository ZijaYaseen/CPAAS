---
id: 006
title: MVP Hardening + uv migration + live DB
stage: green
date: 2026-06-22
surface: agent
model: claude-opus-4-8
feature: 001-unified-comms-platform
branch: 001-unified-comms-platform
user: ZijaYaseen
command: /sp.implement
labels: ["mvp", "hardening", "security", "observability", "uv", "alembic", "neon", "audit"]
links:
  spec: specs/001-unified-comms-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/modules/audit/* (models, service, router)
 - backend/alembic/versions/0004_audit_and_indexes.py
 - backend/src/core/ratelimit.py
 - backend/src/core/validation.py
 - backend/src/core/middleware.py (CSRF)
 - backend/src/core/sentry.py
 - backend/src/core/telemetry.py
 - backend/src/core/cache.py
 - backend/src/core/database.py (slow-query logging, pooler connect_args)
 - backend/src/core/config.py (single DATABASE_URL + derived sync property, env_file root path, security/obs knobs)
 - backend/pyproject.toml (uv project: deps + dev group), uv.lock
 - backend/Dockerfile (uv), frontend/Dockerfile.prod, docker-compose.yml (uv run + .venv volume)
 - .github/workflows/ci.yml
 - docs/deployment.md, docs/production-checklist.md
 - .env / .env.example (single async URL, ssl=require, secrets only in .env)
tests:
 - "ruff check src — PASS (0 errors)"
 - "uv run python -c import src.main — 34 routes OK"
 - "alembic upgrade head on Neon — 19 tables + pgvector, version 0004"
 - "auth smoke test on live Neon (register/login/normalize/reject) — PASS (rolled back)"
---

## Prompt

Multi-turn continuation of /sp.implement. User asked to: do Phase 11 (hardening) as part
of MVP; switch the backend to **uv** (isolated .venv, `uv add`); remove DATABASE_URL_SYNC
(auto-derive); keep Docker working; explain EmailStr/email-validator; then continue and
run migrations. (User confirmed Post-MVP is NOT to be started yet.)

## Response snapshot

**Phase 11 Hardening (T267–T285, T289):** audit_logs table + audit service + admin viewer +
wired audit on login/register/kill-switch; migration 0004 (audit + composite perf indexes);
Redis fixed-window rate limiting middleware; input sanitization helper; Origin-based CSRF for
authenticated mutating requests; Sentry (config-gated) + OpenTelemetry (config-gated, optional
import); slow-query logging; Redis cache helpers; frontend prod Dockerfile (standalone);
GitHub Actions CI (backend lint+import+migrate+test against pgvector service; frontend build);
deployment.md + production-checklist.md. T286/T287/T288 left as manual/runtime.

**Tooling/config fixes (user-driven):**
- Switched backend to a **uv project** — deps moved into pyproject `[project].dependencies`,
  isolated `.venv`, `uv.lock`; removed requirements.txt; Dockerfile + compose now use `uv` /
  `uv run` (+ `/app/.venv` anon volume so host venv doesn't shadow container). Resolved
  openai/openai-agents version conflict (openai>=1.87).
- **Removed `DATABASE_URL_SYNC` env var** → derived `database_url_sync` property from the async
  URL (asyncpg→psycopg, ssl→sslmode). Fixed `env_file` to read the repo-root `.env` (was
  reading defaults). asyncpg `ssl=require` (not sslmode) + Neon pooler `statement_cache_size=0`.
- **Security**: real creds only in gitignored `.env`; `.env.example` placeholders.
- Added `email-validator` via `uv add`; **email lowercase-normalization** in auth + contacts.

**Live validation:** ruff clean; app imports (34 routes); **migrations applied to Neon**
(19 tables, pgvector, v0004); **auth smoke test on live Neon passed** (rolled back, no residue).

## Outcome

- ✅ Impact: MVP code 100% complete (Phases 1–4 + Hardening) and validated against live Neon.
- 🧪 Tests: ruff PASS; import OK; migrations applied; auth flow verified live.
- 📁 Files: ~15 new/changed (audit, security, observability, deploy, uv config).
- 🔁 Next prompts: P-5 OPENAI_API_KEY + P-6 full smoke (Redis+server+channel+AI). Post-MVP deferred.
- 🧠 Reflection: Post-MVP (Phases 5–10) intentionally untouched per user.

## Evaluation notes (flywheel)

- Failure modes observed: env_file not read from root (defaults loaded) → fixed with absolute path; openai version conflict → loosened pin.
- Graders run and results (PASS/FAIL): ruff PASS, alembic PASS, auth smoke PASS.
- Prompt variant (if applicable): n/a
- Next experiment: start Redis + server, post a webchat message with a KB doc + OpenAI key, verify AI reply + run log.
