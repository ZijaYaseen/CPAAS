# Tasks: Unified Communication Platform

**Feature Branch**: `001-unified-comms-platform`
**Date**: 2026-06-21
**Input**: Design documents from `/specs/001-unified-comms-platform/`
**Prerequisites**: spec.md, plan.md, data-model.md, research.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. MVP tasks (Phases 3-4) are prioritized first, followed by Post-MVP features (Phases 5-9).

---

## ⚠️ PENDING / MANUAL STEPS (Action Required Before Live Run)

> These are NOT code tasks — they need the user (env/secrets/infra) and must be done to
> actually run & verify what has been built. Code for Phases 1–4 is complete in the repo.

- [x] **P-1 Provide Neon DATABASE_URL** — paste ONE async URL into `.env` (sync URL is auto-derived):
  - `DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST/DB?ssl=require`  ← note `ssl=require`, NOT `sslmode=require`
- [x] **P-2 Start infra & install deps** — backend uses **uv**: `cd backend && uv sync` (creates isolated `.venv`). Frontend: `cd frontend && npm install`. Redis: `docker-compose up redis` (or full stack `docker-compose up --build`).
- [x] **P-3 Run migrations** — DONE: all 4 migrations applied to Neon (19 tables + RLS, alembic at `0004`).
- [x] **P-4 Enable pgvector on Neon** — DONE: `vector` extension enabled (migration `0003`).
- [x] **P-5 GEMINI_API_KEY set** in `.env` — Gemini used instead of OpenAI. `GEMINI_API_KEY` + `LLM_MODEL=gemini-3.1-flash-lite` set.
- [~] **P-6 Smoke-test** — auth flow verified ✅. Docker stack running (redis + backend + worker) ✅. Web Chat channel connect + AI smoke test still TODO (R-4).
- [ ] **P-7 (Hardening, deferred)** RLS is advisory in MVP (app connects as DB owner). Phase 11 adds a restricted DB role + `FORCE ROW LEVEL SECURITY`. Until then, tenant isolation also relies on the service layer.

**Code status**: Phase 1 ✅ · Phase 2 ✅ · Phase 3 Inbox ✅ · Phase 4 AI ✅ · Phase 11 Hardening ✅ · Post-MVP (5–10) ⬜
**UI status**: Inbox ✅ · Avatars ✅ · Channel icons ✅ · Internal notes ✅ · WhatsApp connected ✅ · AI tuning 🔄

### 🤖 AI provider = Google Gemini (via OpenAI Agents SDK) — DONE in code

Decision: use Gemini through its OpenAI-compatible endpoint (Panaversity pattern):
`AsyncOpenAI(base_url=https://generativelanguage.googleapis.com/v1beta/openai/)` +
`OpenAIChatCompletionsModel` + `set_tracing_disabled(True)`. Embeddings use Gemini's
**native** `embedContent` (`gemini-embedding-001`, `outputDimensionality=1536` + L2
normalize) so vectors fit **pgvector VECTOR(1536) + ivfflat** (no Qdrant; pgvector index
max = 2000 dims). Code: `ai/model_provider.py`, `ai/agents/*`, `knowledge/embeddings.py`,
config `LLM_*` / `EMBEDDING_*` / `GEMINI_API_KEY` (alias).

---

## 🟢 COMPLETED THIS SESSION (2026-06-24)

### Backend
- [x] **S-1** Docker build complete — `cpaas-backend` + `cpaas-worker` images built, all 3 containers running: `cpaas-redis-1`, `cpaas-backend-1`, `cpaas-worker-1`
- [x] **S-2** Health check verified: `{"status":"ok","database":true,"redis":true}` at `http://localhost:8000/health`

### Frontend — Responsive Layout
- [x] **S-3** `react-icons` installed (`npm install react-icons`)
- [x] **S-4** `AppLayout.tsx` created — fully responsive sidebar with hamburger (react-icons `HiMenuAlt2`), desktop permanent sidebar (w-64), mobile slide-out drawer with backdrop + ESC close
- [x] **S-5** `inbox/layout.tsx` updated to use `AppLayout`
- [x] **S-6** `settings/layout.tsx` updated to use `AppLayout`
- [x] **S-7** Post-MVP placeholder pages created (with layouts): `contacts`, `tickets`, `campaigns`, `analytics` — no more 404
- [x] **S-8** `PostMvpPage.tsx` shared component — shows feature list, phase badge, "coming soon" state

### Frontend — Professional Inbox UI
- [x] **S-9** `utils.ts` — added `timeAgo`, `formatTime`, `formatDateSeparator`, `getAvatarColor`, `getInitials`
- [x] **S-10** `ConversationList.tsx` — search bar, filter tabs (All / Open / Mine / Resolved), avatar, channel icon badge, time ago, status dot, open count badge
- [x] **S-11** `ConversationItem.tsx` — color avatar with initials, WhatsApp/Email/WebChat icon badges, left-border active state, assigned indicator
- [x] **S-12** `MessageBubble.tsx` — distinct bubbles for inbound (gray), outbound (primary), AI agent (indigo + bot icon), internal note (amber); date separators between days
- [x] **S-13** `MessageThread.tsx` — date separators, empty state with icon
- [x] **S-14** `MessageComposer.tsx` — auto-resize textarea, Reply / Internal Note tabs, Cmd+Enter shortcut, mode-aware colors and send button
- [x] **S-15** `AssignmentDropdown.tsx` — polished assign/unassign button with icons
- [x] **S-16** `inbox/page.tsx` — mobile responsive (list → tap → full-screen thread, back button), professional header with avatar + status + live indicator

### Frontend — Professional Channels Settings
- [x] **S-17** `settings/channels/page.tsx` — complete rewrite: accordion cards per channel, inline step-by-step guidance, copy buttons for webhook URL and embed snippet, Gmail App Password hint, success toast, empty state

### Docs
- [x] **S-18** `docs/channel-setup-guide.md` — comprehensive guide: account setup, Web Chat embed, Email SMTP, WhatsApp Meta setup, AI knowledge base, end-to-end testing checklist, ngrok + Cloudflare tunnel, security best practices, full API reference with curl examples

---

## 🟢 COMPLETED THIS SESSION (2026-06-26)

### Backend — Email Inbound Multi-Provider Support
- [x] **S-19** `backend/src/modules/channels/email.py` — `parse_inbound()` updated to support Cloudmailin (`plain`), Mailgun (`body-plain`, `sender`, `Message-Id`) and SendGrid (`text`, `from`) field names in one unified parser
- [x] **S-20** `backend/src/modules/channels/service.py` — `_resolve_account()` updated: tries exact `inbound_address` match first, falls back to first active email channel (works with Cloudmailin/Mailgun sandbox where recipient ≠ Gmail address)

### Frontend — Email Channel Inbound Guide
- [x] **S-21** `frontend/src/app/settings/channels/page.tsx` — `EmailForm` now shows success state after connect with full inbound setup guide: webhook URL (auto-filled), step-by-step Cloudmailin Apps Script instructions, production domain note
- [x] **S-22** `EmailInboundGuide` component added — pre-filled Apps Script with webhook URL + channel ID, numbered steps, copy button

### Tools
- [x] **S-23** `ngrok` installed via winget (v3.3.1) — available system-wide

---

## 🟢 COMPLETED THIS SESSION (2026-06-26 → 2026-06-27)

