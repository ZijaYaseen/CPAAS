# Feature Specification: Unified Communication Platform

**Feature Branch**: `001-unified-comms-platform`
**Created**: 2026-06-21
**Status**: Draft
**Input**: User description: "Unified Communication Platform (Convex-like UCaaS + AI Agent System)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Channel Inbox Management (Priority: P1)

As a support agent, I need to view and respond to customer messages from all communication channels in a single unified inbox, so that I can efficiently manage conversations without switching between multiple platforms.

**Why this priority**: This is the core value proposition of the platform. Without a unified inbox, the system provides no unique value over using individual channel apps.

**Independent Test**: Can be fully tested by connecting at least one channel (e.g., WhatsApp), receiving messages, and sending replies through the unified interface. Delivers immediate value by centralizing communication.

**Acceptance Scenarios**:

1. **Given** a message arrives on WhatsApp, **When** the agent opens the inbox, **Then** the message appears in the unified conversation thread with channel indicator
2. **Given** multiple messages from different channels (Email, SMS, WhatsApp), **When** the agent views the inbox, **Then** all conversations are displayed in a single list with channel icons
3. **Given** an agent selects a conversation, **When** they type and send a reply, **Then** the message is delivered through the original channel and status is tracked
4. **Given** a message is delivered, **When** the customer reads it, **Then** the inbox updates the message status to "read" in real-time
5. **Given** an ongoing conversation, **When** the customer starts typing, **Then** the agent sees a typing indicator in real-time

---

### User Story 2 - AI-Powered Auto-Responses (Priority: P2)

As a business owner, I need AI agents to automatically respond to common customer inquiries (support, sales, billing) and escalate complex issues to human agents, so that I can provide 24/7 customer service without hiring night-shift staff.

**Why this priority**: AI automation is a key differentiator but depends on the inbox infrastructure from P1. Provides immediate ROI by reducing agent workload.

**Independent Test**: Can be tested by configuring an AI agent, sending test messages matching known intents (e.g., "What are your hours?"), verifying auto-responses, and confirming escalation for unknown queries. Delivers value by handling repetitive questions automatically.

**Acceptance Scenarios**:

1. **Given** an AI agent is configured with knowledge base, **When** a customer asks a common question, **Then** the AI responds automatically within 5 seconds
2. **Given** an AI-handled conversation, **When** the customer asks a question the AI cannot answer, **Then** the conversation is escalated to a human agent with full context
3. **Given** multiple AI agent types (support, sales, billing), **When** a message arrives, **Then** the routing agent determines intent and assigns to the correct specialized agent
4. **Given** an AI is responding, **When** a human agent takes over, **Then** the AI stops responding and logs the handoff
5. **Given** an AI interaction, **When** it completes, **Then** the full conversation (prompts, tool calls, responses) is logged for audit

---

### User Story 3 - Broadcast Campaign Management (Priority: P3)

As a marketing manager, I need to send bulk messages to segmented customer lists across multiple channels with scheduled delivery and delivery tracking, so that I can run targeted campaigns without manual individual messaging.

**Why this priority**: Broadcast capability is valuable but requires inbox and contact management first. Provides business growth through marketing automation.

**Independent Test**: Can be tested by creating a contact list, designing a template message, scheduling a campaign, and verifying delivery tracking. Delivers value by enabling one-to-many communication.

**Acceptance Scenarios**:

1. **Given** a contact list with tags, **When** a marketing manager creates a campaign targeting specific tags, **Then** the system queues messages for only those contacts
2. **Given** a campaign with a scheduled send time, **When** the time arrives, **Then** messages are sent in batches respecting channel rate limits
3. **Given** a broadcast message, **When** recipients receive it, **Then** delivery status (sent, delivered, read, failed) is tracked per recipient
4. **Given** a campaign in progress, **When** the manager views analytics, **Then** they see real-time delivery statistics and response rates
5. **Given** a template with variables (e.g., {{first_name}}), **When** the campaign sends, **Then** each message is personalized with recipient data

---

### User Story 4 - Ticket and Complaint Tracking (Priority: P4)

As a support manager, I need to convert customer complaints into tracked tickets with SLA deadlines, priority levels, and escalation rules, so that I can ensure no customer issue is lost or forgotten.

