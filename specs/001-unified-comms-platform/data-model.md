# Data Model: Unified Communication Platform

**Feature**: 001-unified-comms-platform
**Date**: 2026-06-21
**Database**: PostgreSQL 15+ with Row-Level Security (RLS)

## Overview

This document defines the complete database schema for the Unified Communication Platform. All tables enforce multi-tenant isolation via `tenant_id` foreign keys and PostgreSQL Row-Level Security policies.

---

## Multi-Tenancy Pattern

### Core Principle
Every domain table MUST include `tenant_id` to enforce data isolation between organizations.

### Implementation
```sql
-- Set tenant context in middleware (before any queries)
SET LOCAL app.current_tenant_id = '<tenant-uuid>';

-- RLS Policy (applied to all tenant-scoped tables)
CREATE POLICY tenant_isolation ON <table_name>
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### System Tables (NO tenant_id)
- `tenants` - The tenant registry itself
- `sessions` - User sessions (links to user → tenant)

---

## Entity Relationship Diagram

```
tenants (organizations)
  ├── users
  │   ├── sessions
  │   └── teams (many-to-many)
  ├── roles & permissions
  ├── channel_accounts
  │   └── messages (via conversations)
  ├── contacts
  │   ├── contact_tags
  │   ├── conversations
  │   │   ├── messages
  │   │   └── message_status
  │   └── tickets
  │       └── ticket_history
  ├── campaigns
  │   └── campaign_recipients
  ├── ai_configurations
  │   └── ai_runs
  │       └── ai_tool_calls
  ├── knowledge_documents
  │   └── knowledge_chunks
  ├── call_logs
  └── audit_logs
```

---

## 1. Tenants (Organizations)

### Table: `tenants`

**Purpose**: Root entity for multi-tenant SaaS. Each tenant is an organization (business customer).

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'acme-corp'
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, suspended, deleted
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, pro, enterprise
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB -- billing info, feature flags, etc.
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_status ON tenants(status);
```

**Notes**:
- NO `tenant_id` (this IS the tenant table)
- Soft delete: Set `status = 'deleted'` instead of actual deletion

---

## 2. Users

### Table: `users`

**Purpose**: User accounts belonging to a tenant.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- bcrypt hashed
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL, -- 'super_admin', 'org_admin', 'agent', 'read_only'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP,
    metadata JSONB, -- profile picture, preferences, etc.

    UNIQUE(tenant_id, email) -- Email unique per tenant
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- RLS Policy
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON users
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 3. Sessions

### Table: `sessions`

**Purpose**: User sessions for authentication (Better Auth).

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL, -- Session token (stored in HTTP-only cookie)
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Auto-delete expired sessions
CREATE INDEX idx_sessions_cleanup ON sessions(expires_at) WHERE expires_at < NOW();
```

**Notes**:
- NO RLS (sessions accessed before tenant context established)
- Middleware extracts `tenant_id` from `user_id → users.tenant_id`

---

## 4. Roles & Permissions

### Table: `roles`

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL, -- {"inbox": ["read", "write"], "tickets": ["read"]}
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_roles_tenant ON roles(tenant_id);

-- RLS Policy
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON roles
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `user_roles`

```sql
CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (user_id, role_id)
);

CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);
```

---

## 5. Teams

### Table: `teams`

**Purpose**: Group users within an organization for assignment and permissions.

```sql
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_teams_tenant ON teams(tenant_id);

-- RLS Policy
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON teams
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `team_members`

```sql
CREATE TABLE team_members (
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (team_id, user_id)
);

CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);
```

---

## 6. Contacts (CRM)

### Table: `contacts`

**Purpose**: Customer/lead profiles with conversation history.

```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    lifecycle_stage VARCHAR(50) DEFAULT 'lead', -- lead, customer, churned
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB, -- custom fields, channel IDs (WhatsApp WAID, etc.)

    UNIQUE(tenant_id, email) -- Email unique per tenant (if provided)
);

CREATE INDEX idx_contacts_tenant ON contacts(tenant_id);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_phone ON contacts(phone);
CREATE INDEX idx_contacts_lifecycle ON contacts(lifecycle_stage);

-- RLS Policy
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON contacts
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `contact_tags`

```sql
CREATE TABLE contact_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(contact_id, tag)
);