### Backend — Channel Fixes
- [x] **S-24** `backend/src/modules/channels/email.py` — `parse_inbound()` Cloudmailin `headers[from]`, `headers[to]`, `headers[subject]`, `headers[message_id]` format support (flat nested keys, not top-level `from`)
- [x] **S-25** `backend/src/modules/channels/router.py` — email webhook form keys normalized to lowercase; WhatsApp WABA auto-subscribe via Graph API on channel connect (`POST /{waba_id}/subscribed_apps`)
- [x] **S-26** `backend/src/modules/channels/whatsapp.py` — signature verification bug fixed: returns `True` (skip) when no `app_secret` configured, `False` only when secret present but signature missing/wrong
- [x] **S-27** `backend/src/modules/channels/schemas.py` — `waba_id: str | None = None` added to `WhatsAppConnectRequest`
- [x] **S-28** `backend/src/modules/inbox/service.py` — `list_conversations` fetches `ChannelAccount` for each conversation and includes `channel_type` in result dict
- [x] **S-29** `backend/src/modules/inbox/schemas.py` — `channel_type: str | None = None` added to `ConversationResponse`
- [x] **S-30** `backend/src/modules/inbox/router.py` — `channel_type=row.get("channel_type")` passed to `ConversationResponse`

### Frontend — Inbox UI Improvements
- [x] **S-31** `frontend/src/components/messages/MessageComposer.tsx` — Enter = send, Shift+Enter = new line; send button moved inside textarea (absolute bottom-right)
- [x] **S-32** `frontend/src/components/messages/MessageBubble.tsx` — AI system notes (🤖) → compact centered pill; human internal notes → Intercom-style amber card with left accent bar, avatar, "left a note", Private lock icon
- [x] **S-33** `frontend/src/app/inbox/page.tsx` — removed duplicate `<InternalNotes>` component render (was showing AI notes twice)
- [x] **S-34** `frontend/src/lib/inbox.ts` — `channel_type: string | null` added to `Conversation` type
- [x] **S-35** `frontend/src/components/inbox/ConversationList.tsx` — `channelType={c.channel_type ?? undefined}` passed to `ConversationItem`
- [x] **S-36** `frontend/src/app/settings/channels/page.tsx` — `wabaId` state + WhatsApp Business Account ID field added; `waba_id` passed in connect API call

### Frontend — Avatar System
- [x] **S-37** `frontend/src/lib/utils.ts` — `getAvatarColor` changed from Tailwind class strings to hex colors (`#7c3aed`, `#2563eb`, etc.) — fixes Tailwind content scan issue where `src/lib/` was excluded
- [x] **S-38** `frontend/src/components/inbox/ConversationItem.tsx` — avatar uses `style={{ backgroundColor: avatarColor }}` instead of Tailwind class
- [x] **S-39** `frontend/src/components/messages/MessageBubble.tsx` — inbound messages show actual contact initials + color via `contactName`/`contactId` props; outbound shows agent initials via `agentName`/`agentId` props; avatar alignment changed to `items-center`
- [x] **S-40** `frontend/src/components/messages/MessageThread.tsx` — accepts `contactName`, `contactId`, `agentName`, `agentId` props and forwards to `MessageBubble`
- [x] **S-41** `frontend/src/app/inbox/page.tsx` — passes `contact` and `user` info to `MessageThread` for avatar rendering
- [x] **S-42** `frontend/src/app/inbox/page.tsx` — header contact avatar uses `style={{ backgroundColor }}` inline hex

### Docs
- [x] **S-43** `docs/email-setup-guide.md` — end-user guide for connecting Gmail via Cloudmailin
- [x] **S-44** `docs/webchat-setup-guide.md` — embed snippet guide for web chat widget
- [x] **S-45** `docs/whatsapp-setup-guide.md` — Meta Developer App setup, WABA subscription, phone number ID guide

### Env / Infra
- [x] **S-46** `.env` + Cloud Run — `WHATSAPP_VERIFY_TOKEN=whatsapp-verify-token` set (platform-level token; per-tenant app secrets stored in DB)

---

## ⏳ PENDING — Email Inbound via Cloudmailin

> **Context**: Email outbound (SMTP replies) works. Inbound needs Cloudmailin webhook + Gmail forwarding.
> Backend is deployed on Cloud Run — **ngrok is NOT needed**.
> Webhook URL: `https://ucaas-api-919679113744.asia-south1.run.app/webhooks/email`

- [x] **E-1** ~~Run ngrok~~ — SKIPPED: backend already deployed on Cloud Run. Public URL ready.
- [ ] **E-2** Cloudmailin (cloudmailin.com) → set HTTP target:
  `https://ucaas-api-919679113744.asia-south1.run.app/webhooks/email`
  → Format: **Multipart - Normalized** → copy assigned address (e.g. `abc123@cloudmailin.net`)
- [ ] **E-3** Gmail Settings → Forwarding → Add `abc123@cloudmailin.net` → confirm the verification email from Gmail (check Cloudmailin logs for the confirmation link)
- [ ] **E-4** Test: send email to your Gmail from any address → should appear in inbox within seconds
- [x] **E-5** ~~Production URL swap~~ — SKIPPED: Cloud Run URL was used from the start.

---

## 🔄 RESUME HERE — Next Session

### 🤖 Priority 1 — AI Agents: Handle Normal Queries Automatically

**Goal**: Inbound customer messages se AI automatically response kare — no human needed for FAQs

**Current State**: AI infrastructure already built (Phase 4 ✅) — agents exist, knowledge base exists, Celery worker triggers AI on every inbound. Issue is tuning prompts + testing the end-to-end flow.

#### Step 1 — Knowledge Base Setup
- [ ] **AI-1** `Settings → Knowledge Base` → upload FAQ content (paste text or upload PDF)
  - Test: POST `https://ucaas-api-919679113744.asia-south1.run.app/api/v1/knowledge/documents`
- [ ] **AI-2** Verify embeddings generated: GET `/api/v1/knowledge/documents` → status should be `ready`
- [ ] **AI-3** Test semantic search: POST `/api/v1/knowledge/search` with `{"query": "your FAQ question"}`

#### Step 2 — AI Agent Configuration
- [ ] **AI-4** `Settings → AI Agents` → Support agent → enable + review system prompt
- [ ] **AI-5** Tune support agent prompt in `backend/src/modules/ai/agents/support.py` — add product context, tone, escalation rules
- [ ] **AI-6** Review routing agent in `backend/src/modules/ai/agents/router.py` — ensure it correctly classifies: support / sales / billing / escalate-to-human

#### Step 3 — End-to-End Test
- [ ] **AI-7** Send test message via Web Chat or WhatsApp
- [ ] **AI-8** Verify AI auto-reply appears in inbox within 5-10 seconds
- [ ] **AI-9** Check AI run log: GET `/api/v1/ai/runs` — should show tool calls + response
- [ ] **AI-10** Test escalation: send complex query → AI should escalate → internal note "🤖 AI escalated..." appears

#### Step 4 — Improve AI Response Quality
- [ ] **AI-11** If responses are generic: add more specific KB documents
- [ ] **AI-12** If escalation too aggressive: tune confidence threshold in `backend/src/modules/ai/agents/escalation.py`
- [ ] **AI-13** Test multi-turn: send follow-up questions → AI should maintain context within conversation
- [ ] **AI-14** (Optional) Add custom tools: `get_order_status` with real data source

#### Step 5 — Production AI Config
- [ ] **AI-15** Verify `GEMINI_API_KEY` is set in Cloud Run env vars
- [ ] **AI-16** Verify `LLM_MODEL=gemini-2.5-flash` (or `gemini-2.0-flash-lite` for cost savings)
- [ ] **AI-17** Monitor Cloud Run Celery worker logs for AI task errors

---

### Priority 2 — Pending Channel Tests

- [x] **R-WA-1** WhatsApp connected and working (WABA subscribed ✅)
- [ ] **E-2** Cloudmailin setup: set HTTP target `https://ucaas-api-919679113744.asia-south1.run.app/webhooks/email` → Format: Multipart Normalized
- [ ] **E-3** Gmail forwarding to Cloudmailin address
- [ ] **E-4** Test email inbound end-to-end

