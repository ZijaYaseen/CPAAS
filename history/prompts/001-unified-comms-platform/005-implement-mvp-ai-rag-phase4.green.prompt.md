---
id: 005
title: Implement MVP AI Auto-Responses + RAG (US2)
stage: green
date: 2026-06-22
surface: agent
model: claude-opus-4-8
feature: 001-unified-comms-platform
branch: 001-unified-comms-platform
user: ZijaYaseen
command: /sp.implement
labels: ["mvp", "ai", "openai-agents", "rag", "pgvector", "guardrails", "knowledge-base", "celery"]
links:
  spec: specs/001-unified-comms-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/modules/ai/models.py
 - backend/src/modules/ai/context.py
 - backend/src/modules/ai/tools.py
 - backend/src/modules/ai/guardrails.py
 - backend/src/modules/ai/agents/router.py
 - backend/src/modules/ai/agents/support.py
 - backend/src/modules/ai/agents/handoffs.py
 - backend/src/modules/ai/agents/escalation.py
 - backend/src/modules/ai/service.py
 - backend/src/modules/ai/schemas.py
 - backend/src/modules/ai/router.py
 - backend/src/modules/knowledge/models.py
 - backend/src/modules/knowledge/chunker.py
 - backend/src/modules/knowledge/embeddings.py
 - backend/src/modules/knowledge/service.py
 - backend/src/modules/knowledge/schemas.py
 - backend/src/modules/knowledge/router.py
 - backend/src/workers/ai_executor.py
 - backend/src/workers/document_processor.py
 - backend/alembic/versions/0003_ai_knowledge.py
 - frontend/src/app/settings/ai/page.tsx
 - frontend/src/app/settings/ai/runs/page.tsx
 - frontend/src/app/settings/knowledge/page.tsx
 - frontend/src/components/ai/* (KillSwitch, AgentConfigForm, RunDetailsModal)
 - frontend/src/components/knowledge/* (DocumentUpload, DocumentList)
tests:
 - "python -m py_compile (full backend) — PASS"
---

## Prompt

phase 4 kr lo pehle, or pending jo he ye unhen taskes me top pr likh do, k is trha reh
gye hen, or yun krne hen. (Do Phase 4 first; write the pending manual items at the top of
tasks.md describing what remains and how to do it.)

## Response snapshot

Added a "⚠️ PENDING / MANUAL STEPS" section at the top of tasks.md (P-1..P-7: Neon URL,
infra/deps, migrations, pgvector, OPENAI_API_KEY, smoke-test, deferred RLS hardening).

Implemented Phase 4 / User Story 2 (T107–T157), completing the MVP feature set:

- **Decision**: pgvector (embeddings in knowledge_chunks) instead of a separate Chroma
  service — single datastore (Neon), simpler ops.
- **Models + migration 0003**: ai_configurations, ai_runs, ai_tool_calls, knowledge_documents,
  knowledge_chunks (VECTOR(1536) + ivfflat index) + pgvector extension, all tenant-scoped + RLS.
- **RAG**: chunker (~512-tok/50 overlap), OpenAI embeddings (text-embedding-3-small),
  pgvector cosine search, ingestion pipeline (text/url/PDF via pypdf), document_processor worker.
  Knowledge API: upload/upload-file/list/delete/search.
- **AI (OpenAI Agents SDK)**: ToolContext (contextvar) so SDK tools get tenant DB session;
  READ-ONLY tools only (search_knowledge_base, get_contact_info, get_order_status stub) with
  enforce_read_only + BLOCKED_WRITE_TOOLS; Router + Support agents with handoff; guardrails
  (input prompt-injection, output safety, no-write-claims); escalation detection.
- **Orchestration**: ai_executor worker triggered on every inbound customer message; runs the
  graph, logs AIRun + AIToolCall audit trail, posts AI reply (→ delivery worker) or an internal
  escalation note; publishes realtime events via the sync publisher (loop-safe). Worker-context
  emit problem avoided by returning events from service and publishing in the worker.
- **AI API**: configurations, per-agent update (admin-gated), kill-switch, run logs + details.
- **Frontend**: AI settings (kill-switch + per-agent prompt/enable), AI run viewer + details
  modal (prompt/response/tool calls/escalation), knowledge base page (text/url/file upload + list).
- Full backend passes py_compile. T107–T157 marked [x] → 157/289 (all MVP phases 1–4 done).

## Outcome

- ✅ Impact: MVP complete — unified inbox + AI auto-responses grounded in RAG, read-only + escalation.
- 🧪 Tests: py_compile PASS. Runtime needs OPENAI_API_KEY + Neon + Redis + worker; not exercised live.
- 📁 Files: ~25 backend + frontend files for US2.
- 🔁 Next prompts: Wire env + smoke-test (P-1..P-6); then Phase 11 hardening or Post-MVP (5–10).
- 🧠 Reflection: Kept AI strictly read-only with two enforcement layers (tool registry + guardrails).

## Evaluation notes (flywheel)

- Failure modes observed: Worker event-loop + async Redis again → service returns events, worker publishes sync.
- Graders run and results (PASS/FAIL): py_compile PASS.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Add OPENAI key + a KB doc, send a webchat message, verify AI reply + run log.
