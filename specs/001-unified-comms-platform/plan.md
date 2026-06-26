# Implementation Plan: Unified Communication Platform

**Branch**: `001-unified-comms-platform` | **Date**: 2026-06-21 | **Spec**: [spec.md](./spec.md)

## Summary

Build a multi-tenant SaaS platform that unifies WhatsApp, Email, SMS, Instagram, Facebook, Web Chat, and Voice into a single AI-powered inbox with CRM, ticketing, broadcasting, and analytics capabilities.

**Core Technical Approach**:
- Modular monolith backend (FastAPI) with clean module boundaries
- Multi-tenant data isolation via PostgreSQL Row-Level Security
- Real-time updates via WebSocket + Redis pub/sub
- AI agents via OpenAI Agents SDK with tool-based security
- Background workers (Celery) for async processing
- Next.js 16 frontend with App Router

---

## 🎯 Implementation Strategy: MVP-First Approach

> **IMPORTANT**: This plan represents the **FULL PLATFORM VISION** (22 weeks total). Implementation follows a phased approach with MVP first, then post-MVP features based on customer feedback.

### MVP Phase (8-10 weeks) - **CURRENT FOCUS**

Build core value proposition: Unified Inbox + AI Auto-Responses

**Phases to Execute**:
- ✅ **Phase 0**: Setup & Infrastructure (Week 1)
- ✅ **Phase 1**: Foundation (Database, Auth, Multi-tenancy) (Weeks 1-2)
- ✅ **Phase 2**: Unified Inbox + Real-time (Weeks 3-4)
- ✅ **Phase 3**: Channel Integration - **LIMITED SCOPE** (Weeks 5-7)
  - **MVP Channels Only**: WhatsApp Business API, Email (SMTP/API), Web Chat widget
  - **Defer to Post-MVP**: Instagram, Facebook Messenger, SMS
- ✅ **Phase 6**: AI System + Tool Functions (Weeks 8-10)
  - **Read-only tools only**: search_knowledge_base, get_contact_info, fetch_order_status
  - **NO write operations**: create_ticket, update_crm, send_broadcast (deferred)
- ✅ **Phase 7**: Knowledge Base (RAG) (Weeks 9-10)
- ✅ **Phase 8**: Workers (Message ingestion, AI execution) (Weeks 10-11)
- ✅ **Phase 10**: Hardening (Security, observability) (Week 12)

**MVP Deliverable**: Functional unified inbox with WhatsApp/Email/Web Chat + AI auto-responses grounded in knowledge base.

---

### Post-MVP Phases (12+ weeks) - **DEFERRED**

Expand platform with CRM, Ticketing, Broadcasts, and Voice based on customer feedback.

**Phases to Execute Later**:
- ⏸️ **Phase 4**: CRM + Tickets (Weeks 13-14)
  - Contact tagging, notes, lifecycle tracking
  - Support ticket system with SLA enforcement
- ⏸️ **Phase 5**: Broadcast Campaigns (Weeks 15-16)
  - Bulk messaging, audience segmentation, analytics
- ⏸️ **Phase 3 (Remaining Channels)**: Instagram, Facebook, SMS (Week 17)
- ⏸️ **Phase 9**: Voice + Analytics Dashboards (Weeks 18-20)
  - Twilio Voice API, call recording, transcription
  - Full analytics suite (FRT, ART, AI deflection, campaign performance)

**Rationale**: This phased approach allows us to:
1. Ship value quickly (8-10 weeks to MVP)
2. Validate core hypothesis (unified inbox + AI reduces response time)
3. Gather customer feedback before building advanced features
4. Avoid over-engineering features customers may not need

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)

**Primary Dependencies**:
- **Backend**: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Better Auth, Celery, OpenAI Agents SDK
- **Frontend**: Next.js 16 (App Router), React 18, Tailwind CSS, shadcn/ui
- **Databases**: PostgreSQL 15+ (Neon), Redis 7+
- **Channels**: WhatsApp Business API, Twilio (SMS/Voice), SendGrid/SMTP (Email)