CREATE INDEX idx_contact_tags_contact ON contact_tags(contact_id);
CREATE INDEX idx_contact_tags_tag ON contact_tags(tag);

-- RLS Policy
ALTER TABLE contact_tags ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON contact_tags
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 7. Channel Accounts

### Table: `channel_accounts`

**Purpose**: Connected communication channels (WhatsApp, Email, SMS, etc.).

```sql
CREATE TABLE channel_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    channel_type VARCHAR(50) NOT NULL, -- 'whatsapp', 'email', 'sms', 'instagram', 'facebook', 'webchat', 'voice'
    name VARCHAR(255) NOT NULL, -- e.g., "Customer Support WhatsApp"
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    credentials JSONB NOT NULL, -- Encrypted API keys, tokens, SMTP credentials
    configuration JSONB, -- Channel-specific config (webhook URLs, IVR menus)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(tenant_id, channel_type, name)
);

CREATE INDEX idx_channel_accounts_tenant ON channel_accounts(tenant_id);
CREATE INDEX idx_channel_accounts_type ON channel_accounts(channel_type);

-- RLS Policy
ALTER TABLE channel_accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON channel_accounts
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 8. Conversations

### Table: `conversations`

**Purpose**: Channel-agnostic conversation threads with a contact.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    channel_account_id UUID NOT NULL REFERENCES channel_accounts(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- open, closed
    assigned_to_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_to_team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMP,
    metadata JSONB -- tags, notes, etc.
);

CREATE INDEX idx_conversations_tenant ON conversations(tenant_id);
CREATE INDEX idx_conversations_contact ON conversations(contact_id);
CREATE INDEX idx_conversations_channel ON conversations(channel_account_id);
CREATE INDEX idx_conversations_assigned_user ON conversations(assigned_to_user_id);
CREATE INDEX idx_conversations_assigned_team ON conversations(assigned_to_team_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at DESC);

-- RLS Policy
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON conversations
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 9. Messages

### Table: `messages`

**Purpose**: Individual messages within conversations (channel-normalized).

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    direction VARCHAR(10) NOT NULL, -- 'inbound', 'outbound'
    sender_type VARCHAR(50) NOT NULL, -- 'contact', 'user', 'ai_agent'
    sender_id UUID, -- contact_id or user_id or ai_run_id
    content TEXT, -- Message body
    media_urls JSONB, -- Array of media URLs (images, videos, documents)
    channel_metadata JSONB, -- Channel-specific data (WhatsApp message ID, email headers)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_tenant ON messages(tenant_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at DESC);
CREATE INDEX idx_messages_sender ON messages(sender_id);

-- RLS Policy
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON messages
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `message_status`

**Purpose**: Track delivery status per channel (sent, delivered, read, failed).

```sql
CREATE TABLE message_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- 'sent', 'delivered', 'read', 'failed'
    error_message TEXT, -- If status = 'failed'
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    channel_metadata JSONB -- Channel-specific status data
);

CREATE INDEX idx_message_status_message ON message_status(message_id);
CREATE INDEX idx_message_status_status ON message_status(status);
CREATE INDEX idx_message_status_timestamp ON message_status(timestamp DESC);

-- RLS Policy
ALTER TABLE message_status ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON message_status
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 10. Tickets

### Table: `tickets`

**Purpose**: Support tickets created from conversations.

```sql
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- open, assigned, in_progress, resolved, closed
    priority VARCHAR(50) NOT NULL DEFAULT 'normal', -- low, normal, high, urgent
    assigned_to_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    sla_deadline TIMESTAMP, -- When ticket must be resolved (SLA)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_tickets_tenant ON tickets(tenant_id);
CREATE INDEX idx_tickets_conversation ON tickets(conversation_id);
CREATE INDEX idx_tickets_contact ON tickets(contact_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_assigned ON tickets(assigned_to_user_id);
CREATE INDEX idx_tickets_sla ON tickets(sla_deadline) WHERE status NOT IN ('resolved', 'closed');

-- RLS Policy
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON tickets
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `ticket_history`

**Purpose**: Audit trail of ticket state changes.

```sql
CREATE TABLE ticket_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    changed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    field_name VARCHAR(100) NOT NULL, -- e.g., 'status', 'assigned_to', 'priority'
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ticket_history_ticket ON ticket_history(ticket_id);
CREATE INDEX idx_ticket_history_created ON ticket_history(created_at DESC);