**Why this priority**: Ticket system builds on inbox foundation (P1) and provides structure for support operations. Critical for enterprise customers with compliance requirements.

**Independent Test**: Can be tested by creating a ticket from a conversation, setting SLA and priority, tracking lifecycle changes, and verifying escalation triggers. Delivers value through accountability and visibility.

**Acceptance Scenarios**:

1. **Given** a customer conversation, **When** an agent creates a ticket, **Then** the ticket is linked to the conversation with lifecycle state "open"
2. **Given** a ticket with an SLA deadline, **When** the deadline approaches, **Then** the system sends alerts to assigned agent and manager
3. **Given** a ticket breaches SLA, **When** escalation rules trigger, **Then** the ticket is reassigned to a senior agent or manager
4. **Given** a ticket is resolved, **When** the agent closes it, **Then** the customer receives a resolution confirmation and can reopen if unsatisfied
5. **Given** multiple tickets, **When** a manager views the dashboard, **Then** they see ticket volume, average resolution time, and SLA compliance metrics

---

### User Story 5 - CRM and Contact Management (Priority: P5)

As a sales agent, I need to view complete customer history (past conversations, notes, tags, lifecycle stage) in a unified profile, so that I can personalize interactions and track leads through the sales pipeline.

**Why this priority**: CRM enhances agent effectiveness but requires inbox and data infrastructure first. Provides long-term value through customer relationship insights.

**Independent Test**: Can be tested by creating a contact profile, adding tags and notes, viewing conversation timeline, and tracking lead progression. Delivers value through customer context and sales pipeline visibility.

**Acceptance Scenarios**:

1. **Given** a new customer contacts the business, **When** they send their first message, **Then** a contact profile is auto-created with channel info
2. **Given** a contact profile, **When** an agent adds tags or notes, **Then** the information is immediately visible to all team members
3. **Given** a contact with multiple conversations across channels, **When** an agent opens the profile, **Then** all conversations are displayed in chronological order
4. **Given** a lead in the sales pipeline, **When** the agent updates their stage, **Then** the CRM tracks progression and displays funnel analytics
5. **Given** a contact list, **When** the manager segments by tags or attributes, **Then** the system creates dynamic lists for targeting

---

### User Story 6 - Voice Communication and Transcription (Priority: P6)

As a support agent, I need to make and receive voice calls directly through the platform with automatic transcription and call logs, so that I can handle phone support without leaving the unified inbox.

**Why this priority**: Voice integration completes the omnichannel vision but is complex and depends on all previous infrastructure. Provides full communication coverage.

**Independent Test**: Can be tested by making a test call, verifying call log creation, checking transcription accuracy, and confirming integration with the inbox. Delivers value by eliminating need for separate phone systems.

**Acceptance Scenarios**:

1. **Given** a customer calls the business number, **When** the call connects, **Then** the agent sees caller ID and previous conversation history in real-time
2. **Given** an active call, **When** the conversation ends, **Then** the call is recorded, transcribed, and added to the customer's timeline
3. **Given** a call recording, **When** speech-to-text processing completes, **Then** the transcript is searchable and linked to the call log
4. **Given** an IVR menu, **When** a customer selects an option, **Then** the system routes the call to the appropriate agent or queue
5. **Given** a missed call, **When** the call log is created, **Then** the system creates a callback task assigned to an agent

---

### User Story 7 - Analytics and Performance Monitoring (Priority: P7)

As a business owner, I need dashboards showing response times, resolution rates, AI deflection, campaign performance, and agent productivity, so that I can identify bottlenecks and optimize operations.

**Why this priority**: Analytics provides business intelligence but requires operational data from all other features. Provides long-term value through data-driven optimization.

**Independent Test**: Can be tested by generating sample data across modules (messages, tickets, campaigns, AI runs), viewing dashboards, and verifying metric accuracy. Delivers value through operational visibility.

**Acceptance Scenarios**:

1. **Given** historical conversation data, **When** a manager views the analytics dashboard, **Then** they see first response time (FRT) and average response time (ART) trends
2. **Given** ticket data, **When** filtering by date range, **Then** the system displays resolution time, SLA compliance percentage, and escalation rates
3. **Given** AI interactions, **When** viewing AI analytics, **Then** the dashboard shows deflection rate (issues resolved without human) and escalation reasons
4. **Given** completed campaigns, **When** viewing campaign performance, **Then** metrics include delivery rate, open rate, response rate, and conversion rate
5. **Given** multiple agents, **When** viewing team performance, **Then** individual agent metrics (conversations handled, average resolution time, customer satisfaction) are displayed

