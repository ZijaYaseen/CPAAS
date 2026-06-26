<!--
Sync Impact Report:
Version: 1.0.0 (initial ratification)
Ratification Date: 2026-06-21
Modified Principles: N/A (initial version)
Added Sections: All sections (initial creation)
Removed Sections: None
Templates requiring updates:
  ✅ plan-template.md - reviewed for constitution alignment
  ✅ spec-template.md - reviewed for requirements alignment
  ✅ tasks-template.md - reviewed for principle-driven task types
Follow-up TODOs: None
-->

# Unified Communication Platform Constitution

## Core Principles

### I. Modular Monolith Architecture (NON-NEGOTIABLE)

**Rule**: The system MUST be built as a single modular monolith backend with clean module boundaries, NOT as microservices.

**Requirements**:
- ONE FastAPI backend application with clearly separated internal modules
- MULTIPLE worker processes for async/background tasks (Celery/RQ)
- Clean module boundaries with explicit interfaces between domains
- Each module operates as if it could be extracted later, but deployed together initially
- No inter-service HTTP calls; all communication via direct Python imports or message queues

**Rationale**: Microservices introduce unnecessary operational complexity, network latency, distributed transaction challenges, and debugging difficulties at early stages. A modular monolith provides the same organizational benefits (clear boundaries, independent development) while maintaining deployment simplicity, atomic transactions, and simplified debugging. This approach allows future extraction into services only when scale demands it.

### II. Multi-Tenancy & Data Isolation (NON-NEGOTIABLE)

**Rule**: Every data access MUST enforce tenant isolation at the database layer.

**Requirements**:
- All domain tables include a `tenant_id` foreign key
- Database queries MUST filter by tenant context automatically (middleware/ORM level)
- Row-level security policies where supported by PostgreSQL
- Sessions and authentication MUST establish tenant context before any data access
- No shared data between tenants except system-level configuration

**Rationale**: Multi-tenant SaaS platforms require absolute data isolation to prevent data leaks, ensure compliance (GDPR, SOC2), and maintain customer trust. Database-level enforcement prevents application bugs from causing cross-tenant data exposure.

### III. Event-Driven Realtime Architecture

**Rule**: All inbox state changes MUST be event-driven, WebSocket-pushed, and database-persisted.

**Requirements**:
- Message arrivals, status updates, typing indicators, assignments → emit events
- Events stored in database (audit log) before WebSocket broadcast
- WebSocket clients receive real-time updates for their tenant/user scope
- Events must be replayable (new client connections can reconstruct current state)
- No polling for inbox updates; clients subscribe via WebSocket

**Rationale**: A unified inbox handling multiple channels (WhatsApp, Email, Instagram, etc.) requires instantaneous updates to maintain user experience and prevent message handling conflicts. Event sourcing ensures audit trails and enables features like conversation replay, analytics, and debugging.

### IV. AI Tool-Based Architecture (Security-First)

**Rule**: AI agents MUST NEVER directly access the database; all operations via defined tools calling FastAPI endpoints.

**Requirements**:
- AI agents use OpenAI Agents SDK with tool definitions
- Each tool maps to a specific FastAPI endpoint with authentication/authorization
- All AI runs logged in `ai_runs` table with tool calls, inputs, outputs, timestamps
- Human escalation always available; AI never makes irreversible decisions without approval gates
- Guardrails defined for each agent type (routing, sales, support)
- Tracing enabled for debugging AI decision paths

**Rationale**: Direct database access by AI creates uncontrollable security risks, bypasses business logic/validation, and makes debugging impossible. Tool-based architecture ensures all AI actions go through the same validated, authorized, auditable paths as human actions, while enabling observability and kill-switches.

### V. Channel Normalization & Abstraction

**Rule**: All communication channels MUST be normalized into a unified conversation/message model.

**Requirements**:
- Channels (WhatsApp, Email, Instagram, Facebook, SMS, Web Chat, Voice) mapped to standard schema
- `conversations` table agnostic to channel type; `channel_id` references specific integration
- Message format normalized: sender, recipient, content, media attachments, timestamps
- Channel-specific metadata stored separately but linked (e.g., WhatsApp message IDs, email headers)
- Unified inbox UI renders all channels consistently

**Rationale**: Users managing multiple communication channels need a single interface to track conversations regardless of origin. Normalization enables cross-channel analytics, unified search, consistent AI behavior, and simplified agent workflows.

### VI. Stateless Backend & Horizontal Scalability

**Rule**: The backend application MUST be stateless; all state stored in PostgreSQL or Redis.

**Requirements**:
- No in-memory session storage; sessions in Redis or database
- No server-side file storage; use S3-compatible object storage
- WebSocket connections managed via Redis pub/sub for multi-instance deployments
- Workers horizontally scalable (more Celery workers = more throughput)
- Database connections pooled; no process-local caches that break with multiple instances

**Rationale**: SaaS platforms require the ability to scale horizontally (add more backend instances) to handle growth. Stateless design enables load balancing, rolling deployments without downtime, and cloud-native scaling patterns.