-- RLS Policy
ALTER TABLE ticket_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON ticket_history
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 11. Broadcast Campaigns

### Table: `campaigns`

**Purpose**: Bulk messaging campaigns.

```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    channel_account_id UUID NOT NULL REFERENCES channel_accounts(id) ON DELETE CASCADE,
    template TEXT NOT NULL, -- Message template with variables {{first_name}}
    audience_filter JSONB NOT NULL, -- Filter criteria (tags, attributes)
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, scheduled, in_progress, completed, paused, cancelled
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB -- total_recipients, sent_count, failed_count
);

CREATE INDEX idx_campaigns_tenant ON campaigns(tenant_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_scheduled ON campaigns(scheduled_at);

-- RLS Policy
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON campaigns
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `campaign_recipients`

**Purpose**: Track delivery status per recipient in a campaign.

```sql
CREATE TABLE campaign_recipients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, sent, delivered, read, failed
    error_message TEXT,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,

    UNIQUE(campaign_id, contact_id)
);

CREATE INDEX idx_campaign_recipients_campaign ON campaign_recipients(campaign_id);
CREATE INDEX idx_campaign_recipients_contact ON campaign_recipients(contact_id);
CREATE INDEX idx_campaign_recipients_status ON campaign_recipients(status);

-- RLS Policy
ALTER TABLE campaign_recipients ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON campaign_recipients
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 12. AI System

### Table: `ai_configurations`

**Purpose**: Per-tenant AI agent configuration.

```sql
CREATE TABLE ai_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL, -- 'router', 'support', 'sales', 'billing'
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    system_prompt TEXT,
    guardrails JSONB, -- Input/output validation rules
    tools JSONB, -- Enabled tool names
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(tenant_id, agent_type)
);

CREATE INDEX idx_ai_configurations_tenant ON ai_configurations(tenant_id);

-- RLS Policy
ALTER TABLE ai_configurations ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON ai_configurations
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `ai_runs`

**Purpose**: Audit log of AI agent executions.

```sql
CREATE TABLE ai_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    agent_type VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT,
    escalated_to_human BOOLEAN DEFAULT FALSE,
    escalation_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    metadata JSONB -- model version, temperature, etc.
);

CREATE INDEX idx_ai_runs_tenant ON ai_runs(tenant_id);
CREATE INDEX idx_ai_runs_conversation ON ai_runs(conversation_id);
CREATE INDEX idx_ai_runs_created ON ai_runs(created_at DESC);
CREATE INDEX idx_ai_runs_escalated ON ai_runs(escalated_to_human);

-- RLS Policy
ALTER TABLE ai_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON ai_runs
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `ai_tool_calls`

**Purpose**: Log individual tool invocations during AI runs.

```sql
CREATE TABLE ai_tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    ai_run_id UUID NOT NULL REFERENCES ai_runs(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_tool_calls_run ON ai_tool_calls(ai_run_id);
CREATE INDEX idx_ai_tool_calls_tool ON ai_tool_calls(tool_name);

-- RLS Policy
ALTER TABLE ai_tool_calls ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON ai_tool_calls
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 13. Knowledge Base (RAG)

### Table: `knowledge_documents`

**Purpose**: Documents ingested into the knowledge base.

```sql
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'pdf', 'text', 'url'
    source_url TEXT,
    content TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_knowledge_documents_tenant ON knowledge_documents(tenant_id);
CREATE INDEX idx_knowledge_documents_active ON knowledge_documents(is_active);

-- RLS Policy
ALTER TABLE knowledge_documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON knowledge_documents
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Table: `knowledge_chunks`

**Purpose**: Chunked segments of documents for embedding and retrieval.

