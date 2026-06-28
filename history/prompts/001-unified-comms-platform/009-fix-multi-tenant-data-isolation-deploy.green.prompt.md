---
id: 009
title: Fix Multi-Tenant Data Isolation + Deploy
stage: green
date: 2026-06-28
surface: agent
model: claude-sonnet-4-6
feature: 001-unified-comms-platform
branch: main
user: ZijaYaseen
command: explore project, fix org data leakage, run migration, deploy
labels: ["bug-fix","multi-tenancy","rls","deployment","security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/alembic/versions/0005_force_rls.py
  - backend/src/modules/inbox/service.py
  - backend/src/modules/inbox/router.py
  - backend/src/modules/contacts/service.py
tests:
  - health check: https://ucaas-api-919679113744.asia-south1.run.app/health → {"status":"ok","database":true,"redis":true}
---

## Prompt

explore my whole project, nd jb me dusri organization bnati hun to same hi messages ka data show hota he sb jga, ek hi data hr organization pr q a rha he, hr organization ka data alg q nhi he. kro run, or migration file bhi read kr lena, or deployment guide bhi, then complete update kr k ok ki report do, testing krun phr me

## Response snapshot

Root cause identified and fixed in two layers:

**Bug 1 (Primary — DB level):** PostgreSQL RLS bypassed for table owner. The migration code itself acknowledged this — `FORCE ROW LEVEL SECURITY` was deferred to "Phase 11 hardening" but never applied. All 8 tenant-scoped tables (users, roles, teams, contacts, channel_accounts, conversations, messages, message_status) were readable by all tenants.

**Bug 2 (Secondary — Application level):** Service layer queries had no `tenant_id` filters as defense-in-depth backup:
- `inbox/service.py list_conversations`: `select(Conversation)` with no WHERE tenant_id
- `inbox/service.py get_conversation`: no tenant filter
- `contacts/service.py get_or_create_contact`: contact dedup queries across all tenants

**Fixes applied:**
1. New migration `0005_force_rls.py` — `ALTER TABLE ... FORCE ROW LEVEL SECURITY` on all 8 tables
2. `list_conversations` — added `tenant_id` param + `WHERE tenant_id = ?` filter
3. `get_conversation` — added optional `tenant_id` param + filter
4. `list_messages`, `send_outbound`, `add_internal_note`, `assign_conversation` — pass `tenant_id` to `get_conversation`
5. `get_or_create_contact` — added `tenant_id` filter to all 3 lookup queries (email, phone, channel_identifier)

**Deployment:**
- Docker image built and pushed to `asia-south1-docker.pkg.dev/cpaas-500610/ucaas-backend/api:latest`
- Migration job `ucaas-migrate` executed successfully on Cloud Run
- `ucaas-api` deployed → revision `ucaas-api-00019-qzm`
- `ucaas-worker` deployed → revision `ucaas-worker-00009-rtr`
- Health check passed: `{"status":"ok","database":true,"redis":true}`

## Outcome

- ✅ Impact: Each organization now sees only its own conversations, messages, and contacts. Both DB-level (FORCE RLS) and application-level (explicit WHERE) isolation enforced.
- 🧪 Tests: Health check passed post-deploy. Manual multi-org test recommended by user.
- 📁 Files: 4 files modified/created — 1 new migration, 3 service/router files updated
- 🔁 Next prompts: Test with two organizations — create org A, add messages, create org B, verify org B sees empty inbox
- 🧠 Reflection: The root cause was a known deferred item in the codebase (explicitly commented). The service layer had no fallback filtering, making the bypass total. Both layers needed fixing.

## Evaluation notes (flywheel)

- Failure modes observed: RLS-only reliance without FORCE RLS is a silent failure — no error, just wrong data returned
- Graders run and results (PASS/FAIL): Health check PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add integration test that registers two tenants and asserts cross-tenant conversation query returns 0 results