### Priority 3 — Production Deployment

- [x] **D-1** Backend deployed to **Google Cloud Run**:
  - API: `https://ucaas-api-919679113744.asia-south1.run.app`
  - Worker: `https://ucaas-worker-919679113744.asia-south1.run.app` (internal)
  - Health: `{"status":"ok","database":true,"redis":true}` ✅
- [ ] **D-2** Deploy frontend to **Vercel**:
  - Connect GitHub repo → select `frontend/` as root
  - Set env var: `NEXT_PUBLIC_API_URL=https://ucaas-api-919679113744.asia-south1.run.app`
  - Set env var: `NEXT_PUBLIC_WS_URL=wss://ucaas-api-919679113744.asia-south1.run.app`
- [ ] **D-3** After frontend deploy: update Cloud Run `FRONTEND_ORIGIN` env var:
  `gcloud run deploy ucaas-api --update-env-vars FRONTEND_ORIGIN=https://your-vercel-app.vercel.app --region=asia-south1 --project=cpaas-500610`
- [ ] **D-4** WhatsApp webhook URL on Meta: use Cloud Run URL (no ngrok needed):
  `https://ucaas-api-919679113744.asia-south1.run.app/webhooks/whatsapp`

### Priority 4 — Remaining MVP validation tasks

- [ ] **T286** Load testing: 500 msg/sec, 1000 concurrent WebSocket connections (`tests/load/`)
- [ ] **T287** Security scan: `docker-compose exec backend uv run pip-audit`
- [ ] **T288** Quickstart validation on a clean machine (`docs/channel-setup-guide.md`)
- [ ] **R-7** Document Gemini decision in `specs/.../research.md` and `plan.md`
- [ ] **P-7** Hardening: restricted DB role + `FORCE ROW LEVEL SECURITY` on Neon (deferred)

### Post-MVP (start after MVP validation)

- Phases 5–10 (~109 tasks): Broadcasts, Tickets, full CRM, Voice, Analytics, Instagram/Facebook/SMS
- All module folders already created and ready to fill in

### 🐳 How to run — Backend via Docker, Frontend local

> **Strategy**: Redis + Backend + Celery Worker = Docker. Frontend = local terminal.
> Backend is **uv-native** (deps in `backend/pyproject.toml` + `uv.lock`; no requirements.txt).
> The Dockerfile installs via `uv sync`. Make sure `.env` exists at repo root.

**Step 1 — Backend (Docker):**
```bash
# Build aur start karo (redis + backend + worker)
docker-compose up --build -d redis backend worker

# Pehli dafa ya migration changes ke baad:
docker-compose run --rm backend uv run alembic upgrade head

# Logs dekhne ke liye:
docker-compose logs -f backend

# API Docs: http://localhost:8000/docs
# Health:   http://localhost:8000/health
```

**Step 2 — Frontend (Local Terminal):**
```bash
cd frontend
npm install       # pehli dafa
npm run dev
# Opens at http://localhost:3000
```

**Useful commands:**
```bash
docker-compose down                              # sab band karo
docker-compose logs -f backend worker            # dono ke logs
docker-compose run --rm backend uv add <pkg>    # naya package add karo
```

> **Note**: `.env` mein `REDIS_URL=redis://redis:6379/0` Docker ke liye theek hai
> (Docker network mein `redis` service name resolve hoti hai).

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- All paths are absolute from repository root

---

## 🎯 MVP-First Strategy

**MVP Scope (8-10 weeks)**: Phases 1-4 + Phase 10 (Setup, Foundation, US1 Inbox, US2 AI, Hardening)
- **MVP Channels**: WhatsApp, Email, Web Chat only
- **MVP AI Tools**: Read-only operations only (search_knowledge_base, get_contact_info)
- **MVP Workers**: Message ingestion + AI execution

**Post-MVP**: Phases 5-9 (CRM, Tickets, Broadcasts, Remaining Channels, Voice, Analytics)
- Defer based on customer feedback after MVP launch

---

## Phase 1: Setup & Infrastructure (Week 1)

**Purpose**: Initialize project structure and development environment

- [x] T001 Create project directory structure per plan.md in backend/ and frontend/
- [x] T002 Initialize Python 3.11 backend project with pyproject.toml in backend/
- [x] T003 [P] Initialize Next.js 16 frontend project with TypeScript in frontend/
- [x] T004 [P] Configure Docker Compose with services: backend, frontend, postgres, redis in docker-compose.yml
- [x] T005 [P] Create environment configuration template in .env.example
- [x] T006 [P] Configure Python linting (ruff) and formatting (black) in backend/pyproject.toml
- [x] T007 [P] Configure TypeScript/ESLint/Prettier in frontend/
- [x] T008 Install core dependencies: FastAPI, SQLAlchemy 2.0 async, Pydantic v2 in backend/requirements.txt
- [x] T009 [P] Install core dependencies: Next.js 16, React 18, Tailwind CSS, shadcn/ui in frontend/package.json
- [x] T010 Create README.md with quickstart instructions at repository root
- [x] T011 [P] Setup Git ignore files in .gitignore for Python and Node.js
- [x] T012 Initialize Alembic for database migrations in backend/alembic/

**Checkpoint**: Development environment ready - can run `docker-compose up` successfully

---

## Phase 2: Foundation (Weeks 1-2) ⚠️ CRITICAL - BLOCKS ALL USER STORIES

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema (Foundation)

- [x] T013 [P] Create tenants table with RLS setup in backend/alembic/versions/001_create_tenants.py
- [x] T014 [P] Create users table with tenant_id FK and RLS in backend/alembic/versions/002_create_users.py
- [x] T015 [P] Create sessions table in backend/alembic/versions/003_create_sessions.py
- [x] T016 [P] Create roles and user_roles tables in backend/alembic/versions/004_create_roles.py
- [x] T017 [P] Create teams and team_members tables in backend/alembic/versions/005_create_teams.py
- [x] T018 Configure PostgreSQL connection with async engine in backend/src/core/database.py
- [x] T019 Implement RLS policy enforcement helper functions in backend/src/core/database.py
- [x] T020 Create SQLAlchemy base models with tenant_id mixin in backend/src/core/models.py

### Authentication & Multi-Tenancy

- [x] T021 Integrate Better Auth library in backend/src/core/auth.py
- [x] T022 Create Tenant model in backend/src/modules/auth/models.py
- [x] T023 [P] Create User model in backend/src/modules/auth/models.py
- [x] T024 [P] Create Session model in backend/src/modules/auth/models.py
- [x] T025 [P] Create Role and Permission models in backend/src/modules/auth/models.py
- [x] T026 Implement tenant context middleware (extract tenant_id from session) in backend/src/core/middleware.py
- [x] T027 Implement authentication dependency (require_auth) in backend/src/modules/auth/dependencies.py
- [x] T028 [P] Implement authorization dependency (require_role) in backend/src/modules/auth/dependencies.py
- [x] T029 Create auth router with POST /auth/register endpoint in backend/src/modules/auth/router.py
- [x] T030 [P] Create POST /auth/login endpoint in backend/src/modules/auth/router.py
- [x] T031 [P] Create POST /auth/logout endpoint in backend/src/modules/auth/router.py
- [x] T032 [P] Create GET /auth/me endpoint in backend/src/modules/auth/router.py
- [x] T033 Implement authentication service (register, login, logout) in backend/src/modules/auth/service.py
- [x] T034 Create Pydantic schemas for auth (LoginRequest, RegisterRequest, UserResponse) in backend/src/modules/auth/schemas.py

### Frontend Foundation