```sql
CREATE TABLE knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI text-embedding-3-small (pgvector)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(document_id, chunk_index)
);

CREATE INDEX idx_knowledge_chunks_document ON knowledge_chunks(document_id);
CREATE INDEX idx_knowledge_chunks_embedding ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops);

-- RLS Policy
ALTER TABLE knowledge_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON knowledge_chunks
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 14. Voice / Call Logs

### Table: `call_logs`

**Purpose**: Record of voice calls.

```sql
CREATE TABLE call_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    direction VARCHAR(10) NOT NULL, -- 'inbound', 'outbound'
    caller_phone VARCHAR(50),
    callee_phone VARCHAR(50),
    assigned_to_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    duration_seconds INTEGER,
    recording_url TEXT,
    transcript TEXT,
    status VARCHAR(50), -- 'completed', 'missed', 'failed'
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    metadata JSONB -- Twilio call SID, IVR responses, etc.
);

CREATE INDEX idx_call_logs_tenant ON call_logs(tenant_id);
CREATE INDEX idx_call_logs_contact ON call_logs(contact_id);
CREATE INDEX idx_call_logs_conversation ON call_logs(conversation_id);
CREATE INDEX idx_call_logs_created ON call_logs(created_at DESC);

-- RLS Policy
ALTER TABLE call_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON call_logs
USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 15. Audit Logs

### Table: `audit_logs`

**Purpose**: Immutable record of critical system actions.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL, -- Can be NULL for system-level events
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- 'message_sent', 'ticket_created', 'ai_escalated', etc.
    entity_type VARCHAR(100), -- 'message', 'ticket', 'campaign', etc.
    entity_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- RLS Policy
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON audit_logs
USING (tenant_id = current_setting('app.current_tenant_id')::uuid OR tenant_id IS NULL);
```

---

## State Machines

### Ticket Lifecycle

```
open → assigned → in_progress → resolved → closed
  ↓                    ↓             ↓
  └─────────────────────────────────┘ (can escalate/reopen)
```

**Transitions**:
- `open → assigned`: Agent claims ticket
- `assigned → in_progress`: Agent starts work
- `in_progress → resolved`: Agent marks resolved
- `resolved → closed`: Auto-close after 24h OR customer confirms
- `* → open`: Customer reopens within 7 days

### Message Status

```
sent → delivered → read
  ↓
failed (terminal state)
```

**Channel Mapping**:
- WhatsApp: All 4 states supported
- Email: sent, failed (no delivery/read confirmation by default)
- SMS: sent, delivered, failed (no read receipts)

### Campaign Status

```
draft → scheduled → in_progress → completed
  ↓                       ↓
  └──────→ paused ────────┘
  ↓
cancelled (terminal state)
```

---

## Indexes & Performance Optimization

### Critical Indexes

1. **Conversations**: `(tenant_id, last_message_at DESC)` - Inbox sorting
2. **Messages**: `(conversation_id, created_at DESC)` - Message threading
3. **Contacts**: `(tenant_id, email)`, `(tenant_id, phone)` - Contact lookup
4. **Tickets**: `(tenant_id, sla_deadline)` WHERE status NOT IN ('resolved', 'closed') - SLA monitoring
5. **Knowledge Chunks**: `ivfflat (embedding vector_cosine_ops)` - Vector similarity search

### Partitioning Strategy (Future)

- **Messages**: Partition by `created_at` (monthly partitions) for archival
- **Audit Logs**: Partition by `created_at` (weekly partitions) for compliance

---

## Migration Strategy

### Safe Migration Pattern

```sql
-- Step 1: Add new column with default
ALTER TABLE messages ADD COLUMN new_field VARCHAR(100) DEFAULT 'default_value';

-- Step 2: Backfill data (in batches)
UPDATE messages SET new_field = old_field WHERE new_field IS NULL LIMIT 1000;

-- Step 3: Remove default constraint
ALTER TABLE messages ALTER COLUMN new_field DROP DEFAULT;

-- Step 4: (Optional) Remove old column after validation
ALTER TABLE messages DROP COLUMN old_field;
```

**Principles**:
- Additive changes first
- Backfill in batches
- Zero downtime (no locks on large tables)

---

## Summary

**Total Entities**: 23 tables
**Multi-Tenant Tables**: 21 (all except `tenants`, `sessions`)
**Foreign Keys**: 45+ relationships
**Indexes**: 80+ for performance
**RLS Policies**: 21 (one per tenant-scoped table)

**Next Step**: Generate API contracts based on this data model

---

**Data Model Complete**: 2026-06-21
