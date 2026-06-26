# Research: Unified Communication Platform

**Feature**: 001-unified-comms-platform
**Date**: 2026-06-21
**Status**: Complete

## Overview

This document captures all technology research, decisions, and rationale for building the Unified Communication Platform - a multi-tenant SaaS that unifies WhatsApp, Email, SMS, Instagram, Facebook Messenger, Web Chat, and Voice into a single AI-powered inbox.

---

## 1. Frontend Framework: Next.js 16 (App Router)

### Decision
Use **Next.js 16 with App Router** (not Pages Router) for the frontend dashboard and inbox UI.

### Rationale
- **App Router** provides better server-side rendering patterns for 2026
- Built-in support for React Server Components reduces client-side JavaScript
- File-based routing with layouts enables shared components (navbar, sidebar)
- Native TypeScript support without additional configuration
- Excellent developer experience with Fast Refresh

### Alternatives Considered
- **Vite + React**: Faster dev server but requires manual SSR setup, no built-in routing
- **Remix**: Good SSR but smaller ecosystem, less mature than Next.js
- **SvelteKit**: Excellent performance but team familiarity with React ecosystem

### Implementation Notes
- Use App Router structure: `app/` directory with `layout.tsx`, `page.tsx`
- Server Components for data fetching (conversations list, analytics)
- Client Components for interactive UI (message composer, real-time updates)
- Deploy to Node.js server (NOT Vercel) to support WebSocket connections