- [x] T035 Create AuthContext with session management in frontend/src/contexts/AuthContext.tsx
- [x] T036 [P] Create TenantContext for multi-tenant state in frontend/src/contexts/TenantContext.tsx
- [x] T037 Create API client with axios and tenant headers in frontend/src/lib/api.ts
- [x] T038 Create login page in frontend/src/app/(auth)/login/page.tsx
- [x] T039 [P] Create register page in frontend/src/app/(auth)/register/page.tsx
- [x] T040 Create root layout with auth provider in frontend/src/app/layout.tsx
- [x] T041 Install and configure shadcn/ui components (Button, Input, Card) in frontend/src/components/ui/

### Core Infrastructure

- [x] T042 Configure Redis connection in backend/src/core/redis.py
- [x] T043 Implement structured logging with correlation IDs in backend/src/core/logging.py
- [x] T044 Create global error handler middleware in backend/src/core/middleware.py
- [x] T045 Configure CORS for frontend origin in backend/src/main.py
- [x] T046 Create health check endpoint GET /health in backend/src/main.py
- [x] T047 Setup environment configuration loader in backend/src/core/config.py

**Checkpoint**: Foundation ready - authentication works, multi-tenancy enforced, user story implementation can begin

---

## Phase 3: User Story 1 - Multi-Channel Inbox (P1) 🎯 MVP (Weeks 3-7)

**Goal**: Build unified inbox where agents can view and respond to messages from all channels in a single interface

**Independent Test**: Connect WhatsApp/Email/Web Chat, receive messages, send replies through unified inbox UI

**MVP Channels**: WhatsApp Business API, Email (SMTP/API), Web Chat widget ONLY
**Post-MVP Channels**: Instagram, Facebook Messenger, SMS (deferred to Phase 5)

### Database Models (US1)

- [x] T048 Create conversations table with tenant_id and RLS in backend/alembic/versions/010_create_conversations.py
- [x] T049 [P] Create messages table with tenant_id and RLS in backend/alembic/versions/011_create_messages.py
- [x] T050 [P] Create message_status table with tenant_id and RLS in backend/alembic/versions/012_create_message_status.py
- [x] T051 [P] Create contacts table (basic auto-creation only) in backend/alembic/versions/013_create_contacts.py
- [x] T052 [P] Create channel_accounts table in backend/alembic/versions/014_create_channel_accounts.py
- [x] T053 Create Conversation model in backend/src/modules/inbox/models.py
- [x] T054 [P] Create Message model in backend/src/modules/inbox/models.py
- [x] T055 [P] Create MessageStatus model in backend/src/modules/inbox/models.py
- [x] T056 [P] Create Contact model (basic fields only) in backend/src/modules/contacts/models.py
- [x] T057 [P] Create ChannelAccount model in backend/src/modules/channels/models.py

### Real-Time Infrastructure (US1)

- [x] T058 Implement WebSocket manager with Redis pub/sub in backend/src/core/websocket.py
- [x] T059 Create WebSocket endpoint /ws with authentication in backend/src/main.py
- [x] T060 Implement event emitter (publish to Redis channel) in backend/src/core/websocket.py
- [x] T061 Create WebSocketContext with reconnect logic in frontend/src/contexts/WebSocketContext.tsx

### Inbox API (US1)

- [x] T062 Create inbox router in backend/src/modules/inbox/router.py
- [x] T063 Implement GET /api/v1/inbox/conversations endpoint (list conversations) in backend/src/modules/inbox/router.py
- [x] T064 [P] Implement GET /api/v1/inbox/conversations/{id}/messages endpoint in backend/src/modules/inbox/router.py
- [x] T065 [P] Implement POST /api/v1/inbox/conversations/{id}/messages endpoint (send message) in backend/src/modules/inbox/router.py
- [x] T066 [P] Implement PUT /api/v1/inbox/conversations/{id}/assign endpoint in backend/src/modules/inbox/router.py
- [x] T067 [P] Implement POST /api/v1/inbox/conversations/{id}/notes endpoint (internal notes) in backend/src/modules/inbox/router.py
- [x] T068 Create inbox service with conversation query logic in backend/src/modules/inbox/service.py
- [x] T069 Implement message sending logic with channel routing in backend/src/modules/inbox/service.py
- [x] T070 Create Pydantic schemas (ConversationResponse, MessageRequest, MessageResponse) in backend/src/modules/inbox/schemas.py

### Channel Integration - WhatsApp (US1 - MVP)

- [x] T071 Create channels router in backend/src/modules/channels/router.py
- [x] T072 Implement POST /api/v1/channels/whatsapp/connect endpoint in backend/src/modules/channels/router.py
- [x] T073 Implement POST /webhooks/whatsapp webhook endpoint in backend/src/modules/channels/router.py
- [x] T074 Create WhatsApp webhook signature validator in backend/src/modules/channels/whatsapp.py
- [x] T075 Implement WhatsApp message normalization (channel → unified schema) in backend/src/modules/channels/whatsapp.py
- [x] T076 Implement WhatsApp send API client in backend/src/modules/channels/whatsapp.py
- [x] T077 Create WhatsApp service with credential encryption in backend/src/modules/channels/service.py

### Channel Integration - Email (US1 - MVP)

- [x] T078 Implement POST /api/v1/channels/email/connect endpoint (SMTP config) in backend/src/modules/channels/router.py
- [x] T079 [P] Implement POST /webhooks/email webhook endpoint (SendGrid Inbound Parse) in backend/src/modules/channels/router.py
- [x] T080 Create Email SMTP sender with aiosmtplib in backend/src/modules/channels/email.py
- [x] T081 [P] Implement Email IMAP poller for inbox sync in backend/src/modules/channels/email.py
- [x] T082 Implement Email message normalization in backend/src/modules/channels/email.py

### Channel Integration - Web Chat (US1 - MVP)

- [x] T083 Implement POST /api/v1/channels/webchat/create endpoint in backend/src/modules/channels/router.py
- [x] T084 [P] Implement POST /api/v1/webchat/messages endpoint (public, no auth) in backend/src/modules/channels/router.py
- [x] T085 Create embeddable web chat widget in frontend/public/webchat-widget.js
- [x] T086 Implement two-way web chat: visitor polling (GET /api/v1/webchat/messages) + widget polling every 3s for agent replies in frontend/public/webchat-widget.js and backend/src/modules/channels/router.py

### Contact Auto-Creation (US1 - MVP Basic)

- [x] T087 Implement contact auto-creation from new messages in backend/src/modules/contacts/service.py
- [x] T088 Create contact deduplication logic (by email/phone) in backend/src/modules/contacts/service.py
- [x] T089 Create Contact schemas (ContactResponse) in backend/src/modules/contacts/schemas.py

### Workers - Message Processing (US1 - MVP)

- [x] T090 Configure Celery with Redis broker in backend/src/celery.py
- [x] T091 Create message ingestion worker in backend/src/workers/message_processor.py
- [x] T092 Implement webhook processing worker in backend/src/workers/webhook_processor.py
- [x] T093 Implement Email IMAP sync worker (runs every 30s) in backend/src/workers/email_sync.py
- [x] T094 Implement retry handler for failed tasks in backend/src/workers/retry_handler.py
- [x] T095 Configure Flower dashboard for worker monitoring in backend/src/celery.py

### Frontend - Inbox UI (US1)

- [x] T096 Create inbox layout in frontend/src/app/inbox/layout.tsx
- [x] T097 Create conversations list component in frontend/src/components/inbox/ConversationList.tsx
- [x] T098 [P] Create conversation item component with channel indicator in frontend/src/components/inbox/ConversationItem.tsx
- [x] T099 Create message thread component in frontend/src/components/inbox/MessageThread.tsx
- [x] T100 [P] Create message bubble component in frontend/src/components/messages/MessageBubble.tsx
- [x] T101 [P] Create message composer component in frontend/src/components/messages/MessageComposer.tsx
- [x] T102 Create typing indicator component in frontend/src/components/messages/TypingIndicator.tsx
- [x] T103 Implement real-time message updates in inbox page in frontend/src/app/inbox/page.tsx
- [x] T104 Create conversation assignment UI in frontend/src/components/inbox/AssignmentDropdown.tsx
- [x] T105 Create internal notes UI in frontend/src/components/inbox/InternalNotes.tsx
- [x] T106 Create channel connection settings page in frontend/src/app/settings/channels/page.tsx