### VII. Test-First for Critical Paths (Strongly Recommended)

**Rule**: Critical user journeys (message delivery, AI escalation, broadcast sending) SHOULD follow TDD.

**Requirements**:
- Tests written BEFORE implementation for high-risk features (payment, security, data integrity)
- Integration tests for cross-module workflows (e.g., WhatsApp message → AI response → human escalation)
- Contract tests for FastAPI endpoints used by AI tools
- Unit tests for business logic functions
- Fixtures for multi-tenant test isolation

**Rationale**: Communication platforms have high reliability expectations (message loss = customer loss). TDD ensures critical paths work correctly before code reaches production, reducing post-deployment firefighting.

### VIII. Observability & Incident Response

**Rule**: All production errors, slow queries, and AI decisions MUST be traceable.

**Requirements**:
- Sentry for error tracking with tenant/user context
- OpenTelemetry traces for request flows (API → worker → AI → database)
- Structured logging (JSON) with correlation IDs linking frontend → backend → worker
- Slow query logging enabled; p95 latency monitored
- AI decision logs include full prompt, tool calls, and reasoning for audit

**Rationale**: Debugging multi-tenant, multi-channel, AI-powered systems requires deep observability. When a customer reports "my message didn't send," engineers need to trace the exact path (which channel, which worker, which AI decision) to diagnose root cause.

### IX. Security & Secrets Management

**Rule**: No secrets in code, environment variables loaded from `.env` (local) or secret managers (production).

**Requirements**:
- API keys (WhatsApp, SendGrid, Twilio, OpenAI) stored in environment variables or secret manager
- Database credentials never hardcoded
- Better Auth configured with secure session cookies (HTTP-only, Secure, SameSite)
- CORS policies restrict frontend origins
- Rate limiting on all public endpoints
- Input validation and sanitization for all user-provided content (prevent XSS, SQL injection)

**Rationale**: Communication platforms handle sensitive customer data (messages, contact info, call recordings). A single leaked API key or SQL injection vulnerability can expose entire tenant databases or enable account takeovers.

### X. Backward Compatibility & Versioning

**Rule**: Database schema changes MUST support zero-downtime migrations; API changes MUST be versioned.

**Requirements**:
- Migrations use additive changes (add columns with defaults, backfill, then remove old columns)
- No breaking API changes without version bumps (`/api/v1`, `/api/v2`)
- Frontend and backend deployments decoupled (backend can deploy without frontend redeployment)
- Feature flags for gradual rollouts and kill-switches

**Rationale**: SaaS platforms serve live customers 24/7. Breaking changes cause downtime and erode trust. Versioning and migration strategies enable continuous deployment without customer-facing disruptions.

## Technology Stack (LOCKED)

**Frontend**:
- Next.js 16+ (App Router) with TypeScript
- Tailwind CSS for styling
- shadcn/ui component library

**Backend**:
- Python FastAPI (single modular monolith)
- REST + WebSocket support

**Authentication**:
- Better Auth with session-based authentication (HTTP-only cookies)
- Database-backed sessions (PostgreSQL or Redis)

**Database**:
- PostgreSQL (Neon recommended for managed hosting)
- Multi-tenant schema design with `tenant_id` on all domain tables

**Cache & Queue**:
- Redis for caching, session storage, and message broker (Celery)

**Workers**:
- Celery (or RQ) for background job processing
- Separate worker types: message processing, AI responses, broadcasts, webhooks, email/SMS sync, voice transcription, scheduled jobs, retry handling

**AI Layer**:
- OpenAI Agents SDK (Python) with tools, handoffs, guardrails, and tracing

**Realtime**:
- WebSockets (FastAPI native) for live inbox updates, typing indicators, delivery status

**Storage**:
- S3-compatible object storage for media attachments (images, videos, voice recordings, documents)

**Observability**:
- Sentry for error tracking
- OpenTelemetry for distributed tracing
- Structured logging (JSON format)

**Deployment**:
- Docker-based services (backend container + worker container)
- Scalable to Kubernetes later if needed

**Rationale**: This stack balances developer productivity (Python FastAPI, Next.js), operational maturity (PostgreSQL, Redis, Celery), and modern best practices (TypeScript, WebSockets, OpenTelemetry). All components are production-proven for SaaS platforms at scale.

## Core Modules (Backend Architecture)

The backend is organized into the following internal modules (within a single FastAPI application):

1. **Auth & Identity**: Users, organizations, teams, roles, permissions, sessions (Better Auth integration)
2. **Unified Inbox**: Conversations, messages, channel normalization, assignment system
3. **Channel Integrations**: WhatsApp API, Email SMTP/API, Instagram/Facebook messaging, SMS gateway, web chat widget, voice/call system
4. **CRM / Contacts**: Leads, customers, tags, notes, contact history
5. **Ticket / Complaint System**: Ticket lifecycle, SLA tracking, escalation workflows
6. **Broadcast System**: Campaigns, templates, bulk messaging, scheduling
7. **AI Agent System**: Auto-replies, routing agent, sales agent, support agent, human escalation, OpenAI Agents SDK integration
8. **Knowledge Base (RAG)**: Documents, FAQs, embeddings, semantic search for AI context
9. **Analytics**: Response time metrics, conversion tracking, agent performance, campaign statistics
10. **Voice Module**: Call logs, speech-to-text, text-to-speech, IVR support

