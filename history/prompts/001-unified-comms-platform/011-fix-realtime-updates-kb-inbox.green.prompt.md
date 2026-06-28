---
id: "011"
title: Fix Real-Time Updates KB and Inbox
stage: green
date: 2026-06-28
surface: agent
model: claude-sonnet-4-6
feature: 001-unified-comms-platform
branch: main
user: ZijaYaseen
command: fix page refresh required for KB doc status and AI handoff message
labels: ["realtime","websocket","polling","knowledge-base","inbox","bug-fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/workers/document_processor.py
  - frontend/src/app/settings/knowledge/page.tsx
  - frontend/src/app/inbox/page.tsx
tests:
  - manual: upload KB doc → status auto-changes pending→ready without refresh
  - manual: AI handoff in inbox → escalation note appears within 5 s without refresh
---

## Prompt

Page refresh ki zarurat kyun parti hai:
1. KB me document upload karo → pending rehta hai jab tak page refresh na karo
2. AI agent ne human ko handoff kia → tab bhi page refresh karna para tab escalation note dikh

## Response snapshot

Two root causes found and fixed:

### Issue 1: Knowledge Base (no event + no subscription)
- `document_processor.py` worker processed docs but **never called `publish_event`** — no WebSocket event was ever emitted on completion
- `knowledge/page.tsx` has no WebSocket access (it's outside the InboxLayout that provides `WebSocketProvider`)

**Fix:**
- Backend: Added `publish_event(tenant_id, "document_updated", {...})` in `document_processor.py` after successful processing (and on error)
- Frontend: Added polling in `knowledge/page.tsx` — every 3 s while any doc has `status === "pending"` or `"processing"`, auto-calls `load()`. Polling stops once all docs are ready.

### Issue 2: Inbox AI Handoff (missed WS event)
- The AI service DOES emit `message_created` and inbox IS subscribed ✓
- But WebSocket is fire-and-forget — if WS drops/reconnects during the 5-15 s AI takes to respond, the event is permanently missed
- No missed-event recovery existed

**Fix:**
- Added a 5-second polling interval in `inbox/page.tsx` whenever a conversation is `active`
- `useRef` used to hold the interval so it clears properly when switching conversations
- WebSocket still fires instantly when available; polling is the safety net

## Outcome

- ✅ KB docs: pending → ready auto-updates within 3 s, no refresh needed
- ✅ Inbox: AI replies and handoff notes appear within 5 s even if WS event missed
- 🧪 Tests: Manual — upload doc, watch status; trigger AI handoff, watch note appear
- 📁 Files: 3 files modified