**Checkpoint**: User Story 1 complete - unified inbox works with WhatsApp, Email, Web Chat; real-time updates functional

---

## Phase 4: User Story 2 - AI Auto-Responses (P2) 🎯 MVP (Weeks 8-10)

**Goal**: AI agents automatically respond to common inquiries and escalate complex issues to humans

**Independent Test**: Configure AI agent, send test messages, verify auto-responses and escalation logic

**MVP AI Capabilities**: Read-only operations ONLY (search_knowledge_base, get_contact_info)
**MVP AI Agents**: Routing agent + Support agent (Sales/Billing agents deferred to Post-MVP)
**Post-MVP**: Write operations (create_ticket, update_contact, send_broadcast) require human approval

### Database Models (US2)

- [x] T107 Create ai_configurations table in backend/alembic/versions/020_create_ai_configurations.py
- [x] T108 [P] Create ai_runs table in backend/alembic/versions/021_create_ai_runs.py
- [x] T109 [P] Create ai_tool_calls table in backend/alembic/versions/022_create_ai_tool_calls.py
- [x] T110 [P] Create knowledge_documents table in backend/alembic/versions/023_create_knowledge_documents.py
- [x] T111 [P] Create knowledge_chunks table with pgvector extension in backend/alembic/versions/024_create_knowledge_chunks.py
- [x] T112 Create AIConfiguration model in backend/src/modules/ai/models.py
- [x] T113 [P] Create AIRun model in backend/src/modules/ai/models.py
- [x] T114 [P] Create AIToolCall model in backend/src/modules/ai/models.py
- [x] T115 [P] Create KnowledgeDocument model in backend/src/modules/knowledge/models.py
- [x] T116 [P] Create KnowledgeChunk model in backend/src/modules/knowledge/models.py

### AI Configuration (US2)

- [x] T117 Install OpenAI Agents SDK in backend/requirements.txt
- [x] T118 Create AI router in backend/src/modules/ai/router.py
- [x] T119 Implement GET /api/v1/ai/configurations endpoint in backend/src/modules/ai/router.py
- [x] T120 [P] Implement PUT /api/v1/ai/configurations/{agent_type} endpoint in backend/src/modules/ai/router.py
- [x] T121 [P] Implement POST /api/v1/ai/kill-switch endpoint in backend/src/modules/ai/router.py
- [x] T122 Create AI configuration service in backend/src/modules/ai/service.py
- [x] T123 Create AI configuration schemas in backend/src/modules/ai/schemas.py

### AI Read-Only Tool Functions (US2 - MVP)

- [x] T124 Create search_knowledge_base tool function in backend/src/modules/ai/tools.py
- [x] T125 [P] Create get_contact_info tool function in backend/src/modules/ai/tools.py
- [x] T126 [P] Create get_order_status tool function (mock/stub) in backend/src/modules/ai/tools.py
- [x] T127 Implement tool function registry with read-only enforcement in backend/src/modules/ai/tools.py

### AI Agents (US2 - MVP)

- [x] T128 Create routing agent (classifies intent: support/sales/billing) in backend/src/modules/ai/agents/router.py
- [x] T129 Create support agent with RAG integration in backend/src/modules/ai/agents/support.py
- [x] T130 Implement agent handoff logic (routing → support → human) in backend/src/modules/ai/agents/handoffs.py
- [x] T131 Create human escalation handler in backend/src/modules/ai/agents/escalation.py

### AI Guardrails (US2 - MVP)

- [x] T132 Implement input guardrails (profanity filter, prompt injection detection) in backend/src/modules/ai/guardrails.py
- [x] T133 [P] Implement output guardrails (no unauthorized actions, on-brand responses) in backend/src/modules/ai/guardrails.py
- [x] T134 Create tool restriction enforcer (block write operations) in backend/src/modules/ai/guardrails.py

### Knowledge Base (RAG) (US2 - MVP)

- [x] T135 Configure Chroma vector database in backend/src/modules/knowledge/chroma.py
- [x] T136 Create knowledge router in backend/src/modules/knowledge/router.py
- [x] T137 Implement POST /api/v1/knowledge/documents endpoint (upload) in backend/src/modules/knowledge/router.py
- [x] T138 [P] Implement GET /api/v1/knowledge/documents endpoint in backend/src/modules/knowledge/router.py
- [x] T139 [P] Implement DELETE /api/v1/knowledge/documents/{id} endpoint in backend/src/modules/knowledge/router.py
- [x] T140 [P] Implement POST /api/v1/knowledge/search endpoint (semantic search) in backend/src/modules/knowledge/router.py
- [x] T141 Create document ingestion pipeline (PDF, text, URL) in backend/src/modules/knowledge/service.py
- [x] T142 Implement text chunking (512 tokens, 50-token overlap) in backend/src/modules/knowledge/chunker.py
- [x] T143 Integrate OpenAI embeddings API (text-embedding-3-small) in backend/src/modules/knowledge/embeddings.py
- [x] T144 Implement semantic search with vector similarity in backend/src/modules/knowledge/service.py
- [x] T145 Create document processing worker (async) in backend/src/workers/document_processor.py

### AI Execution & Logging (US2 - MVP)

- [x] T146 Create AI execution worker in backend/src/workers/ai_executor.py
- [x] T147 Implement AI run logging (prompt, tool calls, response) in backend/src/modules/ai/service.py
- [x] T148 Implement GET /api/v1/ai/runs endpoint (audit logs) in backend/src/modules/ai/router.py
- [x] T149 [P] Implement GET /api/v1/ai/runs/{id} endpoint (run details) in backend/src/modules/ai/router.py

### Frontend - AI Configuration UI (US2)

- [x] T150 Create AI settings page in frontend/src/app/settings/ai/page.tsx
- [x] T151 Create agent configuration form in frontend/src/components/ai/AgentConfigForm.tsx
- [x] T152 [P] Create AI kill-switch button in frontend/src/components/ai/KillSwitch.tsx
- [x] T153 Create AI run viewer (audit logs) in frontend/src/app/settings/ai/runs/page.tsx
- [x] T154 Create AI run details modal in frontend/src/components/ai/RunDetailsModal.tsx

### Frontend - Knowledge Base UI (US2)

- [x] T155 Create knowledge base page in frontend/src/app/settings/knowledge/page.tsx
- [x] T156 Create document upload component in frontend/src/components/knowledge/DocumentUpload.tsx
- [x] T157 [P] Create document list component in frontend/src/components/knowledge/DocumentList.tsx

**Checkpoint**: User Story 2 complete - AI auto-responds using knowledge base, escalates to humans when needed

---

## Phase 5: User Story 3 - Broadcast Campaigns (P3) ⏸️ POST-MVP (Weeks 15-16)

**Goal**: Enable bulk messaging to segmented contact lists with delivery tracking

**Independent Test**: Create campaign, target specific tags, schedule send, verify delivery tracking

> **DEFERRED TO POST-MVP**: This phase implemented after MVP launch based on customer demand

### Database Models (US3 - Post-MVP)

- [ ] T158 Create campaigns table in backend/alembic/versions/030_create_campaigns.py
- [ ] T159 [P] Create campaign_recipients table in backend/alembic/versions/031_create_campaign_recipients.py
- [ ] T160 Create Campaign model in backend/src/modules/campaigns/models.py
- [ ] T161 [P] Create CampaignRecipient model in backend/src/modules/campaigns/models.py

