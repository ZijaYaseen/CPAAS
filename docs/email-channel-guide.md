# Email Channel — Inbound & Outbound Guide

## Overview

```
Customer Email
      ↓
  Your Gmail
      ↓  (Gmail Forwarding)
  Cloudmailin
      ↓  (HTTP POST webhook)
  Backend /webhooks/email
      ↓
  Unified Inbox  ←→  Agent replies via SMTP
```

---

## Part 1 — Inbound Setup (Customer → Your Inbox)

### Step 1: Cloudmailin Account

1. Go to [cloudmailin.com](https://cloudmailin.com) → Sign up / Login
2. Create a new **Address**
3. Set **Target URL**:
   ```
   https://ucaas-api-919679113744.asia-south1.run.app/webhooks/email
   ```
4. Set **Format**: `Multipart - Normalized (recommended)`
5. Copy your Cloudmailin address (e.g. `a76f8e1002e6020cef25@cloudmailin.net`)

### Step 2: Gmail Forwarding Setup

1. Gmail → **Settings (gear icon)** → **See all settings**
2. Tab: **"Forwarding and POP/IMAP"**
3. Click **"Add a forwarding address"**
4. Enter your Cloudmailin address: `a76f8e1002e6020cef25@cloudmailin.net`
5. Gmail will send a confirmation email to Cloudmailin
6. Cloudmailin receives it → check **Cloudmailin Dashboard → Messages**
7. Open that message → find the **confirmation link** → click it
8. Back in Gmail Forwarding settings → select **"Forward a copy to..."** → **Save Changes**

> Gmail forwarding only applies to **new emails** received after setup. Old emails are not forwarded.

### Step 3: Connect Email Channel in App

1. Go to `http://localhost:3000/settings/channels`
2. Click **Email → Connect**
3. Fill in details (see Part 2 below for SMTP setup)
4. Click **Connect**

Now incoming emails will appear in your Inbox automatically.

---

## Part 2 — Outbound Setup (You → Customer Reply via SMTP)

To reply to emails from the inbox, SMTP credentials are required.

### Gmail App Password (Required)

Gmail blocks regular passwords for SMTP. You need an **App Password**:

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Make sure **2-Step Verification is ON** (required for App Passwords)
3. Search for **"App passwords"** → click it
4. Select app: **Mail** → Select device: **Other** → type `UCAAS`
5. Click **Generate** → copy the 16-character password (e.g. `abcd efgh ijkl mnop`)

### Email Channel Connect Form

Go to `Settings → Channels → Email → Connect` and fill:

| Field | Value |
|-------|-------|
| Channel Name | My Gmail (or any name) |
| From Email | `yourname@gmail.com` |
| SMTP Password | *(16-char App Password from above)* |
| SMTP Host | `smtp.gmail.com` *(pre-filled)* |
| SMTP Port | `587` *(pre-filled)* |
| SMTP User | `yourname@gmail.com` |

Click **Connect** → channel is now active.

---

## Part 3 — Sending a Reply (Outbound Flow)

1. Open `http://localhost:3000/inbox`
2. Click any email conversation
3. In the composer at the bottom → type your reply
4. Make sure **"Reply"** tab is selected (not "Internal Note")
5. Press **Send** (or `Cmd+Enter`)

The reply goes out via SMTP (Gmail) and lands in the customer's inbox.

```
Agent types reply in Inbox
        ↓
POST /api/v1/inbox/conversations/{id}/messages
        ↓
Backend → EmailAdapter.send()
        ↓
SMTP → smtp.gmail.com:587
        ↓
Customer's Email Inbox
```

---

## Part 4 — Testing End-to-End

### Test Inbound
1. Ask a friend to send an email to your Gmail address
2. Wait 10–30 seconds
3. Check `http://localhost:3000/inbox` — conversation should appear

### Test Outbound
1. Open the conversation in inbox
2. Type a reply → Send
3. Friend checks their inbox — reply should arrive from your Gmail

### Check Cloudmailin Logs (if email not arriving)
- Cloudmailin Dashboard → **Messages** tab
- Status should be **200** — if 404/500, webhook URL is wrong
- If no messages appear — Gmail forwarding is not enabled

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Email not in inbox | Gmail forwarding disabled | Gmail Settings → Forwarding → Enable |
| Email not in inbox | Cloudmailin wrong URL | Set URL to `/webhooks/email` (not `/api/v1/webhooks/email`) |
| Email not in inbox | No Email channel connected | Settings → Channels → Email → Connect |
| Reply not sending | SMTP not configured | Connect email channel with App Password |
| Reply not sending | Wrong App Password | Regenerate App Password from Google Account |
| 401 error in app | Session cookie issue | Hard refresh (Ctrl+Shift+R) → re-login |

---

## Current Setup (Your Config)

- **Cloudmailin Address**: `a76f8e1002e6020cef25@cloudmailin.net`
- **Webhook URL**: `https://ucaas-api-919679113744.asia-south1.run.app/webhooks/email`
- **Gmail**: Forward all incoming mail to Cloudmailin ✅
- **SMTP Host**: `smtp.gmail.com:587`