---

### Edge Cases

- **What happens when a channel (e.g., WhatsApp API) goes down during active conversations?**
  - System must queue outgoing messages for retry
  - Display clear "channel offline" status to agents
  - Log failed delivery attempts for audit
  - Auto-retry with exponential backoff when channel reconnects

- **How does the system handle message delivery failures (e.g., invalid phone number, blocked email)?**
  - Mark message status as "failed" with error reason
  - Alert assigned agent with actionable error message
  - For broadcasts, track failure rate per campaign
  - Provide manual retry option for transient failures

- **What happens when AI and human agent both try to respond simultaneously?**
  - AI must yield to human agent (human always takes precedence)
  - Log the race condition for monitoring
  - Display "Agent typing" indicator to suppress AI
  - AI should not resume auto-responses after human stops unless re-enabled

- **How does the system handle duplicate messages from unreliable channels?**
  - Implement idempotency using channel-specific message IDs
  - Deduplicate within 5-minute window
  - Log deduplication events for debugging
  - Ensure conversation thread doesn't show duplicates

- **What happens when tenant data isolation is accidentally bypassed (critical security edge case)?**
  - All queries must include tenant context from session
  - Database row-level security as backup enforcement
  - Audit logs must track tenant context for every query
  - Automated tests must verify cross-tenant data leakage prevention

- **How does the system handle high-volume message spikes (e.g., viral campaign response)?**
  - Queue system must auto-scale workers horizontally
  - Rate limiting per channel to avoid API bans
  - Display queue depth to agents (e.g., "50 messages pending")
  - Prioritize real-time customer messages over batch/broadcast

- **What happens when a contact exists in multiple tenants (same email/phone used by different businesses)?**
  - Contacts are tenant-scoped (no shared contact database)
  - Same person can have separate profiles per tenant
  - No cross-tenant contact linking or data sharing

- **How does the system handle message threading across channels (customer starts on WhatsApp, continues on Email)?**
  - Messages are linked to contact, not channel-specific thread
  - Agent sees unified timeline regardless of channel switching
  - Each message retains original channel metadata
  - System should suggest potential duplicate contacts for manual merging

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Multi-Tenancy

- **FR-001**: System MUST support session-based authentication with secure HTTP-only cookies
- **FR-002**: System MUST enforce organization-based multi-tenancy with complete data isolation between organizations
- **FR-003**: System MUST implement role-based access control (RBAC) with at minimum: Super Admin, Organization Admin, Agent, and Read-Only roles
- **FR-004**: Users MUST be able to belong to multiple teams within an organization with distinct permissions per team
- **FR-005**: System MUST automatically establish tenant context from session before any data access
- **FR-006**: System MUST track and audit all authentication events (login, logout, session expiry, failed attempts)

#### Unified Inbox

- **FR-007**: System MUST normalize messages from all channels into a unified conversation schema
- **FR-008**: System MUST display real-time message updates via WebSocket connections without page refresh
- **FR-009**: System MUST track message states: sent, delivered, read, failed (channel-specific states mapped to unified states)
- **FR-010**: System MUST allow agents to assign conversations to themselves or other team members
- **FR-011**: System MUST support internal notes visible only to agents (not sent to customer)
- **FR-012**: System MUST allow tagging conversations with custom labels for organization
- **FR-013**: System MUST preserve message order within a conversation across all channels
- **FR-014**: System MUST display typing indicators when customers are composing messages (for channels that support it)

#### Channel Integrations

- **FR-015**: System MUST integrate with WhatsApp Business API for sending and receiving messages
- **FR-016**: System MUST support Email communication via SMTP/IMAP or email API providers
- **FR-017**: System MUST integrate with Instagram Messaging API for direct messages
- **FR-018**: System MUST integrate with Facebook Messenger API for page conversations
- **FR-019**: System MUST support SMS sending and receiving via configurable gateway providers
- **FR-020**: System MUST provide a web chat widget embeddable on customer websites
- **FR-021**: System MUST support voice calls with call logging and recording
- **FR-022**: Each channel integration MUST attach metadata (channel type, sender ID, timestamp, channel-specific message ID)
- **FR-023**: System MUST validate webhook signatures for all inbound channel webhooks to prevent spoofing
- **FR-024**: System MUST handle channel-specific media types (images, videos, documents, voice notes, locations)