### Campaigns API (US3 - Post-MVP)

- [ ] T162 Create campaigns router in backend/src/modules/campaigns/router.py
- [ ] T163 Implement POST /api/v1/campaigns endpoint (create campaign) in backend/src/modules/campaigns/router.py
- [ ] T164 [P] Implement GET /api/v1/campaigns endpoint in backend/src/modules/campaigns/router.py
- [ ] T165 [P] Implement GET /api/v1/campaigns/{id} endpoint in backend/src/modules/campaigns/router.py
- [ ] T166 [P] Implement PUT /api/v1/campaigns/{id}/schedule endpoint in backend/src/modules/campaigns/router.py
- [ ] T167 [P] Implement POST /api/v1/campaigns/{id}/pause endpoint in backend/src/modules/campaigns/router.py
- [ ] T168 [P] Implement POST /api/v1/campaigns/{id}/resume endpoint in backend/src/modules/campaigns/router.py
- [ ] T169 [P] Implement DELETE /api/v1/campaigns/{id} endpoint (cancel) in backend/src/modules/campaigns/router.py
- [ ] T170 Create campaign service with audience segmentation in backend/src/modules/campaigns/service.py
- [ ] T171 Implement template variable substitution in backend/src/modules/campaigns/templates.py

### Broadcast Worker (US3 - Post-MVP)

- [ ] T172 Create broadcast sending worker with rate limiting in backend/src/workers/broadcast_sender.py
- [ ] T173 Implement campaign scheduler worker in backend/src/workers/campaign_scheduler.py
- [ ] T174 Create delivery tracking logic in backend/src/workers/broadcast_sender.py

### Frontend - Campaigns UI (US3 - Post-MVP)

- [ ] T175 Create campaigns page in frontend/src/app/campaigns/page.tsx
- [ ] T176 Create campaign creation wizard in frontend/src/components/campaigns/CampaignWizard.tsx
- [ ] T177 [P] Create template editor with variable insertion in frontend/src/components/campaigns/TemplateEditor.tsx
- [ ] T178 [P] Create audience segmentation builder in frontend/src/components/campaigns/AudienceBuilder.tsx
- [ ] T179 Create campaign analytics dashboard in frontend/src/components/campaigns/CampaignAnalytics.tsx

**Checkpoint**: User Story 3 complete - broadcast campaigns functional with delivery tracking

---

## Phase 6: User Story 4 - Ticket Management (P4) ⏸️ POST-MVP (Weeks 13-14)

**Goal**: Track customer complaints with SLA enforcement and escalation rules

**Independent Test**: Create ticket from conversation, set SLA, verify escalation triggers

> **DEFERRED TO POST-MVP**: This phase implemented after MVP launch based on customer demand

### Database Models (US4 - Post-MVP)

- [ ] T180 Create tickets table in backend/alembic/versions/040_create_tickets.py
- [ ] T181 [P] Create ticket_history table in backend/alembic/versions/041_create_ticket_history.py
- [ ] T182 Create Ticket model in backend/src/modules/tickets/models.py
- [ ] T183 [P] Create TicketHistory model in backend/src/modules/tickets/models.py

### Tickets API (US4 - Post-MVP)

- [ ] T184 Create tickets router in backend/src/modules/tickets/router.py
- [ ] T185 Implement POST /api/v1/tickets endpoint (create from conversation) in backend/src/modules/tickets/router.py
- [ ] T186 [P] Implement GET /api/v1/tickets endpoint in backend/src/modules/tickets/router.py
- [ ] T187 [P] Implement GET /api/v1/tickets/{id} endpoint in backend/src/modules/tickets/router.py
- [ ] T188 [P] Implement PUT /api/v1/tickets/{id}/status endpoint in backend/src/modules/tickets/router.py
- [ ] T189 [P] Implement PUT /api/v1/tickets/{id}/priority endpoint in backend/src/modules/tickets/router.py
- [ ] T190 [P] Implement POST /api/v1/tickets/{id}/escalate endpoint in backend/src/modules/tickets/router.py
- [ ] T191 Create ticket service with lifecycle state machine in backend/src/modules/tickets/service.py
- [ ] T192 Implement SLA tracking with deadline alerts in backend/src/modules/tickets/service.py
- [ ] T193 Implement escalation rules engine in backend/src/modules/tickets/escalation.py

### Ticket Workers (US4 - Post-MVP)

- [ ] T194 Create SLA monitoring worker in backend/src/workers/sla_monitor.py
- [ ] T195 Implement ticket auto-escalation worker in backend/src/workers/ticket_escalator.py

### Frontend - Tickets UI (US4 - Post-MVP)

- [ ] T196 Create tickets page in frontend/src/app/tickets/page.tsx
- [ ] T197 Create ticket creation modal in frontend/src/components/tickets/CreateTicketModal.tsx
- [ ] T198 [P] Create ticket details view in frontend/src/components/tickets/TicketDetails.tsx
- [ ] T199 [P] Create ticket history timeline in frontend/src/components/tickets/TicketHistory.tsx
- [ ] T200 Create SLA progress indicator in frontend/src/components/tickets/SLAIndicator.tsx

**Checkpoint**: User Story 4 complete - ticket system operational with SLA enforcement

---

## Phase 7: User Story 5 - CRM Contact Management (P5) ⏸️ POST-MVP (Weeks 13-14)

**Goal**: Full contact profiles with tags, notes, lifecycle tracking, conversation history

**Independent Test**: Create contact, add tags/notes, view timeline, update lifecycle stage

> **DEFERRED TO POST-MVP**: Basic contact auto-creation in MVP (Phase 3); full CRM features post-MVP

### Database Models (US5 - Post-MVP)

- [ ] T201 Create contact_tags table in backend/alembic/versions/050_create_contact_tags.py
- [ ] T202 Extend contacts table with lifecycle_stage and metadata in backend/alembic/versions/051_extend_contacts.py
- [ ] T203 Create ContactTag model in backend/src/modules/contacts/models.py

### Contacts API (US5 - Post-MVP)

- [ ] T204 Create contacts router in backend/src/modules/contacts/router.py
- [ ] T205 Implement POST /api/v1/contacts endpoint (manual creation) in backend/src/modules/contacts/router.py
- [ ] T206 [P] Implement GET /api/v1/contacts endpoint in backend/src/modules/contacts/router.py
- [ ] T207 [P] Implement GET /api/v1/contacts/{id} endpoint in backend/src/modules/contacts/router.py
- [ ] T208 [P] Implement PUT /api/v1/contacts/{id} endpoint in backend/src/modules/contacts/router.py
- [ ] T209 [P] Implement POST /api/v1/contacts/{id}/tags endpoint in backend/src/modules/contacts/router.py
- [ ] T210 [P] Implement DELETE /api/v1/contacts/{id}/tags/{tag} endpoint in backend/src/modules/contacts/router.py
- [ ] T211 [P] Implement POST /api/v1/contacts/{id}/notes endpoint in backend/src/modules/contacts/router.py
- [ ] T212 [P] Implement PUT /api/v1/contacts/{id}/lifecycle endpoint in backend/src/modules/contacts/router.py
- [ ] T213 Implement contact search and segmentation in backend/src/modules/contacts/service.py

### Frontend - CRM UI (US5 - Post-MVP)

