# Production Readiness Checklist

Work through this before exposing the platform to real customers.

## Secrets & config
- [ ] `ENVIRONMENT=production`, `DEBUG=false`
- [ ] `SECRET_KEY` is long, random, and stored in a secret manager (not `.env` in the image)
- [ ] `SESSION_COOKIE_SECURE=true` (HTTPS only) and app served over HTTPS
- [ ] `FRONTEND_ORIGIN` set to the exact production origin (CORS + CSRF depend on it)
- [ ] No secrets committed to git (`.env` gitignored; `.env.example` has placeholders only)
- [ ] Channel credentials rotated from any test values

## Database
- [ ] Migrations applied (`alembic upgrade head`)
- [ ] `pgvector` extension enabled
- [ ] **RLS hardening**: create a non-owner DB role for the app and `FORCE ROW LEVEL
      SECURITY` on tenant tables (MVP runs as owner → RLS advisory; service layer also
      filters by tenant). See [P-7] in tasks.md.
- [ ] Backups / PITR enabled on Neon
- [ ] Connection pool sized for instance count (pooled endpoint)

## Security
- [ ] Rate limiting enabled (`RATE_LIMIT_ENABLED=true`) and tuned per plan
- [ ] CSRF protection enabled (`CSRF_PROTECTION_ENABLED=true`)
- [ ] Webhook signature verification configured (`WHATSAPP_APP_SECRET`, etc.)
- [ ] Input sanitization applied to any rendered-as-HTML fields
- [ ] Dependency scan clean (`uv run pip-audit` / GitHub Dependabot)
- [ ] AI restricted to read-only tools (verify `BLOCKED_WRITE_TOOLS` enforcement)

## Observability
- [ ] `SENTRY_DSN` set; errors flowing with environment tag
- [ ] (Optional) `OTEL_EXPORTER_ENDPOINT` set + OTel packages installed for tracing
- [ ] Structured logs shipped to a log aggregator; correlation IDs visible
- [ ] Flower (or equivalent) monitoring worker queue depth
- [ ] Alerts: error rate, queue backlog, DB latency, 5xx rate

## Performance
- [ ] Load test passed (target: 500 msg/sec, 1000 concurrent WS) — see tasks T286
- [ ] Slow query log reviewed (`SLOW_QUERY_MS`); hot paths indexed (migration `0004`)
- [ ] Caching enabled for read-mostly data (contact profiles, channel configs)

## Reliability
- [ ] Health checks wired to the orchestrator (`GET /health`)
- [ ] Workers run with `acks_late` + retries (configured); dead-letter monitored
- [ ] Graceful shutdown verified (in-flight tasks drain)
- [ ] Rollback plan: previous image + `alembic downgrade` path tested

## Frontend
- [ ] Production build (`Dockerfile.prod`, standalone output) deployed
- [ ] `NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_WS_URL` point to production endpoints
- [ ] HTTPS + secure cookies end-to-end