**Module Boundaries**: Each module has a dedicated Python package (`backend/src/modules/<module_name>`) with:
- `models.py` (SQLAlchemy models)
- `schemas.py` (Pydantic request/response schemas)
- `router.py` (FastAPI routes)
- `service.py` (business logic)
- `dependencies.py` (dependency injection for auth, tenant context, etc.)

## Worker Services

Background tasks are handled by separate worker processes (Celery workers):

1. **Message Processing Worker**: Ingest incoming messages from channels, normalize, store, trigger AI if needed
2. **AI Response Worker**: Execute AI agent runs (call OpenAI Agents SDK, log runs, update conversations)
3. **Broadcast Sender Worker**: Send bulk messages via channels (rate-limited, retry logic)
4. **Webhook Ingestion Worker**: Process incoming webhooks from WhatsApp, Twilio, SendGrid, etc.
5. **Email/SMS Sync Worker**: Poll email IMAP/SMTP, sync SMS provider APIs
6. **Voice Transcription Worker**: Convert call recordings to text using speech-to-text
7. **Scheduled Jobs Worker**: Cron-like tasks (SLA checks, campaign scheduling, cleanup)
8. **Retry/Failure Handler Worker**: Dead-letter queue processing for failed tasks

## Database Design (Required Tables)

The database schema MUST include (at minimum):

- `tenants` (organization-level isolation)
- `sessions` (Better Auth session storage)
- `users` (with `tenant_id`, roles, teams)
- `conversations` (channel-agnostic conversation threads)
- `messages` (normalized messages with `conversation_id`, `channel_id`)
- `message_status` (delivery, read, failed statuses per channel)
- `channels` (WhatsApp, Email, Instagram, etc., with credentials per tenant)
- `contacts` (leads, customers, linked to `tenant_id`)
- `tickets` (support tickets with SLA tracking)
- `broadcasts` (campaign definitions)
- `campaigns` (scheduled/sent broadcasts)
- `ai_runs` (AI agent execution logs with tool calls, prompts, outputs)
- `tool_calls` (individual AI tool invocations linked to `ai_runs`)
- `knowledge_base` (documents, FAQs, embeddings for RAG)
- `audit_logs` (all critical actions: message sends, AI escalations, user changes)

All domain tables include `tenant_id` foreign key (except system tables like `tenants` itself).

## Development Workflow

### Code Quality Standards

- **Type Safety**: All Python code uses type hints; MyPy enforced in CI
- **Linting**: Ruff (Python), ESLint (TypeScript) with pre-commit hooks
- **Formatting**: Black (Python), Prettier (TypeScript)
- **Security Scanning**: Bandit (Python), npm audit (Node.js dependencies)

### Testing Requirements

- **Unit Tests**: Business logic functions (services, utilities)
- **Integration Tests**: Cross-module workflows (message ingestion → AI response)
- **Contract Tests**: FastAPI endpoints used by AI tools (ensure tool definitions match API)
- **End-to-End Tests**: Critical user journeys (send message, receive reply, escalate to human)

### Deployment Process

1. **Local Development**: Docker Compose with backend, frontend, PostgreSQL, Redis, Celery workers
2. **Staging**: Deployed to staging environment (separate database, same architecture)
3. **Production**: Docker-based deployment (backend container, worker container pool)
4. **Rollback Strategy**: Database migrations use safe patterns (additive changes); container rollback via orchestration

## Governance

### Amendment Process

1. Proposed changes to this constitution MUST be documented in a Pull Request
2. Changes require approval from project maintainers
3. MAJOR version bump (e.g., 1.x.x → 2.0.0) for backward-incompatible principle changes (e.g., switching from monolith to microservices)
4. MINOR version bump (e.g., 1.0.x → 1.1.0) for new principles or materially expanded guidance
5. PATCH version bump (e.g., 1.0.0 → 1.0.1) for clarifications, wording fixes, non-semantic refinements

### Compliance Reviews

- All Pull Requests MUST verify compliance with principles (architecture, multi-tenancy, security, observability)
- Code reviews MUST check for:
  - Tenant ID enforcement in all queries
  - No hardcoded secrets
  - AI tools calling FastAPI endpoints (not direct DB access)
  - Event emission for realtime updates
  - Stateless backend patterns (no in-memory state)

### Complexity Justification

Any deviation from principles (e.g., introducing a second backend service, adding microservices) MUST document:
- Why the deviation is necessary (specific business/technical constraint)
- Why simpler alternatives were rejected
- Migration plan to return to compliance if temporary

### Runtime Guidance

Developers MUST refer to `CLAUDE.md` for detailed development practices, AI agent interaction patterns, and operational procedures aligned with this constitution.

---

**Version**: 1.0.0 | **Ratified**: 2026-06-21 | **Last Amended**: 2026-06-21