#### CRM & Contact Management

- **FR-025**: System MUST automatically create contact profiles when a new customer initiates conversation
- **FR-026**: System MUST allow manual creation and editing of contact profiles with custom fields
- **FR-027**: System MUST support contact tagging and segmentation for targeting
- **FR-028**: System MUST display complete conversation history timeline per contact across all channels
- **FR-029**: System MUST allow agents to add private notes to contact profiles
- **FR-030**: System MUST track contact lifecycle stages (lead, customer, churned, etc.)
- **FR-031**: System MUST support contact import/export for data migration
- **FR-032**: System MUST prevent duplicate contacts within a tenant (suggest potential matches for manual review)

#### Ticket & Complaint Management

- **FR-033**: System MUST allow creation of tickets from conversations or manually
- **FR-034**: System MUST track ticket lifecycle: open → assigned → in progress → resolved → closed
- **FR-035**: System MUST support priority levels (low, normal, high, urgent) with visual indicators
- **FR-036**: System MUST enforce SLA deadlines with countdown timers and breach alerts
- **FR-037**: System MUST support escalation rules triggered by SLA breach or manual action
- **FR-038**: System MUST maintain complete audit trail of ticket state changes (who, when, what)
- **FR-039**: System MUST allow customers to reopen closed tickets within configurable time window
- **FR-040**: System MUST link tickets to contacts and conversations for full context

#### Broadcast & Campaign Management

- **FR-041**: System MUST support bulk message sending to segmented contact lists
- **FR-042**: System MUST provide template system with variable substitution (e.g., {{first_name}})
- **FR-043**: System MUST allow scheduling campaigns for future send times
- **FR-044**: System MUST support audience segmentation by contact tags, attributes, or custom filters
- **FR-045**: System MUST track delivery status per recipient (sent, delivered, read, failed)
- **FR-046**: System MUST respect channel-specific rate limits to avoid API throttling/bans
- **FR-047**: System MUST allow pausing or canceling in-progress campaigns
- **FR-048**: System MUST provide campaign analytics (total sent, delivery rate, response rate, conversion tracking)

#### AI Agent System

- **FR-049**: System MUST support multiple AI agent types (routing, support) with distinct personas and knowledge (sales/billing agents deferred to post-MVP)
- **FR-050**: AI agents MUST interact with backend systems only via defined tool APIs (no direct database access)
- **FR-051**: System MUST log every AI interaction (prompt, tool calls, responses, timestamps) in ai_runs table
- **FR-052**: AI agents MUST support escalation to human agents with full conversation context handoff
- **FR-053**: System MUST detect customer intent (support, sales, complaint) and route to appropriate AI agent
- **FR-054**: AI agents MUST use knowledge base (RAG system) to provide accurate, context-aware responses
- **FR-055**: System MUST allow per-tenant AI configuration (enable/disable agents, customize behavior, set escalation rules)
- **FR-056**: AI agents MUST be restricted to read-only operations (search knowledge base, fetch order status, retrieve contact info) and CANNOT create/modify data (tickets, CRM, broadcasts) without human approval
- **FR-057**: System MUST provide kill-switch to instantly disable AI for a tenant or globally
- **FR-058**: AI tool functions MUST be categorized as read-only (allowed) or write (requires human approval)

#### Knowledge Base (RAG System)

- **FR-058**: System MUST support document ingestion from multiple formats (PDF, text files, URLs)
- **FR-059**: System MUST chunk documents and generate embeddings for semantic search
- **FR-060**: System MUST provide semantic search over knowledge base with relevance ranking
- **FR-061**: System MUST inject relevant knowledge base context into AI agent prompts
- **FR-062**: System MUST support versioning of knowledge base documents with change tracking
- **FR-063**: System MUST allow per-tenant knowledge bases (isolated, tenant-specific content)

#### Analytics & Reporting

