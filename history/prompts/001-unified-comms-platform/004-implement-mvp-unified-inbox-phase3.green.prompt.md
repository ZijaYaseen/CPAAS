---
id: 004
title: Implement MVP Unified Inbox (US1)
stage: green
date: 2026-06-22
surface: agent
model: claude-opus-4-8
feature: 001-unified-comms-platform
branch: 001-unified-comms-platform
user: ZijaYaseen
command: /sp.implement
labels: ["mvp", "inbox", "websocket", "channels", "whatsapp", "email", "webchat", "celery", "realtime"]
links:
  spec: specs/001-unified-comms-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/modules/inbox/models.py
 - backend/src/modules/inbox/schemas.py
 - backend/src/modules/inbox/service.py
 - backend/src/modules/inbox/router.py
 - backend/src/modules/contacts/models.py
 - backend/src/modules/contacts/service.py
 - backend/src/modules/contacts/schemas.py
 - backend/src/modules/channels/models.py
 - backend/src/modules/channels/base.py
 - backend/src/modules/channels/whatsapp.py
 - backend/src/modules/channels/email.py
 - backend/src/modules/channels/webchat.py
 - backend/src/modules/channels/service.py
 - backend/src/modules/channels/schemas.py
 - backend/src/modules/channels/router.py
 - backend/src/core/websocket.py
 - backend/src/core/events.py
 - backend/src/core/crypto.py
 - backend/src/workers/db.py
 - backend/src/workers/message_processor.py
 - backend/src/workers/webhook_processor.py
 - backend/src/workers/email_sync.py
 - backend/src/workers/retry_handler.py
 - backend/alembic/versions/0002_inbox.py
 - frontend/src/contexts/WebSocketContext.tsx
 - frontend/src/lib/inbox.ts
 - frontend/src/app/inbox/layout.tsx
 - frontend/src/app/inbox/page.tsx
 - frontend/src/app/settings/channels/page.tsx
 - frontend/src/components/inbox/*  (ConversationList, ConversationItem, AssignmentDropdown, InternalNotes)
 - frontend/src/components/messages/*  (MessageThread, MessageBubble, MessageComposer, TypingIndicator)
 - frontend/src/components/AppSidebar.tsx
 - frontend/public/webchat-widget.js
tests:
 - "python -m py_compile (full backend) — PASS"
---

## Prompt

(Continuation of /sp.implement) User chose: "Continue Phase 3 now" — build the unified
inbox vertical slice (models → WebSocket → APIs → channel adapters → workers → UI).

## Response snapshot

Completed Phase 3 / User Story 1 (T048–T106), the core MVP product:

- **Data models + migration 0002**: contacts, channel_accounts, conversations, messages
  (+ is_internal_note), message_status — all with tenant_id + RLS policies.
- **Realtime**: ConnectionManager (core/websocket.py) backed by a single Redis pub/sub
  channel; instances keep only local connections and fan out per tenant. /ws endpoint
  authenticated via the session cookie. Events: message_created/updated, assignment_changed.
  Sync publisher (core/events.py) for workers to avoid cross-event-loop Redis issues.
- **Inbox API**: list conversations (with contact + last-message preview via DISTINCT ON),
  list messages, send (outbound → persist → emit → enqueue delivery), assign, internal notes.
- **Channel adapter pattern**: ChannelAdapter ABC + NormalizedInbound/OutboundResult unify
  all channels. WhatsApp (Meta Cloud API + HMAC signature verify), Email (SendGrid Inbound
  Parse + SMTP send via aiosmtplib), Web Chat (own widget + WS delivery). Credentials
  encrypted at rest with Fernet keyed off SECRET_KEY (core/crypto.py). Public webhook routes
  + public /api/v1/webchat/messages endpoint. Contact auto-creation + dedup (email/phone/channel-id).
- **Workers (Celery)**: message_processor (deliver_outbound w/ retry + ingest), webhook_processor,
  email_sync (IMAP fallback, beat every 30s; webhook is primary), retry_handler (dead-letter).
  Per-task NullPool engine (workers/db.py) so asyncio.run is loop-safe.
- **Frontend**: WebSocketContext (auto-reconnect), full inbox (ConversationList, MessageThread,
  Bubble, Composer with reply/note toggle, AssignmentDropdown self-assign, InternalNotes),
  app sidebar nav, channel settings page, embeddable webchat-widget.js.
- Full backend passes py_compile. T048–T106 marked [x] (106/289 tasks done).

## Outcome

- ✅ Impact: End-to-end unified inbox across WhatsApp/Email/WebChat with realtime + worker delivery.
- 🧪 Tests: py_compile PASS. Runtime needs Neon DATABASE_URL + Redis + deps; not yet exercised live.
- 📁 Files: ~30 backend + frontend files for US1.
- 🔁 Next prompts: Phase 4 (US2 AI: routing+support agents, RAG, read-only tools, T107–T157).
- 🧠 Reflection: Kept inbound webhook ingestion inline for reliability; outbound via worker per arch.

## Evaluation notes (flywheel)

- Failure modes observed: Cross-event-loop Redis in Celery → solved with sync publisher + per-task engine.
- Graders run and results (PASS/FAIL): py_compile PASS.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Wire Neon + Redis, run migrations, smoke-test send/receive + WS event.