**Storage**: PostgreSQL (structured data), S3-compatible object storage (media files, recordings), Redis (cache + queue + pub/sub)

**Testing**: pytest (Python), Vitest (TypeScript), Playwright (E2E)

**Target Platform**: Linux servers (Docker containers), scalable to Kubernetes

**Project Type**: Web application (backend/ + frontend/)

**Performance Goals**:
- <2s real-time message updates (excluding external API latency)
- <200ms API response time (p95)
- <5s AI response time (p95)
- 500 messages/second processing throughput
- 1000+ concurrent WebSocket connections per backend instance

**Constraints**:
- <200ms internal processing latency (per constitutional requirement)
- Multi-tenant isolation (100% - no cross-tenant data leaks)
- Horizontal scalability (stateless backend + workers)
- Zero-downtime migrations

**Scale/Scope**:
- 10,000 tenants (initial target)
- 100,000 messages/day per tenant (average)
- 50-500 concurrent agents per tenant
- 7 communication channels
- 4 AI agent types
- 23 database tables

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Implementation |
|-----------|-------------|--------|----------------|
| **I. Modular Monolith** | ONE FastAPI backend, NO microservices | ✅ PASS | Single backend with 10 internal modules |
| **II. Multi-Tenancy** | tenant_id on all tables, RLS policies | ✅ PASS | 21 tables with RLS, middleware enforcement |
| **III. Event-Driven Realtime** | WebSocket + DB events, replayable | ✅ PASS | All inbox events persisted before broadcast |
| **IV. AI Tool-Based** | AI via endpoints only, no direct DB | ✅ PASS | OpenAI Agents SDK with tool functions |
| **V. Channel Normalization** | Unified conversation/message schema | ✅ PASS | 7 channels mapped to standard models |
| **VI. Stateless Backend** | All state in PostgreSQL/Redis | ✅ PASS | No in-memory state, Redis pub/sub for WebSocket |
| **VII. Test-First** | TDD for critical paths (recommended) | ✅ PASS | Contract + integration tests for inbox, AI, broadcasts |
| **VIII. Observability** | Sentry + OpenTelemetry + logging | ✅ PASS | Error tracking, distributed tracing, structured logs |
| **IX. Security** | No secrets in code, .env + secret manager | ✅ PASS | Environment variables, encrypted credentials |
| **X. Versioning** | Zero-downtime migrations, API versions | ✅ PASS | Additive migrations, /api/v1 namespace |

**Overall**: ✅ **ALL GATES PASSED** - No constitutional violations

---

## Project Structure

### Documentation (this feature)

```text
specs/001-unified-comms-platform/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification with user stories
├── research.md          # Technology research and decisions
├── data-model.md        # Database schema (23 tables)
├── quickstart.md        # Developer setup guide
├── contracts/           # OpenAPI 3.0 API specifications
│   ├── auth-api.yaml
│   ├── inbox-api.yaml
│   ├── channels-api.yaml
│   ├── contacts-api.yaml
│   ├── tickets-api.yaml
│   ├── campaigns-api.yaml
│   ├── ai-api.yaml
│   ├── knowledge-api.yaml
│   └── analytics-api.yaml
├── checklists/
│   └── requirements.md  # Specification quality validation
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Structure Decision**: Web application (frontend + backend)

```text
backend/
├── src/
│   ├── core/                   # Shared infrastructure
│   │   ├── database.py         # SQLAlchemy async engine, sessions, RLS
│   │   ├── middleware.py       # Tenant context extraction
│   │   ├── config.py           # Environment configuration
│   │   └── websocket.py        # WebSocket manager with Redis pub/sub
│   ├── modules/                # Business logic modules
│   │   ├── auth/               # Authentication & authorization
│   │   │   ├── models.py       # User, Session, Role models
│   │   │   ├── schemas.py      # Pydantic request/response schemas
│   │   │   ├── router.py       # FastAPI routes (/auth/*)
│   │   │   ├── service.py      # Business logic
│   │   │   └── dependencies.py # Auth dependencies
│   │   ├── inbox/              # Unified inbox
│   │   ├── channels/           # Channel integrations
│   │   ├── contacts/           # CRM
│   │   ├── tickets/            # Support tickets
│   │   ├── campaigns/          # Broadcast campaigns
│   │   ├── ai/                 # AI agents
│   │   ├── knowledge/          # RAG knowledge base
│   │   ├── analytics/          # Metrics and dashboards
│   │   └── voice/              # Voice calls
│   ├── workers/                # Celery tasks
│   │   ├── message_processor.py
│   │   ├── ai_executor.py
│   │   ├── broadcast_sender.py
│   │   └── ...
│   ├── main.py                 # FastAPI application entry
│   └── celery.py               # Celery configuration
├── tests/
│   ├── contract/               # API contract tests
│   ├── integration/            # Cross-module workflow tests
│   └── unit/                   # Business logic unit tests
├── alembic/                    # Database migrations
├── requirements.txt
└── Dockerfile

frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Homepage
│   │   ├── (auth)/             # Auth route group
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── inbox/              # Inbox pages
│   │   ├── contacts/           # CRM pages
│   │   ├── tickets/            # Ticket pages
│   │   ├── campaigns/          # Campaign pages
│   │   ├── settings/           # Settings pages
│   │   └── analytics/          # Analytics pages
│   ├── components/             # Reusable React components
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── inbox/              # Inbox-specific components
│   │   ├── messages/           # Message composer, bubble
│   │   └── ...
│   ├── contexts/               # React contexts
│   │   ├── AuthContext.tsx
│   │   ├── WebSocketContext.tsx
│   │   └── TenantContext.tsx
│   ├── lib/                    # Utilities
│   │   ├── api.ts              # API client
│   │   └── utils.ts            # Helper functions
│   └── types/                  # TypeScript types
├── public/                     # Static assets
├── tests/                      # Frontend tests
├── package.json
└── Dockerfile

docker-compose.yml              # Local development setup
.env.example                    # Environment variable template
```

---

## Complexity Tracking

> **No violations** - All constitutional requirements satisfied without compromise.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Set up project infrastructure and core authentication

**Tasks**:
1. Initialize Next.js 16 frontend project (App Router, TypeScript, Tailwind, shadcn/ui)
2. Initialize FastAPI backend project (Python 3.11, async SQLAlchemy, Pydantic v2)
3. Set up PostgreSQL database (Neon) with Alembic migrations
4. Set up Redis instance (cache + queue + pub/sub)
5. Integrate Better Auth (session-based authentication, RBAC)
6. Create core database tables (tenants, users, sessions, roles)
7. Implement multi-tenant middleware (extract tenant_id, set PostgreSQL session variable)
8. Configure Docker Compose for local development
9. Set up environment configuration (.env management)
10. Implement global error handling and structured logging

**Acceptance Criteria**:
- User can register and login via frontend
- Session cookie stored securely (HttpOnly, Secure, SameSite)
- Multi-tenant middleware enforces tenant context
- PostgreSQL RLS policies active on all tenant-scoped tables
- Docker Compose starts all services (backend, frontend, PostgreSQL, Redis)

---

### Phase 2: Core Inbox (Weeks 3-4)

**Goal**: Build unified conversation system with real-time updates

**Tasks**:
1. Create conversations and messages tables
2. Implement WebSocket endpoint (`/ws`) with authentication
3. Set up Redis pub/sub for WebSocket horizontal scaling
4. Create inbox API endpoints (list conversations, get messages, send message)
5. Build frontend inbox UI (conversation list, message thread)
6. Implement real-time message updates (WebSocket push)
7. Add message status tracking (sent, delivered, read, failed)
8. Implement conversation assignment (user/team)
9. Add typing indicators
10. Create internal notes feature (agent-only messages)

**Acceptance Criteria**:
- Agent sees all conversations in unified inbox
- Sending message via UI → appears in both browser windows instantly (real-time)
- Message status updates appear without page refresh
- Typing indicators work across connected clients
- Conversations can be assigned to specific agents/teams

---

### Phase 3: Channel Integration (Weeks 5-7)

**Goal**: Connect WhatsApp, Email, SMS, Instagram, Facebook, Web Chat

> **MVP SCOPE**: For MVP (8-10 weeks), implement **WhatsApp, Email, and Web Chat only**. Defer Instagram, Facebook Messenger, and SMS to post-MVP phase based on customer demand.

**Tasks** (✅ = MVP | ⏸️ = Post-MVP):
1. ✅ Create channel_accounts table
2. ✅ Implement WhatsApp Business API integration (webhook + send API)
3. ✅ Implement Email integration (SMTP/IMAP + SendGrid API)
4. ⏸️ Implement Instagram Messaging API integration **(POST-MVP)**
5. ⏸️ Implement Facebook Messenger API integration **(POST-MVP)**
6. ⏸️ Implement SMS integration (Twilio) **(POST-MVP)**
7. ✅ Build web chat widget (embeddable JavaScript widget)
8. ✅ Create webhook ingestion endpoints for all channels
9. ✅ Implement message normalization (channel → unified schema)
10. ✅ Add channel-specific metadata handling (WhatsApp IDs, email headers)
11. ✅ Build channel management UI (connect/disconnect channels)
12. ✅ Implement webhook signature validation for security

**Acceptance Criteria** (MVP):
- ✅ Message sent on WhatsApp → appears in unified inbox with channel indicator
- ✅ Message sent from inbox → delivered via original channel
- ✅ WhatsApp, Email, Web Chat normalized to same conversation/message schema
- ✅ Channel connection UI allows easy setup
- ✅ Webhook signatures validated to prevent spoofing

**Acceptance Criteria** (Post-MVP):
- ⏸️ All 7 channels (including Instagram, Facebook, SMS) integrated

---

### Phase 4: CRM + Tickets (Weeks 13-14) ⏸️ **POST-MVP**

**Goal**: Add contact management and support ticket system

> **DEFERRED TO POST-MVP**: This phase will be implemented after MVP launch (Weeks 13-14) based on customer feedback. MVP includes basic contact auto-creation only.

**Tasks**:
1. Create contacts, contact_tags tables
2. Create tickets, ticket_history tables
3. Implement contact CRUD APIs
4. Implement contact tagging system
5. Build contact profile UI (conversation history, notes, tags)
6. Implement ticket creation from conversations
7. Build ticket lifecycle state machine (open → assigned → in_progress → resolved → closed)
8. Implement SLA tracking with deadline alerts
9. Add ticket escalation rules
10. Build ticket dashboard UI (list, filters, SLA compliance)
11. Implement ticket history audit trail

**Acceptance Criteria**:
- Contact auto-created when new message arrives
- Agent can add tags and notes to contacts
- Ticket created from conversation with SLA deadline
- System alerts when SLA deadline approaching
- Escalation rules trigger automatic reassignment
- Ticket history shows all state changes with timestamps

---

### Phase 5: Broadcast System (Weeks 15-16) ⏸️ **POST-MVP**

**Goal**: Enable bulk messaging campaigns

> **DEFERRED TO POST-MVP**: This phase will be implemented after MVP launch (Weeks 15-16) based on customer feedback and campaign feature demand.

**Tasks**:
1. Create campaigns, campaign_recipients tables
2. Implement campaign creation API (template, audience filter, schedule)
3. Build template editor UI with variable substitution ({{first_name}})
4. Implement audience segmentation logic (filter by tags, attributes)
5. Create Celery worker for broadcast sending (rate-limited per channel)
6. Implement campaign scheduling (future send times)
7. Add delivery tracking per recipient (sent, delivered, read, failed)
8. Build campaign analytics dashboard
9. Implement pause/resume/cancel campaign functionality
10. Add error handling for failed deliveries

**Acceptance Criteria**:
- User creates campaign with template targeting specific tags
- Campaign sends messages to all recipients in audience
- Rate limiting prevents API throttling (500 msg/sec for WhatsApp)
- Delivery status tracked per recipient
- Analytics show delivery rate, response rate in real-time
- User can pause campaign mid-send

---

### Phase 6: AI System (Weeks 8-10)

**Goal**: Implement AI agents with OpenAI Agents SDK

> **MVP SCOPE - READ-ONLY OPERATIONS ONLY**: AI agents can auto-reply and perform read-only operations (search knowledge base, fetch order status, retrieve contact info) but CANNOT create/modify data (tickets, CRM updates, broadcasts). Write operations require human approval (post-MVP enhancement).

**Tasks** (✅ = MVP | ⏸️ = Post-MVP):
1. ✅ Install OpenAI Agents SDK and configure API credentials
2. ✅ Create ai_configurations, ai_runs, ai_tool_calls tables
3. ✅ Define **read-only** tool functions:
   - `search_knowledge_base(query)` - Semantic search over RAG system
   - `get_contact_info(contact_id)` - Retrieve contact profile
   - `get_order_status(order_id)` - Fetch order information (if integrated)
4. ✅ Implement routing agent (classifies intent: support/sales/billing)
5. ✅ Implement support agent (answers product questions using RAG)
6. ⏸️ Implement sales agent (lead qualification, recommendations) **(POST-MVP)**
7. ⏸️ Implement billing agent (invoice inquiries, payment issues) **(POST-MVP)**
8. ✅ Configure handoffs between agents (routing → specialist → human)
9. ✅ Implement guardrails:
   - Input: profanity filter, prompt injection detection
   - Output: no unauthorized refunds, no off-brand responses
   - **Tool restriction**: Block all write operations (create_ticket, update_contact, send_broadcast)
10. ✅ Create Celery worker for AI execution
11. ✅ Build AI configuration UI (enable/disable agents, customize prompts, kill-switch)
12. ✅ Add AI run viewer (audit logs with prompts, tool calls, responses)
13. ✅ Implement human escalation flow (AI → agent takeover with full context)
14. ⏸️ Implement human-in-loop approval workflow for write actions **(POST-MVP)**

**Acceptance Criteria** (MVP):
- ✅ Customer message triggers routing agent to classify intent
- ✅ Routing agent hands off to support agent (sales/billing agents deferred)
- ✅ Support agent retrieves knowledge base context and provides accurate answer
- ✅ AI can ONLY perform read-only operations (no ticket creation, no CRM updates)
- ✅ AI escalates to human when uncertain or write operation requested
- ✅ All AI interactions logged in database
- ✅ Agent can view AI run details (prompts, tool calls, reasoning)
- ✅ Kill-switch allows instant AI disable per tenant or globally

**Acceptance Criteria** (Post-MVP):
- ⏸️ Sales and billing specialized agents implemented
- ⏸️ Human-in-loop approval for AI-suggested write operations (e.g., "Create ticket? [Approve/Reject]")

---

### Phase 7: Knowledge Base (Weeks 15-16)

**Goal**: Build RAG system for AI context

**Tasks**:
1. Install pgvector extension for PostgreSQL
2. Create knowledge_documents, knowledge_chunks tables
3. Implement document ingestion pipeline (PDF, text, URLs)
4. Implement text chunking (512 tokens with 50-token overlap)
5. Integrate OpenAI embeddings API (text-embedding-3-small)
6. Set up Chroma vector database (embedded mode)
7. Implement semantic search endpoint (vector similarity)
8. Build document upload UI (drag-and-drop, URL input)
9. Create document management view (list, preview, delete)
10. Implement versioning for document updates
11. Integrate knowledge base search into AI agent tools
12. Create Celery worker for async document processing

**Acceptance Criteria**:
- User uploads PDF → processed into chunks with embeddings
- Semantic search returns relevant chunks for queries
- AI agents receive knowledge base context in prompts
- AI responses grounded in knowledge base content
- Document version history tracked

---

### Phase 8: Workers (Weeks 10-11)

**Goal**: Implement all background workers and queue management

> **MVP SCOPE**: Implement workers for message ingestion, AI execution, and webhook processing. Defer broadcast and transcription workers to post-MVP.

**Tasks** (✅ = MVP | ⏸️ = Post-MVP):
1. ✅ Configure Celery with Redis broker and result backend
2. ✅ Set up task routing (different queues for different worker types)
3. ✅ Implement message processor worker (ingest, normalize, store)
4. ✅ Implement AI worker (execute AI runs)
5. ⏸️ Implement broadcast worker (send campaigns) **(POST-MVP - Phase 5)**
6. ✅ Implement webhook ingestion worker (process channel webhooks)
7. ✅ Implement email sync worker (IMAP polling every 30 seconds)
8. ⏸️ Implement transcription worker (speech-to-text for calls) **(POST-MVP - Phase 9)**
9. ⏸️ Implement scheduled jobs worker (SLA checks, campaign triggers, cleanup) **(POST-MVP - Phase 4/5)**
10. ✅ Implement retry handler worker (dead-letter queue for failed tasks)
11. ✅ Configure idempotency checks (prevent duplicate processing)
12. ✅ Set up Flower dashboard for worker monitoring
13. ✅ Implement graceful shutdown handling

**Acceptance Criteria** (MVP):
- ✅ Message ingestion and AI execution workers operational
- ✅ Workers scale horizontally (can add more instances)
- ✅ Failed tasks automatically retried with exponential backoff
- ✅ Idempotency prevents duplicate message processing
- ✅ Flower dashboard shows worker health and task queue depth

**Acceptance Criteria** (Post-MVP):
- ⏸️ Broadcast, transcription, and scheduled jobs workers implemented

---

### Phase 9: Voice + Analytics (Weeks 18-20) ⏸️ **POST-MVP**

**Goal**: Add voice calling and analytics dashboards

> **DEFERRED TO POST-MVP**: Voice calling deferred to Phase 3+ per spec.md clarifications. Basic analytics (FRT, ART) will be included in MVP; full analytics dashboards implemented post-MVP.

**Tasks**:
1. Create call_logs table
2. Integrate Twilio Voice API (inbound/outbound calls, recording, IVR)
3. Implement speech-to-text transcription (Twilio or OpenAI Whisper)
4. Create call log UI (history, recordings, transcripts)
5. Link call logs to contact profiles
6. Implement analytics queries (FRT, ART, ticket resolution time, SLA compliance, AI deflection rate, campaign performance, agent productivity)
7. Build analytics dashboards UI (charts, date range filters)
8. Implement data export (CSV/Excel)
9. Add real-time metrics (live dashboard updates)

**Acceptance Criteria**:
- Agent makes/receives calls through platform
- Call recordings automatically transcribed
- Transcripts linked to contact conversation timeline
- Analytics dashboards show accurate metrics
- FRT/ART calculated correctly
- AI deflection rate measures % of issues resolved without human

---

### Phase 10: Hardening (Weeks 21-22)

**Goal**: Production readiness (security, performance, observability)

**Tasks**:
1. Implement rate limiting per tenant/user
2. Add input validation and sanitization (prevent XSS, SQL injection)
3. Configure CSRF protection
4. Implement audit logging for critical actions
5. Set up Sentry error tracking with tenant context
6. Configure OpenTelemetry distributed tracing
7. Implement structured JSON logging with correlation IDs
8. Add slow query logging and monitoring
9. Optimize database indexes based on query patterns
10. Implement caching strategy (contact profiles, channel configs)
11. Create Docker production images (multi-stage builds)
12. Write deployment documentation
13. Set up CI/CD pipeline (tests, linting, migrations, deploy)
14. Perform security audit (dependency scanning, penetration testing)
15. Load testing (simulate 500 msg/sec, 1000 concurrent WebSocket connections)

**Acceptance Criteria**:
- Rate limiting prevents abuse (10 req/sec per user)
- All user input validated and sanitized
- Audit logs track who did what when
- Sentry captures errors with full context
- OpenTelemetry traces span API → Worker → AI → DB
- Database performs well under load (p95 < 200ms)
- Load testing confirms 500 msg/sec throughput

---

**Implementation Plan Complete**: 2026-06-21
**Next Step**: Execute `/sp.tasks` command to generate detailed task breakdown
**Status**: ✅ Ready for Implementation