- **FR-064**: System MUST track and display First Response Time (FRT) and Average Response Time (ART) metrics
- **FR-065**: System MUST track ticket resolution time and SLA compliance rates
- **FR-066**: System MUST calculate AI deflection rate (issues resolved by AI vs escalated to humans)
- **FR-067**: System MUST provide campaign performance metrics (delivery, open, response, conversion rates)
- **FR-068**: System MUST track agent performance (conversations handled, resolution time, customer satisfaction)
- **FR-069**: System MUST display channel usage statistics (message volume per channel over time)
- **FR-070**: System MUST support date range filtering and export of all analytics data

#### Voice Module

- **FR-071**: System MUST support inbound and outbound voice calls linked to contact profiles
- **FR-072**: System MUST log all calls with metadata (caller ID, duration, timestamp, assigned agent)
- **FR-073**: System MUST record calls and store recordings securely
- **FR-074**: System MUST transcribe call recordings using speech-to-text
- **FR-075**: System MUST support IVR (Interactive Voice Response) menus for call routing
- **FR-076**: System MUST maintain callback queues for missed calls
- **FR-077**: System MUST integrate call transcripts into conversation timeline

#### Real-Time & Event System

- **FR-078**: System MUST use WebSocket connections for real-time inbox updates
- **FR-079**: System MUST emit events for: new_message, message_status_update, ticket_update, assignment_change, ai_response_stream
- **FR-080**: System MUST persist all events in database before broadcasting via WebSocket (event sourcing)
- **FR-081**: System MUST support event replay for new WebSocket connections (reconstruct current state)
- **FR-082**: System MUST maintain event ordering per conversation to prevent race conditions

#### Security & Compliance

- **FR-083**: System MUST validate and sanitize all user input to prevent XSS and SQL injection attacks
- **FR-084**: System MUST implement CSRF protection for all state-changing operations
- **FR-085**: System MUST enforce rate limiting per tenant and per user to prevent abuse
- **FR-086**: System MUST encrypt sensitive data at rest (passwords, API keys, customer PII)
- **FR-087**: System MUST audit log all critical actions (message sends, AI escalations, user changes, permission changes)
- **FR-088**: System MUST support soft deletes for all customer data (retain for audit/recovery)
- **FR-089**: System MUST implement webhook signature validation for all channel integrations

#### Performance & Scalability

- **FR-090**: System MUST support horizontal scaling of background workers for async task processing
- **FR-091**: System MUST use caching for frequently accessed data (contact profiles, channel configs)
- **FR-092**: System MUST process incoming messages asynchronously to avoid blocking channel webhooks
- **FR-093**: System MUST target internal message processing latency under 200ms (excluding external channel API calls)

### Key Entities

- **Organization (Tenant)**: Represents a business customer using the platform. Contains users, teams, channels, contacts, conversations, tickets, campaigns, and AI configurations. Enforces complete data isolation.

- **User**: An individual with platform access. Belongs to one organization, can be member of multiple teams. Has a role (Super Admin, Org Admin, Agent, Read-Only) that defines permissions.

- **Team**: A group of users within an organization. Used for conversation assignment and permission scoping.

- **Channel Account**: A connected communication channel (WhatsApp Business, Email, SMS gateway, etc.) with credentials and configuration. Belongs to an organization.

- **Contact**: A customer or lead. Contains profile information (name, email, phone, tags, custom fields), lifecycle stage, and relationship to conversations. Tenant-scoped.

- **Conversation**: A message thread with a contact. Channel-agnostic (contains messages from any channel). Has assignment (which agent/team handles it), status (open, closed), and tags.

- **Message**: A single communication unit within a conversation. Contains sender, recipient, content, media attachments, channel metadata, timestamp, and delivery status.

- **Ticket**: A formal support request created from a conversation or manually. Has priority, SLA deadline, lifecycle state, assigned agent, and audit trail.

- **Broadcast Campaign**: A bulk messaging job targeting segmented contacts. Contains template, target audience filter, schedule, and delivery tracking.

- **AI Run**: A log of AI agent execution. Contains conversation context, prompts, tool calls made, responses generated, and escalation decisions. Used for audit and debugging.

- **Knowledge Document**: Content ingested into the RAG system. Can be PDF, text file, URL content. Chunked into embeddings for semantic search.

- **Call Log**: A record of a voice interaction. Contains caller ID, agent, duration, recording file reference, transcript, and link to contact/conversation.

