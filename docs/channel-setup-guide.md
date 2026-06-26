# CPAAS — Channel Setup & Testing Guide

> **Audience**: Developers and operators setting up the platform for the first time.
> **API Base URL**: `http://localhost:8000` (dev) · `https://api.yourdomain.com` (prod)
> **Frontend**: `http://localhost:3000`

---

## Table of Contents

1. [Account & Tenant Setup](#1-account--tenant-setup)
2. [Web Chat Channel](#2-web-chat-channel) ← _easiest, start here_
3. [Email Channel](#3-email-channel)
4. [WhatsApp Channel](#4-whatsapp-channel)
5. [AI Agents & Knowledge Base](#5-ai-agents--knowledge-base)
6. [Using the Inbox (Day-to-Day)](#6-using-the-inbox)
7. [End-to-End Testing Checklist](#7-end-to-end-testing-checklist)
8. [Exposing Local Server (ngrok)](#8-exposing-local-server-for-webhooks)
9. [Security Best Practices](#9-security-best-practices)
10. [API Quick Reference](#10-api-quick-reference)

---

## 1. Account & Tenant Setup

### Register your workspace

Every company gets an isolated **tenant**. The first user to register becomes the tenant owner.

**Via UI:**
1. Open `http://localhost:3000/register`
2. Fill in: Organization Name, Your Name, Email, Password
3. You are now logged in as **owner** of your tenant

**Via API (curl):**
```bash
curl -s -c cookies.txt -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Acme Corp",
    "full_name": "Ali Khan",
    "email": "ali@acme.com",
    "password": "SuperSecret123!"
  }' | jq .
```

**Expected response:**
```json
{
  "user": {
    "id": "uuid...",
    "email": "ali@acme.com",
    "full_name": "Ali Khan",
    "tenant_id": "uuid..."
  },
  "tenant": {
    "id": "uuid...",
    "name": "Acme Corp"
  }
}
```
> `cookies.txt` stores your session cookie — subsequent requests will be authenticated.

### Login (existing account)
```bash
curl -s -c cookies.txt -b cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ali@acme.com", "password": "SuperSecret123!"}' | jq .
```

### Verify session
```bash
curl -s -b cookies.txt http://localhost:8000/api/v1/auth/me | jq .
```

---

## 2. Web Chat Channel

**What it is**: An embeddable JavaScript widget you paste into any website. Visitors
can send messages that appear instantly in your unified inbox.

**Why start here**: No third-party accounts needed. Works 100% locally.

---

### Step 2.1 — Create the Web Chat channel

**Via UI:**
1. Go to `http://localhost:3000/settings/channels`
2. Click **"Add Web Chat"**, give it a name (e.g. "Website Support")
3. Copy the **Channel Account ID** shown after creation

**Via API:**
```bash
curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/channels/webchat/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Website Support"}' | jq .
```

**Response:**
```json
{
  "id": "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
  "channel_type": "webchat",
  "name": "Website Support",
  "is_active": true
}
```
> Save the `id` — this is your **CHANNEL_ACCOUNT_ID**.

---

### Step 2.2 — Embed the widget on any webpage

Create a test HTML file (e.g. `test-chat.html`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Test Chat</title>
</head>
<body>
  <h1>Hello — the chat widget is in the bottom-right corner.</h1>

  <!-- CPAAS Web Chat Widget -->
  <script
    src="http://localhost:3000/webchat-widget.js"
    data-account="aaaabbbb-cccc-dddd-eeee-ffffffffffff"
    data-api="http://localhost:8000">
  </script>
</body>
</html>
```

> Replace `data-account` with your actual **CHANNEL_ACCOUNT_ID**.

Open `test-chat.html` in a browser. The chat bubble appears bottom-right.

---

### Step 2.3 — Test the flow

1. Open `test-chat.html` in **Browser A** (visitor side)
2. Open `http://localhost:3000/inbox` in **Browser B** (agent side — logged in)
3. Type a message in the widget → click **Send**
4. In Browser B inbox: a new conversation appears instantly (WebSocket push)
5. Click the conversation → type a reply → click **Send**

**Expected result**: Message in inbox, conversation created, agent can reply.

---

### Step 2.4 — Test API directly (no HTML file needed)

```bash
curl -s -X POST http://localhost:8000/api/v1/webchat/messages \
  -H "Content-Type: application/json" \
  -d '{
    "channel_account_id": "aaaabbbb-cccc-dddd-eeee-ffffffffffff",
    "session_id": "test_visitor_001",
    "content": "Hello, I need help with my order",
    "visitor_name": "Ahmed Visitor",
    "page_url": "https://example.com/products"
  }' | jq .
```

---

## 3. Email Channel

**What it is**: Connect an email address so inbound emails become inbox conversations.
Outbound replies go via SMTP.

**Inbound options**:
- **SendGrid Inbound Parse** (recommended for production) — SendGrid forwards emails to your webhook
- **IMAP polling** (simpler, for testing) — the worker polls your mailbox every 30s

---

### Step 3.1 — Get SMTP credentials

**Option A: Gmail (for testing)**
1. Enable **2-Factor Authentication** on your Google Account
2. Go to: Google Account → Security → App Passwords
3. Generate an App Password → select "Mail" + "Other"
4. Note the 16-character password

**Option B: Any SMTP provider** (SendGrid, Mailgun, SES, etc.)
- Get your SMTP host, port, user, and password from provider dashboard

---

### Step 3.2 — Connect the email channel

**Via API:**
```bash
curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/channels/email/connect \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Support Inbox",
    "from_address": "support@acme.com",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "support@acme.com",
    "smtp_password": "your-app-password-here",
    "inbound_address": "support@acme.com"
  }' | jq .
```

> **`inbound_address`**: the email address SendGrid/IMAP watches for inbound mail.

**Via UI:**
1. `Settings → Channels → Add Email`
2. Fill in SMTP details → Save

---

### Step 3.3 — Configure inbound (SendGrid Inbound Parse)

**Prerequisite**: Your server must be publicly reachable (see [Section 8 — ngrok](#8-exposing-local-server-for-webhooks)).

1. Log in to [SendGrid](https://app.sendgrid.com)
2. Go to **Settings → Inbound Parse → Add Host & URL**
3. Set:
   - **Receiving Domain**: `mail.acme.com` (add MX record pointing to `mx.sendgrid.net`)
   - **Destination URL**: `https://YOUR_NGROK_URL/webhooks/email`
   - Enable **"Post the raw, full MIME message"**: OFF (default form mode is fine)
4. Send a test email to `support@acme.com`
5. Check your inbox — a conversation should appear

**Test the webhook directly:**
```bash
curl -s -X POST http://localhost:8000/webhooks/email \
  -F "from=customer@gmail.com" \
  -F "to=support@acme.com" \
  -F "subject=Help with billing" \
  -F "text=Hi, I was charged twice this month. Please help." | jq .
```

---

### Step 3.4 — IMAP polling (alternative to SendGrid)

Add to `.env`:
```env
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=support@acme.com
IMAP_PASSWORD=your-app-password
```

The Celery worker (`email_sync`) polls every 30 seconds automatically when running.
Start the worker: `docker-compose up -d worker`

---

## 4. WhatsApp Channel

**What it is**: Connect WhatsApp Business API (Meta) so WhatsApp messages appear in your inbox.

**Requirements**:
- Meta Developer Account (free)
- WhatsApp Business Account
- Public HTTPS webhook URL (use ngrok for local testing)

---

### Step 4.1 — Create a Meta App

1. Go to [Meta for Developers](https://developers.facebook.com)
2. **My Apps → Create App → Business type**
3. Add **WhatsApp** product to your app
4. Go to **WhatsApp → Getting Started**
5. Note down:
   - **Phone Number ID** (e.g. `123456789012345`)
   - **WhatsApp Business Account ID**
   - **Temporary Access Token** (or generate a permanent system user token)

---

### Step 4.2 — Add your credentials to `.env`

```env
WHATSAPP_VERIFY_TOKEN=my_random_verify_token_123
WHATSAPP_APP_SECRET=your_app_secret_from_meta
WHATSAPP_ACCESS_TOKEN=your_access_token_from_meta
```

> **`WHATSAPP_VERIFY_TOKEN`**: any random string you choose — Meta sends it to verify your webhook.

Restart the backend: `docker-compose restart backend`

---

### Step 4.3 — Expose webhook via ngrok

```bash
ngrok http 8000
# You get: https://abc123.ngrok-free.app
```

---

### Step 4.4 — Register webhook on Meta

1. Meta Developer Dashboard → **WhatsApp → Configuration**
2. Set **Webhook URL**: `https://abc123.ngrok-free.app/webhooks/whatsapp`
3. Set **Verify Token**: same value as `WHATSAPP_VERIFY_TOKEN` in `.env`
4. Click **Verify and Save** — Meta calls `GET /webhooks/whatsapp` with your token
5. Subscribe to **Webhook Fields**: `messages` (check the checkbox)

**Verify locally:**
```bash
curl "http://localhost:8000/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=my_random_verify_token_123&hub.challenge=CHALLENGE_ACCEPTED"
# Should return: CHALLENGE_ACCEPTED
```

---

### Step 4.5 — Connect the WhatsApp channel

```bash
curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/channels/whatsapp/connect \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WhatsApp Business",
    "phone_number_id": "123456789012345",
    "access_token": "your_access_token",
    "app_secret": "your_app_secret"
  }' | jq .
```

---

### Step 4.6 — Test WhatsApp

1. Send a WhatsApp message **from your personal phone** to your business number
2. Check your inbox — the conversation appears within seconds
3. Reply from the inbox → message delivered to the customer's phone

**Simulate an inbound webhook (no phone needed for backend testing):**
```bash
curl -s -X POST http://localhost:8000/webhooks/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [{
        "value": {
          "messaging_product": "whatsapp",
          "metadata": {"display_phone_number": "923001234567", "phone_number_id": "123456789012345"},
          "contacts": [{"profile": {"name": "Usman Khan"}, "wa_id": "923009876543"}],
          "messages": [{
            "from": "923009876543",
            "id": "wamid.test001",
            "timestamp": "1700000000",
            "text": {"body": "Hello, I need support"},
            "type": "text"
          }]
        },
        "field": "messages"
      }]
    }]
  }' | jq .
```

> Note: Signature verification is skipped in dev when `WHATSAPP_APP_SECRET` is not set.

---

## 5. AI Agents & Knowledge Base

### Step 5.1 — Verify Gemini API key

In `.env`:
```env
GEMINI_API_KEY=your_key_here
LLM_MODEL=gemini-2.5-flash
```

Verify: `docker-compose logs backend | grep "startup"`

---

### Step 5.2 — Upload knowledge base documents

**Via UI:**
1. Go to `Settings → Knowledge Base → Upload Document`
2. Upload a PDF or paste text (e.g. FAQ, product docs, pricing)
3. Wait ~10-30s for embedding (Celery worker processes it)

**Via API (text):**
```bash
curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/knowledge/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Refund Policy",
    "source_type": "text",
    "content": "We offer a 30-day full refund on all products. To request a refund, email support@acme.com with your order number. Refunds are processed within 5 business days."
  }' | jq .
```

**Via API (PDF upload):**
```bash
curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/knowledge/documents/upload \
  -F "file=@/path/to/your/faq.pdf" | jq .
```

**Test semantic search:**
```bash
curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "how do I get a refund?", "top_k": 3}' | jq .
```

---

### Step 5.3 — Enable AI for a channel

**Via UI:**
1. Go to `Settings → AI Agents`
2. Select agent type: **Support**
3. Toggle **Active** → Save
4. The AI now auto-responds to inbound messages using your knowledge base

**Via API:**
```bash
curl -s -b cookies.txt -X PUT http://localhost:8000/api/v1/ai/configurations/support \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": true,
    "system_prompt": "You are a helpful support agent for Acme Corp. Be concise and friendly. If you cannot answer, escalate to a human.",
    "max_tokens": 500,
    "temperature": 0.3
  }' | jq .
```

---

### Step 5.4 — AI Kill Switch (emergency)

```bash
curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/ai/kill-switch \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}' | jq .
```

---

### Step 5.5 — View AI run logs

```bash
# List recent runs
curl -s -b cookies.txt http://localhost:8000/api/v1/ai/runs | jq .

# Specific run details (tool calls, prompts, response)
curl -s -b cookies.txt http://localhost:8000/api/v1/ai/runs/{run_id} | jq .
```

---

## 6. Using the Inbox

### Conversation lifecycle

```
Inbound message arrives
        │
        ▼
   [open] ──── AI auto-replies (if enabled) ──► escalates if unsure
        │                                              │
        ▼                                              ▼
  Agent assigned                                Agent handles
        │
        ▼
    [resolved]
```

### Daily workflow

| Action | How |
|--------|-----|
| See all open conversations | Inbox → "Open" tab |
| Filter my assigned | Inbox → "Mine" tab |
| Reply to customer | Select conversation → type in Reply box → Send |
| Add internal note | Select conversation → click "Internal Note" tab → Add Note |
| Assign to yourself | Click **"Assign to me"** button in conversation header |
| Search conversations | Use search bar at top of conversation list |

### Keyboard shortcuts
| Key | Action |
|-----|--------|
| `⌘ Enter` (Mac) / `Ctrl Enter` (Win) | Send message |
| `Esc` | Close mobile sidebar |

---

## 7. End-to-End Testing Checklist

Run this checklist after setup to confirm everything works.

### Auth
- [ ] Register a new account → redirected to inbox
- [ ] Logout → redirected to login
- [ ] Login → session restored
- [ ] `/api/v1/auth/me` returns correct user

### Web Chat
- [ ] Created Web Chat channel → got Channel Account ID
- [ ] Widget loads on test HTML page
- [ ] Visitor sends message → conversation appears in inbox (within 2s)
- [ ] Agent replies → no error
- [ ] Refresh inbox → conversation still visible

### Email
- [ ] Connected email channel (SMTP)
- [ ] Sent test webhook → conversation created
- [ ] (Optional) Real inbound email via SendGrid → conversation created

### WhatsApp
- [ ] `WHATSAPP_VERIFY_TOKEN` set in `.env`
- [ ] Verify endpoint returns challenge → `GET /webhooks/whatsapp?...`
- [ ] Simulated inbound payload → conversation created
- [ ] (Real phone) Sent WhatsApp message → appears in inbox

### AI
- [ ] Uploaded a knowledge document
- [ ] Knowledge search returns relevant results
- [ ] AI configuration set to active
- [ ] Inbound message → AI replied automatically
- [ ] AI run log shows prompt + response → `/api/v1/ai/runs`
- [ ] Kill switch works → AI stops responding

### Inbox UI
- [ ] Conversations list loads
- [ ] Search filters conversations correctly
- [ ] "Open" / "Mine" / "Resolved" tabs filter correctly
- [ ] Messages load on conversation select
- [ ] Realtime: open two browser tabs, send from one → appears in other instantly
- [ ] Internal note visible in thread (amber color, not sent to customer)
- [ ] Mobile view: hamburger opens sidebar, back button works

---

## 8. Exposing Local Server for Webhooks

WhatsApp and SendGrid Email require a **public HTTPS URL**. Use ngrok for local testing.

### Install ngrok
```bash
# Download from https://ngrok.com/download
# Or via brew:
brew install ngrok
ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
```

### Start tunnel
```bash
ngrok http 8000
# Output:
# Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

### Use in webhooks
| Channel | Webhook URL |
|---------|-------------|
| WhatsApp | `https://abc123.ngrok-free.app/webhooks/whatsapp` |
| SendGrid Email | `https://abc123.ngrok-free.app/webhooks/email` |

> **Important**: Free ngrok URLs change on every restart. Pin a static domain on ngrok's paid plan or use a reverse proxy (Cloudflare Tunnel is free).

### Cloudflare Tunnel (free static URL alternative)
```bash
# Install cloudflared
# Windows: winget install Cloudflare.cloudflared

cloudflared tunnel --url http://localhost:8000
# Gives you a permanent *.trycloudflare.com URL (no account needed for quick test)
```

---

## 9. Security Best Practices

### Secrets management
- Never commit `.env` to Git — it's in `.gitignore`
- Rotate `SECRET_KEY` carefully: invalidates all active sessions
- Use separate `.env` per environment (dev / staging / prod)

### WhatsApp webhook security
- Always set `WHATSAPP_APP_SECRET` in production
- The webhook handler verifies the `X-Hub-Signature-256` header
- Reject any request where signature doesn't match

### Session security
- In production: `SESSION_COOKIE_SECURE=true` (HTTPS only)
- Session TTL default: 7 days (configurable via `SESSION_TTL_SECONDS`)
- Sessions stored in DB — logout invalidates server-side

### API rate limiting
- Default: 120 requests/minute per user/IP (configurable via `RATE_LIMIT_PER_MINUTE`)
- Enabled by default (`RATE_LIMIT_ENABLED=true`)

### Channel credential encryption
- WhatsApp access tokens and SMTP passwords are **encrypted at rest** in the database
- Encryption key is derived from `SECRET_KEY`

### AI guardrails
- Input: profanity filter + prompt injection detection
- Output: brand safety check, no unauthorized write operations
- Kill switch: instant disable via API or UI

---

## 10. API Quick Reference

> All authenticated endpoints require the session cookie (set automatically after login).
> API docs (Swagger): `http://localhost:8000/docs`

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register + create tenant |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Current user |

### Channels
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/channels` | List connected channels |
| POST | `/api/v1/channels/webchat/create` | Create Web Chat channel |
| POST | `/api/v1/channels/whatsapp/connect` | Connect WhatsApp |
| POST | `/api/v1/channels/email/connect` | Connect Email |

### Webhooks (public — no auth)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/webhooks/whatsapp` | Meta webhook verification |
| POST | `/webhooks/whatsapp` | Inbound WhatsApp message |
| POST | `/webhooks/email` | Inbound email (SendGrid) |
| POST | `/api/v1/webchat/messages` | Web chat visitor message |

### Inbox
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/inbox/conversations` | List conversations |
| GET | `/api/v1/inbox/conversations/{id}/messages` | Get messages |
| POST | `/api/v1/inbox/conversations/{id}/messages` | Send reply |
| PUT | `/api/v1/inbox/conversations/{id}/assign` | Assign conversation |
| POST | `/api/v1/inbox/conversations/{id}/notes` | Add internal note |

### Knowledge Base
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/knowledge/documents` | Create document (text) |
| POST | `/api/v1/knowledge/documents/upload` | Upload PDF/file |
| GET | `/api/v1/knowledge/documents` | List documents |
| DELETE | `/api/v1/knowledge/documents/{id}` | Delete document |
| POST | `/api/v1/knowledge/search` | Semantic search |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ai/configurations` | List AI configs |
| PUT | `/api/v1/ai/configurations/{agent_type}` | Update AI config |
| POST | `/api/v1/ai/kill-switch` | Enable/disable AI |
| GET | `/api/v1/ai/runs` | AI run audit logs |
| GET | `/api/v1/ai/runs/{id}` | Run details |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | DB + Redis health check |

---

## Quick Copy-Paste: Full Test Flow (Web Chat)

```bash
# 1. Register
curl -s -c cookies.txt -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"organization_name":"Test Co","full_name":"Test User","email":"test@test.com","password":"Test1234!"}' | jq .user.id

# 2. Create Web Chat channel
CHANNEL_ID=$(curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/channels/webchat/create \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Widget"}' | jq -r .id)
echo "Channel ID: $CHANNEL_ID"

# 3. Send a visitor message
curl -s -X POST http://localhost:8000/api/v1/webchat/messages \
  -H "Content-Type: application/json" \
  -d "{\"channel_account_id\":\"$CHANNEL_ID\",\"session_id\":\"visitor_test_001\",\"content\":\"Hello I need help\",\"visitor_name\":\"Test Visitor\"}" | jq .

# 4. Check conversations in inbox
curl -s -b cookies.txt http://localhost:8000/api/v1/inbox/conversations | jq '.[0] | {id, status, contact}'

# 5. Get the conversation ID and reply
CONV_ID=$(curl -s -b cookies.txt http://localhost:8000/api/v1/inbox/conversations | jq -r '.[0].id')
curl -s -b cookies.txt -X POST "http://localhost:8000/api/v1/inbox/conversations/$CONV_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello! How can I help you today?"}' | jq .

echo "Done! Check http://localhost:3000/inbox"
```

---

_Last updated: 2026-06-24 · MVP v1.0_