- [ ] T214 Create contacts page in frontend/src/app/contacts/page.tsx
- [ ] T215 Create contact profile page in frontend/src/app/contacts/[id]/page.tsx
- [ ] T216 [P] Create contact edit form in frontend/src/components/contacts/ContactForm.tsx
- [ ] T217 [P] Create contact tags component in frontend/src/components/contacts/ContactTags.tsx
- [ ] T218 [P] Create contact notes component in frontend/src/components/contacts/ContactNotes.tsx
- [ ] T219 Create contact timeline (all conversations) in frontend/src/components/contacts/ContactTimeline.tsx
- [ ] T220 Create lifecycle stage selector in frontend/src/components/contacts/LifecycleStage.tsx

**Checkpoint**: User Story 5 complete - full CRM functionality operational

---

## Phase 8: User Story 6 - Voice Communication (P6) ⏸️ POST-MVP (Weeks 18-20)

**Goal**: Make/receive voice calls with transcription and call logs

**Independent Test**: Make test call, verify recording, check transcription accuracy, confirm inbox integration

> **DEFERRED TO POST-MVP**: Voice calling deferred to Phase 3+ per spec.md clarifications

### Database Models (US6 - Post-MVP)

- [ ] T221 Create call_logs table in backend/alembic/versions/060_create_call_logs.py
- [ ] T222 Create CallLog model in backend/src/modules/voice/models.py

### Voice Integration (US6 - Post-MVP)

- [ ] T223 Integrate Twilio Voice API in backend/src/modules/voice/twilio.py
- [ ] T224 Create voice router in backend/src/modules/voice/router.py
- [ ] T225 Implement POST /api/v1/voice/calls endpoint (outbound) in backend/src/modules/voice/router.py
- [ ] T226 [P] Implement POST /webhooks/twilio/voice endpoint (inbound) in backend/src/modules/voice/router.py
- [ ] T227 [P] Implement GET /api/v1/voice/calls endpoint in backend/src/modules/voice/router.py
- [ ] T228 [P] Implement GET /api/v1/voice/calls/{id} endpoint in backend/src/modules/voice/router.py
- [ ] T229 Create IVR menu builder with TwiML in backend/src/modules/voice/ivr.py
- [ ] T230 Implement call recording download in backend/src/modules/voice/service.py

### Transcription (US6 - Post-MVP)

- [ ] T231 Integrate OpenAI Whisper API for transcription in backend/src/modules/voice/transcription.py
- [ ] T232 Create transcription worker in backend/src/workers/transcription.py
- [ ] T233 Link transcripts to conversation timeline in backend/src/modules/voice/service.py

### Frontend - Voice UI (US6 - Post-MVP)

- [ ] T234 Create call logs page in frontend/src/app/voice/page.tsx
- [ ] T235 Create call details modal in frontend/src/components/voice/CallDetails.tsx
- [ ] T236 [P] Create call player (recording playback) in frontend/src/components/voice/CallPlayer.tsx
- [ ] T237 [P] Create transcript viewer in frontend/src/components/voice/TranscriptViewer.tsx

**Checkpoint**: User Story 6 complete - voice calling integrated with inbox

---

## Phase 9: User Story 7 - Analytics & Reporting (P7) ⏸️ POST-MVP (Weeks 18-20)

**Goal**: Dashboards showing FRT, ART, AI deflection, campaign performance, agent productivity

**Independent Test**: Generate sample data, view dashboards, verify metric accuracy, test date filters

> **DEFERRED TO POST-MVP**: Basic metrics (FRT, ART) in MVP; full analytics dashboards post-MVP

### Analytics API (US7 - Post-MVP)

- [ ] T238 Create analytics router in backend/src/modules/analytics/router.py
- [ ] T239 Implement GET /api/v1/analytics/overview endpoint in backend/src/modules/analytics/router.py
- [ ] T240 [P] Implement GET /api/v1/analytics/response-times endpoint (FRT, ART) in backend/src/modules/analytics/router.py
- [ ] T241 [P] Implement GET /api/v1/analytics/tickets endpoint (resolution time, SLA) in backend/src/modules/analytics/router.py
- [ ] T242 [P] Implement GET /api/v1/analytics/ai-deflection endpoint in backend/src/modules/analytics/router.py
- [ ] T243 [P] Implement GET /api/v1/analytics/campaigns endpoint in backend/src/modules/analytics/router.py
- [ ] T244 [P] Implement GET /api/v1/analytics/agents endpoint (productivity) in backend/src/modules/analytics/router.py
- [ ] T245 [P] Implement GET /api/v1/analytics/channels endpoint (message volume) in backend/src/modules/analytics/router.py
- [ ] T246 Create analytics service with aggregation queries in backend/src/modules/analytics/service.py
- [ ] T247 Implement data export (CSV/Excel) in backend/src/modules/analytics/export.py

### Frontend - Analytics UI (US7 - Post-MVP)

- [ ] T248 Create analytics dashboard page in frontend/src/app/analytics/page.tsx
- [ ] T249 Create response time chart component in frontend/src/components/analytics/ResponseTimeChart.tsx
- [ ] T250 [P] Create ticket metrics component in frontend/src/components/analytics/TicketMetrics.tsx
- [ ] T251 [P] Create AI deflection chart in frontend/src/components/analytics/AIDeflectionChart.tsx
- [ ] T252 [P] Create campaign performance table in frontend/src/components/analytics/CampaignPerformance.tsx
- [ ] T253 [P] Create agent productivity table in frontend/src/components/analytics/AgentProductivity.tsx
- [ ] T254 Create date range filter component in frontend/src/components/analytics/DateRangeFilter.tsx

**Checkpoint**: User Story 7 complete - full analytics dashboards operational

---

## Phase 10: Remaining Channels (Post-MVP) ⏸️ (Week 17)

**Goal**: Integrate Instagram, Facebook Messenger, SMS

> **DEFERRED TO POST-MVP**: MVP includes WhatsApp, Email, Web Chat only

### Instagram Messaging (Post-MVP)

- [ ] T255 Implement POST /api/v1/channels/instagram/connect endpoint in backend/src/modules/channels/router.py
- [ ] T256 [P] Implement POST /webhooks/instagram webhook endpoint in backend/src/modules/channels/router.py
- [ ] T257 Create Instagram message normalization in backend/src/modules/channels/instagram.py
- [ ] T258 Implement Instagram send API client in backend/src/modules/channels/instagram.py

### Facebook Messenger (Post-MVP)

- [ ] T259 Implement POST /api/v1/channels/facebook/connect endpoint in backend/src/modules/channels/router.py
- [ ] T260 [P] Implement POST /webhooks/facebook webhook endpoint in backend/src/modules/channels/router.py
- [ ] T261 Create Facebook message normalization in backend/src/modules/channels/facebook.py
- [ ] T262 Implement Facebook send API client in backend/src/modules/channels/facebook.py

### SMS (Twilio) (Post-MVP)

- [ ] T263 Implement POST /api/v1/channels/sms/connect endpoint in backend/src/modules/channels/router.py
- [ ] T264 [P] Implement POST /webhooks/twilio/sms webhook endpoint in backend/src/modules/channels/router.py
- [ ] T265 Create SMS message normalization in backend/src/modules/channels/sms.py
- [ ] T266 Implement Twilio SMS send API client in backend/src/modules/channels/sms.py

**Checkpoint**: All 7 channels integrated

---

## Phase 11: Hardening & Production Readiness (Week 12)

**Purpose**: Security, performance, observability for production deployment

### Security

- [x] T267 Implement rate limiting per tenant/user in backend/src/core/middleware.py
- [x] T268 [P] Add input validation and sanitization (XSS prevention) in backend/src/core/validation.py
- [x] T269 [P] Configure CSRF protection in backend/src/main.py
- [x] T270 Implement webhook signature validation for all channels in backend/src/modules/channels/security.py
- [x] T271 Create audit logging for critical actions in backend/src/modules/audit/service.py
- [x] T272 Create audit_logs table in backend/alembic/versions/070_create_audit_logs.py

### Observability