- **Audit Log**: Immutable record of critical system actions. Contains actor (user/system), action type, affected entity, tenant context, and timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Agents can view and respond to messages from at least 3 different channels in a single unified inbox interface
- **SC-002**: Real-time message updates appear in agent inbox within 2 seconds of customer sending (excluding external channel API latency)
- **SC-003**: AI agents successfully handle and resolve at least 60% of common inquiries without human escalation
- **SC-004**: Broadcast campaigns can send messages to 10,000 recipients within 1 hour while respecting channel rate limits
- **SC-005**: System supports at least 500 concurrent agents across all tenants without performance degradation
- **SC-006**: Average response time to customer messages decreases by at least 40% compared to manual multi-platform management
- **SC-007**: Ticket SLA breach rate is reduced to under 10% through automated alerts and escalation
- **SC-008**: Voice call transcription achieves at least 90% accuracy for English language conversations
- **SC-009**: Analytics dashboards load and display metrics for 30-day time periods in under 3 seconds
- **SC-010**: Zero cross-tenant data leakage incidents in production (100% tenant isolation)
- **SC-011**: Campaign delivery success rate exceeds 95% (excluding invalid contact data)
- **SC-012**: Agent productivity (conversations handled per hour) increases by at least 50% with AI assistance enabled

## Assumptions

1. **Channel API Availability**: We assume third-party channel APIs (WhatsApp Business, Facebook Messenger, etc.) maintain reasonable uptime (>99.5%) and backward compatibility. System design includes retry mechanisms for transient failures.

2. **AI Model Performance**: We assume OpenAI (or Gemini) API provides consistent response times (<3 seconds for typical queries) and maintains model availability. System includes fallback to human agents when AI services are unavailable.

3. **Message Volume**: We assume typical tenants handle up to 10,000 messages per day with peak spikes up to 3x normal volume. Architecture supports horizontal scaling for higher volumes.

4. **Storage Growth**: We assume average message size of 1KB (text) to 5MB (media), with 90-day hot storage and archival for older data. Storage strategy uses S3-compatible object storage for cost-effectiveness.

5. **Regulatory Compliance**: We assume businesses using the platform are responsible for obtaining customer consent for messaging and call recording per their jurisdiction (GDPR, TCPA, etc.). Platform provides tools (opt-out, data export, deletion) but does not enforce specific compliance workflows.

6. **Network Reliability**: We assume agents have stable internet connections. WebSocket reconnection logic handles temporary network interruptions, but persistent offline scenarios require local queueing (future enhancement).

7. **Language Support**: Initial implementation assumes English language for AI agents and transcription. Multi-language support is a future enhancement requiring additional embeddings and model configurations.

8. **Authentication Delegation**: MVP uses session-based authentication (Better Auth) with email/password only. OAuth/Social login (Google, Microsoft, Meta) and enterprise SSO (SAML, OAuth2) will be added post-MVP based on customer demand. This avoids OAuth app approval delays and reduces initial complexity.

9. **Media Storage Costs**: We assume media files (images, videos, call recordings) account for 80% of storage costs. Retention policies (e.g., delete media after 90 days, keep metadata) will be configurable per tenant.

10. **AI Training Data**: We assume tenant-provided knowledge base documents are sufficient for AI accuracy. Custom model fine-tuning per tenant is out of scope for initial release.

## Clarifications

### Session 2026-06-21

- **Q1: MVP Scope Strategy** → **A: Inbox + AI MVP** (8-10 weeks) - Build unified inbox with AI auto-responses and priority channels (WhatsApp, Email, Web Chat). This balanced approach delivers core value plus competitive differentiation. CRM, Tickets, Broadcasts, Voice, and Analytics are deferred to post-MVP phases based on customer demand.

- **Q2: AI Agent Capabilities Scope** → **A: Auto-reply + Read-only Actions** - AI can send responses AND perform safe read-only operations (search knowledge base, fetch order status, retrieve contact information) but CANNOT create/modify data (tickets, CRM updates, broadcasts). This provides useful automation with controlled risk. Future enhancement: Human-in-loop approval workflow for write actions based on real-world usage patterns and customer trust levels.