### References
- [Next.js App Router Patterns in 2026](https://pristren.com/blog/nextjs-app-router-patterns-2026/)
- [WebSockets with Next.js](https://websocket.org/guides/frameworks/nextjs/)

---

## 2. Backend Framework: FastAPI (Python 3.11)

### Decision
Use **FastAPI with Python 3.11** as a modular monolith (NOT microservices).

### Rationale
- **Async/await native**: Critical for handling concurrent WebSocket connections
- **Pydantic v2**: Built-in request/response validation with excellent performance
- **Auto-generated OpenAPI docs**: Interactive API documentation out-of-the-box
- **Type hints**: Python 3.11 type system enables better IDE support and fewer runtime errors
- **Modular structure**: Can organize as `modules/auth`, `modules/inbox`, etc. within single app

### Alternatives Considered
- **Django**: Mature but synchronous by default; Django Channels adds complexity
- **Flask**: Lightweight but requires many extensions; async support not native
- **Node.js (Express/Fastify)**: Good performance but Python ecosystem better for AI/ML integration

### Implementation Notes
- Structure: `backend/src/modules/{auth,inbox,channels,contacts,tickets,campaigns,ai,knowledge,analytics,voice}/`
- Each module has: `models.py`, `schemas.py`, `router.py`, `service.py`, `dependencies.py`
- Async database access with SQLAlchemy 2.0+ async engine
- CORS configuration for frontend (localhost:3000 in dev, production domain in prod)

### References
- [FastAPI Multi-Tenant SaaS: Row-Level Security](https://medium.com/@hjparmar1944/fastapi-multi-tenant-saas-row-level-security-without-pain-9ef960085bf4)

---

## 3. Database: PostgreSQL 15+ with Row-Level Security

### Decision
Use **PostgreSQL 15+** (Neon managed service recommended) with **Row-Level Security (RLS)** for multi-tenant isolation.

### Rationale
- **RLS**: Database-level enforcement of tenant isolation prevents application bugs from leaking data
- **JSONB**: Flexible schema for channel-specific metadata (WhatsApp message IDs, email headers)
- **pgvector extension**: Native vector storage for RAG embeddings (knowledge base)
- **Mature ecosystem**: Battle-tested for SaaS applications at scale
- **Neon**: Managed PostgreSQL with auto-scaling, branching for dev/staging/prod

### Alternatives Considered
- **MySQL**: Lacks RLS; weaker JSON support; no native vector extension
- **MongoDB**: No built-in RLS; eventual consistency risks for financial data (billing)
- **CockroachDB**: Excellent distributed SQL but overkill for initial scale; higher cost

### Implementation Notes
- Enable RLS on all tenant-scoped tables
- Set session variable `SET LOCAL app.current_tenant_id = <tenant_id>` in middleware
- RLS policy: `CREATE POLICY tenant_isolation ON conversations USING (tenant_id = current_setting('app.current_tenant_id')::uuid)`
- Use Alembic for migrations with safe patterns (additive changes, backfill, remove old columns)

### References
- [PostgreSQL Row-Level Security for Multi-Tenant SaaS](https://dev.to/software_mvp-factory/postgresql-row-level-security-for-multi-tenant-saas-1lgp)

---

## 4. Authentication: Better Auth (Session-Based)

### Decision
Use **Better Auth** with session-based authentication (HTTP-only cookies), NOT JWT.

### Rationale
- **Better Auth**: Modern, TypeScript-first auth library designed for Next.js + backend integration
- **Session-based**: More secure than JWT (can revoke sessions server-side, no token expiry issues)
- **HTTP-only cookies**: Immune to XSS attacks (JavaScript cannot access)
- **RBAC built-in**: Support for roles (Super Admin, Org Admin, Agent, Read-Only)
- **Organization/Team support**: Native multi-tenant user management

### Alternatives Considered
- **JWT tokens**: Cannot revoke without blacklist; vulnerable if XSS occurs; stateless but less secure
- **Auth0/Clerk**: Managed services but expensive at scale ($$$); vendor lock-in
- **NextAuth**: Good but tightly coupled to Next.js; harder to integrate with FastAPI backend

### Implementation Notes
- Store sessions in PostgreSQL `sessions` table (can move to Redis later for performance)
- Session cookie: `HttpOnly`, `Secure`, `SameSite=Lax`
- Middleware extracts `tenant_id` from session and sets PostgreSQL session variable
- Session TTL: 7 days idle, 30 days absolute

---

## 5. Cache & Queue: Redis

### Decision
Use **Redis** for caching, session storage (optional), and message broker for Celery workers.

### Rationale
- **Caching**: Frequently accessed data (contact profiles, channel configs) cached with TTL
- **Pub/Sub**: WebSocket horizontal scaling (broadcast events across backend instances)
- **Queue broker**: Celery task queue for background jobs (message processing, AI, broadcasts)
- **Session store**: Can migrate sessions from PostgreSQL to Redis for performance if needed
- **Single dependency**: One service handles cache + queue + pub/sub

### Alternatives Considered
- **Memcached**: Cache-only (no pub/sub, no queue support)
- **RabbitMQ**: Excellent queue but requires separate service; Redis simpler for early stage

### Implementation Notes
- Redis structure:
  - Cache: `cache:<entity>:<id>` with TTL (e.g., `cache:contact:123`)
  - Pub/Sub: Channel `inbox_updates:<tenant_id>` for WebSocket broadcasts
  - Celery: Queues `default`, `ai`, `broadcast`, `webhooks`, `transcription`
- Use `redis-py` with async support (`aioredis`)

---

## 6. Background Workers: Celery

### Decision
Use **Celery** with Redis broker for background job processing.

### Rationale
- **Mature**: Production-proven for millions of tasks/day
- **Horizontal scaling**: Add more worker instances as load increases
- **Task routing**: Different queues for different job types (priority, resource needs)
- **Retry logic**: Automatic retry with exponential backoff for transient failures
- **Monitoring**: Flower dashboard for worker health, queue depth, task history

### Alternatives Considered
- **RQ (Redis Queue)**: Simpler but lacks advanced features (task routing, complex retry logic)
- **Celery Beat**: Built-in cron-like scheduler for recurring tasks (SLA checks, campaign triggers)

### Worker Types
1. **Message Processing**: Ingest, normalize, store messages from channel webhooks
2. **AI Execution**: Run AI agents (OpenAI API calls can take 3-5 seconds)
3. **Broadcast Sending**: Send campaign messages with rate limiting
4. **Webhook Ingestion**: Process incoming webhooks from WhatsApp, Twilio, SendGrid
5. **Email/SMS Sync**: Poll IMAP, sync SMS provider APIs
6. **Voice Transcription**: Speech-to-text (CPU/GPU intensive)
7. **Scheduled Jobs**: SLA checks, campaign scheduling, cleanup
8. **Retry Handler**: Dead-letter queue processing

### Implementation Notes
- Worker command: `celery -A backend.celery worker --queues=ai,default -c 4`
- Concurrency: 4 workers per instance; scale horizontally by adding instances
- Idempotency: Use message ID as task ID to prevent duplicate processing

### References
- [Celery Python Tutorial 2026](https://tech-insider.org/celery-python-tutorial-task-queue-redis-2026/)

---

## 7. AI Framework: OpenAI Agents SDK

### Decision
Use **OpenAI Agents SDK** (Python) with tool calling, NOT LangChain.

### Rationale
- **Official SDK**: Maintained by OpenAI, guaranteed compatibility with API changes
- **Tool calling**: Native support for defining Python functions as tools
- **Handoffs**: Built-in agent-to-agent handoffs (router → support → human)
- **Guardrails**: Input/output validation, content filtering
- **Tracing**: Built-in observability for debugging AI decisions
- **Simpler**: Less abstraction than LangChain; easier to understand and debug

### Alternatives Considered
- **LangChain**: Feature-rich but complex; many abstraction layers; frequent breaking changes
- **Custom OpenAI API calls**: More control but requires implementing handoffs, guardrails manually

### Agent Architecture
- **Router Agent**: Classifies intent (support, sales, billing) → routes to specialist
- **Support Agent**: Answers product questions using knowledge base (RAG)
- **Sales Agent**: Lead qualification, product recommendations
- **Billing Agent**: Invoice inquiries, payment issues
- **Human Escalation**: When AI uncertain or customer requests human

### Implementation Notes
- Tool functions call FastAPI endpoints (e.g., `get_customer_orders`, `search_knowledge_base`)
- All AI runs logged in `ai_runs` table with prompts, tool calls, responses
- Guardrails: profanity filter on input, no unauthorized refunds on output
- Gemini API key used (user specified this in requirements)

### References
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Guardrails - OpenAI Agents SDK](https://openai.github.io/openai-agents-python/guardrails/)

---

## 8. Vector Database: Chroma (Embedded)

### Decision
Use **Chroma** (embedded mode) for RAG knowledge base, NOT managed Pinecone.

### Rationale
- **Embedded**: Runs in-process with backend (no separate service to manage)
- **PostgreSQL storage**: Chroma can use PostgreSQL as backend (aligns with stack)
- **Cost**: Free (vs Pinecone $70/month minimum)
- **OpenAI embeddings**: Native integration with `text-embedding-3-small`
- **Sufficient scale**: Handles millions of vectors (knowledge base won't exceed this initially)

### Alternatives Considered
- **Pinecone**: Managed service, excellent performance but $$$ expensive
- **Weaviate**: Self-hosted or cloud; more features but heavier deployment
- **pgvector**: PostgreSQL extension; simpler but less optimized for vector search at scale

### Implementation Notes
- Chroma collection: `knowledge_base_{tenant_id}` (tenant-scoped)
- Document chunking: 512 tokens with 50-token overlap
- Embedding model: `text-embedding-3-small` (1536 dimensions, $0.02/1M tokens)
- Top-k retrieval: 5 most relevant chunks injected into AI context

### References
- [RAG Architecture Guide 2026](https://jobsbyculture.com/blog/rag-architecture-guide-2026)
- [How to Build a RAG Pipeline in Python: 2026 Technical Guide](https://racine.ai/en/blog/build-rag-pipeline-python-2026/)

---

## 9. Channel Integrations

### WhatsApp Business API

**Decision**: Use **WhatsApp Business API** (Cloud API, not On-Premises)

**Rationale**:
- Cloud API: No server setup, Meta-hosted
- Webhooks: Real-time message delivery
- Template messages: Pre-approved for marketing (required for broadcasts)

**Implementation**:
- Webhook: `/webhooks/whatsapp` receives incoming messages
- Verify signature: `X-Hub-Signature-256` header validation
- Send API: `POST https://graph.facebook.com/v18.0/{phone_number_id}/messages`

**References**:
- [WhatsApp API 2026: Complete Integration Guide](https://www.unipile.com/whatsapp-api-a-complete-guide-to-integration/)

### Email (SMTP/API)

**Decision**: Support both SMTP and API providers (SendGrid, Mailgun)

**Rationale**:
- SMTP: Custom domain email (e.g., support@company.com)
- API providers: Better deliverability, analytics (open/click tracking)

**Implementation**:
- Inbound: IMAP polling every 30 seconds OR webhook (SendGrid Inbound Parse)
- Outbound: SMTP (via `aiosmtplib`) or API (SendGrid/Mailgun SDK)

### SMS Gateway

**Decision**: Use **Twilio** for SMS

**Rationale**:
- Global coverage (200+ countries)
- Programmable SMS API
- Webhook support for inbound SMS

**Implementation**:
- Webhook: `/webhooks/twilio/sms`
- Send API: Twilio Messaging Service

### Voice

**Decision**: Use **Twilio Voice** for calls

**Rationale**:
- IVR via TwiML (XML-based call flow)
- Call recording built-in
- SIP trunking for custom phone numbers

**Implementation**:
- Webhook: `/webhooks/twilio/voice` (TwiML response)
- Recording: Auto-transcribe with Whisper API

---

## 10. Real-Time Architecture: WebSocket + Redis Pub/Sub

### Decision
Use **FastAPI WebSocket** with **Redis Pub/Sub** for horizontal scaling.

### Rationale
- **WebSocket**: Native support in FastAPI (no separate service)
- **Redis Pub/Sub**: Broadcast events to all backend instances
- **Scalability**: Add more backend instances; Redis ensures all receive events
- **Event sourcing**: Events stored in DB before broadcast (replay capability)

### Implementation
- Frontend: `WebSocketContext` React context provider connects to `/ws`
- Backend: WebSocket endpoint validates session, subscribes to Redis channel `inbox_updates:<tenant_id>`
- Event flow:
  1. Message arrives → stored in DB
  2. Event emitted to Redis: `PUBLISH inbox_updates:<tenant_id> {type: "new_message", ...}`
  3. All backend instances subscribed to channel receive event
  4. Each instance broadcasts to connected WebSocket clients for that tenant

### Event Types
- `new_message`: New message in conversation
- `message_status_update`: Delivered, read, failed
- `ticket_update`: Ticket state change
- `assignment_change`: Conversation assigned to agent
- `ai_response_stream`: AI typing indicator + streaming response

---

## 11. Observability: Sentry + OpenTelemetry + Structured Logging

### Decision
Use **Sentry** for errors, **OpenTelemetry** for traces, **JSON logging** for structured logs.

### Rationale
- **Sentry**: Error tracking with stack traces, tenant context, breadcrumbs
- **OpenTelemetry**: Distributed tracing (API → Worker → AI → DB)
- **JSON logs**: Machine-readable, correlation IDs link frontend → backend → worker

### Implementation
- Sentry: Capture exceptions with `tenant_id`, `user_id`, `conversation_id` tags
- OpenTelemetry: Trace spans for API requests, Celery tasks, AI calls, DB queries
- Logging: `structlog` with correlation ID propagated through headers

---

## 12. Deployment: Docker + Docker Compose (Dev) → Kubernetes (Prod)

### Decision
Use **Docker** for containerization, **Docker Compose** for local dev, scale to **Kubernetes** later.

### Rationale
- **Docker**: Consistent environments (dev = prod)
- **Docker Compose**: Simple local setup (backend + frontend + PostgreSQL + Redis + workers)
- **Kubernetes**: Production scaling (horizontal pod autoscaling, rolling updates)

### Implementation
- Dockerfile: Multi-stage builds (separate build + runtime images)
- Docker Compose: `docker-compose.yml` with services: `backend`, `frontend`, `postgres`, `redis`, `worker`
- Kubernetes: Helm charts for deployment (future)

---

## Summary of Key Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend | Next.js 16 (App Router) | SSR, React Server Components, TypeScript |
| Backend | FastAPI (Python 3.11) | Async, Pydantic validation, modular monolith |
| Database | PostgreSQL 15+ (Neon) | RLS for multi-tenancy, pgvector, JSONB |
| Auth | Better Auth | Session-based, RBAC, organization support |
| Cache/Queue | Redis | Cache + Celery broker + WebSocket pub/sub |
| Workers | Celery | Mature, horizontal scaling, task routing |
| AI | OpenAI Agents SDK | Tool calling, handoffs, guardrails, tracing |
| Vector DB | Chroma (embedded) | Free, PostgreSQL-backed, OpenAI embeddings |
| Channels | WhatsApp (Cloud API), Twilio (SMS/Voice), SMTP/API (Email) | Official APIs, webhook support |
| Real-Time | WebSocket + Redis Pub/Sub | Native FastAPI, horizontal scaling |
| Observability | Sentry + OpenTelemetry | Error tracking, distributed tracing |
| Deployment | Docker + Docker Compose → Kubernetes | Consistent environments, scalable |

---

**Research Complete**: 2026-06-21
**Next Step**: Proceed to data model design and API contract definition