- [x] T273 Integrate Sentry error tracking with tenant context in backend/src/core/sentry.py
- [x] T274 [P] Configure OpenTelemetry distributed tracing in backend/src/core/telemetry.py
- [x] T275 Implement correlation ID propagation in backend/src/core/logging.py
- [x] T276 Add slow query logging in backend/src/core/database.py

### Performance

- [x] T277 Implement caching strategy (contact profiles, channel configs) in backend/src/core/cache.py
- [x] T278 Create database indexes based on query patterns in backend/alembic/versions/080_add_indexes.py
- [x] T279 Optimize conversation list query with pagination in backend/src/modules/inbox/service.py
- [x] T280 Implement connection pooling for database in backend/src/core/database.py

### Deployment

- [x] T281 Create production Dockerfile with multi-stage builds in backend/Dockerfile
- [x] T282 [P] Create production Dockerfile for frontend in frontend/Dockerfile
- [x] T283 Write deployment documentation in docs/deployment.md
- [x] T284 Create CI/CD pipeline configuration in .github/workflows/deploy.yml
- [x] T285 Setup health check monitoring in backend/src/main.py

### Testing & Validation

- [ ] T286 Run load testing (500 msg/sec, 1000 concurrent WebSocket) in tests/load/
- [ ] T287 [P] Perform security audit (dependency scanning) with `safety check`
- [ ] T288 Validate quickstart.md by running fresh setup in docs/quickstart.md
- [x] T289 Create production environment checklist in docs/production-checklist.md

**Checkpoint**: System production-ready with security, performance, and observability

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundation)**: Depends on Phase 1 completion - **BLOCKS ALL USER STORIES**
- **Phase 3 (US1 Inbox)**: Depends on Phase 2 completion - MVP priority 1
- **Phase 4 (US2 AI)**: Depends on Phase 2 completion - MVP priority 2 (can run parallel to US1 after foundation)
- **Phase 5 (US3 Broadcasts)**: POST-MVP - depends on Phase 2 + full CRM (Phase 7)
- **Phase 6 (US4 Tickets)**: POST-MVP - depends on Phase 2 + US1 (conversations)
- **Phase 7 (US5 CRM)**: POST-MVP - depends on Phase 2 + basic contacts (US1)
- **Phase 8 (US6 Voice)**: POST-MVP - depends on Phase 2 + US1 (conversations)
- **Phase 9 (US7 Analytics)**: POST-MVP - depends on operational data from US1-6
- **Phase 10 (Remaining Channels)**: POST-MVP - depends on Phase 3 (channel framework)
- **Phase 11 (Hardening)**: Depends on MVP phases (1-4) completion

### User Story Dependencies

**MVP Stories (Can run in parallel after Foundation)**:
- **User Story 1 (US1 - Inbox)**: Independent after Phase 2
- **User Story 2 (US2 - AI)**: Independent after Phase 2 (integrates with US1 but testable alone)

**Post-MVP Stories**:
- **User Story 3 (US3 - Broadcasts)**: Requires US5 (contacts/tagging) + Phase 2
- **User Story 4 (US4 - Tickets)**: Requires US1 (conversations) + Phase 2
- **User Story 5 (US5 - CRM)**: Requires basic contacts from US1 + Phase 2
- **User Story 6 (US6 - Voice)**: Requires US1 (conversation framework) + Phase 2
- **User Story 7 (US7 - Analytics)**: Requires operational data from US1-6

### Within Each User Story

- Database models before services
- Services before API endpoints
- API endpoints before workers
- Workers before frontend UI
- Tasks marked [P] can run in parallel (different files, no dependencies)

### Parallel Opportunities

**Foundation Phase (Phase 2)**:
- Database tables (T013-T017) can be created in parallel
- Auth models (T022-T025) can be created in parallel
- Frontend foundation (T035-T041) can proceed while backend auth is being built

**User Story 1 (Phase 3)**:
- Database models (T048-T052, T053-T057) can be created in parallel
- Channel integrations (WhatsApp T071-T077, Email T078-T082, Web Chat T083-T086) can be built in parallel
- Frontend components (T096-T106) can be built in parallel after API is ready

**User Story 2 (Phase 4)**:
- Database models (T107-T111, T112-T116) can be created in parallel
- Tool functions (T124-T126) can be built in parallel
- Frontend components (T150-T157) can be built in parallel after API is ready

**Post-MVP Phases**:
- Phase 10 channels (Instagram, Facebook, SMS) can be built in parallel
- All user stories 3-7 can proceed in parallel with separate teams after Phase 2

---

## Implementation Strategy

### MVP-First Approach (8-10 Weeks)

**Week 1**:
1. Complete Phase 1: Setup
2. Start Phase 2: Foundation (auth, multi-tenancy, database)

**Weeks 2**:
3. Complete Phase 2: Foundation
4. **CHECKPOINT**: Validate auth works, RLS enforced

**Weeks 3-4**:
5. Start Phase 3: User Story 1 (Inbox)
   - Database models → API → Workers → Frontend
6. Focus on WhatsApp + Email first, then Web Chat

**Weeks 5-7**:
7. Complete Phase 3: User Story 1
8. **CHECKPOINT**: Test unified inbox independently

**Weeks 8-9**:
9. Start Phase 4: User Story 2 (AI)
   - Knowledge base → AI agents → Tool functions → Frontend
10. Focus on routing + support agents only

**Week 10**:
11. Complete Phase 4: User Story 2
12. **CHECKPOINT**: Test AI auto-responses independently

**Week 11-12**:
13. Phase 11: Hardening (security, observability, performance)
14. **FINAL CHECKPOINT**: MVP ready for launch

**MVP Deliverable**: Unified inbox with WhatsApp/Email/Web Chat + AI auto-responses with read-only operations

---

### Post-MVP Expansion (12+ Weeks)

**Weeks 13-14**: Phase 6 (Tickets) + Phase 7 (CRM)
**Weeks 15-16**: Phase 5 (Broadcasts)
**Week 17**: Phase 10 (Remaining Channels: Instagram, Facebook, SMS)
**Weeks 18-20**: Phase 8 (Voice) + Phase 9 (Analytics)
**Week 21**: Integration testing across all features
**Week 22**: Production hardening and launch

---

## Summary

**Total Tasks**: 289 tasks
- **MVP Tasks (Phases 1-4, 11)**: 157 tasks (54%)
- **Post-MVP Tasks (Phases 5-10)**: 132 tasks (46%)

**Parallel Opportunities**:
- Phase 1: 7 parallel tasks
- Phase 2: 18 parallel tasks
- Phase 3 (US1): 35 parallel tasks
- Phase 4 (US2): 22 parallel tasks
- Phase 5-10 (Post-MVP): 48 parallel tasks
- Phase 11: 6 parallel tasks
- **Total Parallelizable**: 136 tasks (47%)

**Critical Path**:
1. Phase 1 (Setup) → 1 week
2. Phase 2 (Foundation) → 1 week **BLOCKS EVERYTHING**
3. Phase 3 (US1 Inbox) → 4-5 weeks (MVP Priority 1)
4. Phase 4 (US2 AI) → 3 weeks (MVP Priority 2)
5. Phase 11 (Hardening) → 2 weeks

**MVP Duration**: 8-10 weeks (Phases 1-4 + 11)
**Full Platform**: 22 weeks (All phases)

**Next Steps**:
1. Start with Phase 1 (Setup) immediately
2. Complete Phase 2 (Foundation) before any user story work
3. Focus on MVP first (Phases 3-4)
4. Validate each user story independently before proceeding
5. Deploy MVP for customer feedback before building Post-MVP features

---

**Tasks Complete**: 2026-06-21
**Status**: ✅ Ready for Implementation
**Next Action**: Begin Phase 1 - Setup & Infrastructure