- **Q3: Multi-Tenancy Database Model** → **A: Shared Database with Row-Level Security (RLS)** - Single PostgreSQL database with tenant_id on all domain tables enforced via Row-Level Security policies. This industry-standard approach (used by Slack, GitHub, Notion) provides security-by-default, cost efficiency, and scales to 10,000+ tenants. RLS prevents cross-tenant data leaks even if application code has bugs.

- **Q4: Media Storage Strategy for MVP** → **A: S3-Compatible from Day 1** - Use S3-compatible object storage from the start to avoid painful migration later. For MVP cost optimization: Start with MinIO (self-hosted, free) or AWS S3 Free Tier (5GB free for 12 months). Estimated MVP cost: ~$0.10/month with AWS S3 or $0 with MinIO. Enables horizontal scaling and prevents technical debt.

- **Q5: OAuth/Social Login Requirement** → **A: Session-based Only (Email/Password) for MVP** - Focus exclusively on Better Auth with email/password authentication for initial release. OAuth/Social login (Google, Microsoft, Meta) deferred to post-MVP phase. This avoids OAuth app approval delays (1-2 weeks), reduces complexity, and aligns with B2B SaaS standard practice of launching with email/password first.

## Scope

### MVP Scope (Phase 1: Inbox + AI - 8-10 weeks)

**Priority Features for First Release:**
- ✅ Core unified inbox with multi-channel message normalization
- ✅ Real-time WebSocket-based message updates and typing indicators
- ✅ **Priority Channel Integration**: WhatsApp Business API, Email (SMTP/API), Web Chat widget
- ✅ AI agent system with routing and support agents (sales/billing agents deferred)
- ✅ Knowledge base (RAG) system for AI context
- ✅ Basic contact auto-creation and conversation history
- ✅ Multi-tenant architecture with complete data isolation
- ✅ Role-based access control (Org Admin, Agent roles - Super Admin deferred)
- ✅ Background worker system for message ingestion and AI execution

### Post-MVP Features (Phase 2+)

**Deferred to Phase 2 (based on customer feedback):**
- Full CRM contact management with tags, notes, lifecycle tracking
- Ticket and complaint tracking with SLA enforcement
- Broadcast campaign system with scheduling and analytics
- Additional channels: Instagram, Facebook Messenger, SMS
- AI sales and billing specialized agents
- Analytics dashboards (start with basic metrics in MVP)

**Deferred to Phase 3+:**
- Voice calls with recording and transcription
- Advanced audit logging
- Super Admin role and org management
- Read-Only role

## Scope (Full Platform Vision)

### In Scope (Full Platform - All Features)

This represents the complete vision after MVP + all post-MVP phases:

- Core unified inbox with multi-channel message normalization
- Real-time WebSocket-based message updates and typing indicators
- Integration with all 7 channels: WhatsApp Business API, Email, SMS, Instagram, Facebook Messenger, Web Chat, Voice
- AI agent system with routing, support, sales, and billing agent types
- Knowledge base (RAG) system for AI context
- Full CRM contact management with tags, notes, and conversation history
- Ticket and complaint tracking with SLA enforcement
- Broadcast campaign system with scheduling and analytics
- Voice calls with recording and transcription
- Analytics dashboards for response time, ticket resolution, AI deflection, campaign performance, agent productivity
- Multi-tenant architecture with complete data isolation
- Role-based access control (Super Admin, Org Admin, Agent, Read-Only)
- Audit logging for critical actions
- Background worker system for async processing (message ingestion, AI execution, broadcasts, transcription)

### Out of Scope (Future Enhancements)

- Mobile applications (iOS/Android) - initial release is web-only
- Custom AI model fine-tuning per tenant - uses pre-trained models with RAG
- Video calling functionality - voice only for initial release
- Social media post monitoring (Twitter, LinkedIn) - only direct messaging channels in scope
- Advanced workflow automation (if/then rules, custom triggers) - future enhancement
- Third-party integrations (Salesforce, HubSpot, Zendesk sync) - future connectors
- Multi-language AI support - English only initially
- SSO/SAML authentication - session-based auth only initially
- Sentiment analysis and conversation categorization - future AI enhancement
- Chatbot visual builder (no-code bot creation) - future feature
- Co-browsing and screen sharing - out of scope
- Payment processing within conversations - future commerce enhancement
- Appointment scheduling and calendar integration - future feature
