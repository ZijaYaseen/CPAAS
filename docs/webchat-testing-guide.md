# Web Chat Testing Guide

> Yeh guide client demo ya internal testing ke liye hai.
> Sab curl commands copy-paste ready hain.

---

## Session kya hota hai?

**Session = ek visitor ki unique identity.**

Jab koi user tumhara web chat widget open karta hai, usse ek `session_id` assign hoti hai. Yeh ek random string hoti hai jo:

- Ek visitor ke saare messages ko ek hi **conversation** mein group karti hai
- Agar same `session_id` se 2 messages aate hain → inbox mein **ek hi conversation** mein dikhte hain
- Agar alag `session_id` se message aata hai → inbox mein **nayi alag conversation** banti hai

**Real widget mein:** `session_id` automatically browser localStorage mein save hoti hai, toh visitor ke saare messages ek conversation mein aate hain.

**Testing mein:** Tum khud `session_id` set karte ho (koi bhi string chalegi).

---

## Prerequisites

1. Docker stack running hona chahiye:
   ```bash
   docker-compose up -d redis backend worker
   ```
2. Frontend running hona chahiye:
   ```bash
   cd frontend && npm run dev
   ```
3. Browser mein login karo: `http://localhost:3000/login`
4. Inbox open karo: `http://localhost:3000/inbox`

---

## Step 1 — Channel ID Lena

Channel ID woh UUID hai jo tumne Web Chat channel create karte waqt mili thi.

**Settings se dekhna:**
```
http://localhost:3000/settings/channels
```
→ Web Chat section → Channel ID copy karo

**Ya API se lena (agar logged in ho):**
```bash
curl -s http://localhost:8000/api/v1/channels \
  -H "Cookie: ucaas_session=TUMHARI_SESSION_COOKIE"
```

**Is project ki test Channel ID:**
```
6832096d-e8ec-433f-bb1d-c9891ea5a377
```

---

## Step 2 — Basic Message Bhejna

Yeh sabse simple test hai:

```bash
curl -X POST "http://localhost:8000/api/v1/webchat/messages" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "channel_account_id": "6832096d-e8ec-433f-bb1d-c9891ea5a377",
    "session_id": "test-session-001",
    "content": "Hello! Mujhe help chahiye.",
    "visitor_name": "Test User"
  }'
```

**Expected Response:**
```json
{"status": "received", "message_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
```

**Inbox mein check karo** → Message bina refresh ke aana chahiye (real-time).

---

## Step 3 — Multiple Messages (Same Conversation)

Same `session_id` use karo — sab messages ek hi conversation mein aayenge:

```bash
# Message 1
curl -X POST "http://localhost:8000/api/v1/webchat/messages" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "channel_account_id": "6832096d-e8ec-433f-bb1d-c9891ea5a377",
    "session_id": "test-session-001",
    "content": "Mera order kahan hai?",
    "visitor_name": "Ahmed Khan"
  }'

# Message 2 (same session → same conversation)
curl -X POST "http://localhost:8000/api/v1/webchat/messages" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "channel_account_id": "6832096d-e8ec-433f-bb1d-c9891ea5a377",
    "session_id": "test-session-001",
    "content": "Order ID: ORD-12345",
    "visitor_name": "Ahmed Khan"
  }'
```

---

## Step 4 — Alag Visitor (New Conversation)

Alag `session_id` = nayi alag conversation inbox mein:

```bash
curl -X POST "http://localhost:8000/api/v1/webchat/messages" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "channel_account_id": "6832096d-e8ec-433f-bb1d-c9891ea5a377",
    "session_id": "test-session-002",
    "content": "Hi, I need to return my product.",
    "visitor_name": "Sara Ali"
  }'
```

**Inbox mein:** Ahmed Khan aur Sara Ali — **2 alag conversations** dikhni chahiye.

---

## Step 5 — Optional Fields

```bash
curl -X POST "http://localhost:8000/api/v1/webchat/messages" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "channel_account_id": "6832096d-e8ec-433f-bb1d-c9891ea5a377",
    "session_id": "test-session-003",
    "content": "Payment mein issue aa raha hai.",
    "visitor_name": "Bilal Ahmed",
    "page_url": "https://yoursite.com/checkout",
    "client_message_id": "msg-xyz-001"
  }'
```

| Field | Required | Description |
|-------|----------|-------------|
| `channel_account_id` | ✅ Yes | Web Chat channel ka UUID |
| `session_id` | ✅ Yes | Visitor ki unique identity (koi bhi string) |
| `content` | ✅ Yes | Message text |
| `visitor_name` | ❌ Optional | Inbox mein contact naam dikhega |
| `page_url` | ❌ Optional | Visitor kis page pe tha |
| `client_message_id` | ❌ Optional | Duplicate prevention ke liye |

---

## Step 6 — Real-Time Verify Karna

1. **Inbox open karo** (`http://localhost:3000/inbox`) — page refresh mat karo
2. Naya terminal/tab mein curl chalao
3. Message inbox mein **automatically** aana chahiye (2-3 seconds mein)
4. Header mein **`● Live`** (green) dikhna chahiye — iska matlab WebSocket connected hai

Agar **`○ Reconnecting…`** dikh raha hai → login session expire ho gayi, dobara login karo.

---

## Step 7 — Reply Karna (Inbox se)

1. Inbox mein conversation click karo
2. Neeche composer mein reply type karo
3. **Cmd+Enter** ya Send button → reply visitor tak pahunchti hai

---

## Ek Sath Saara Test (Full Demo Script)

```bash
# ---- Visitor 1: Ahmed Khan ----
curl -X POST "http://localhost:8000/api/v1/webchat/messages" \
  -H "Content-Type: application/json" \
  --data-raw '{"channel_account_id":"6832096d-e8ec-433f-bb1d-c9891ea5a377","session_id":"demo-ahmed","content":"Assalam o Alaikum, mujhe help chahiye!","visitor_name":"Ahmed Khan"}'

sleep 2

curl -X POST "http://localhost:8000/api/v1/webchat/messages" \
  -H "Content-Type: application/json" \
  --data-raw '{"channel_account_id":"6832096d-e8ec-433f-bb1d-c9891ea5a377","session_id":"demo-ahmed","content":"Mera refund kab aayega?","visitor_name":"Ahmed Khan"}'

# ---- Visitor 2: Sara Ali ----
curl -X POST "http://localhost:8000/api/v1/webchat/messages" \
  -H "Content-Type: application/json" \
  --data-raw '{"channel_account_id":"6832096d-e8ec-433f-bb1d-c9891ea5a377","session_id":"demo-sara","content":"Hi, product quality issue hai.","visitor_name":"Sara Ali"}'
```

**Expected inbox result:** 2 conversations (Ahmed Khan + Sara Ali), real-time, no refresh.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `{"detail":"There was an error parsing the body"}` | Special characters in content | Simple English/Urdu use karo, avoid `"` quotes inside |
| `{"detail":[{"msg":"Field required"...}]}` | Required field missing | `channel_account_id` aur `session_id` zaroor do |
| Message inbox mein nahi aaya | Docker down hai | `docker-compose up -d redis backend worker` |
| `● Reconnecting…` dikh raha hai | Session expire | Logout → Login karo |
| Message dikh raha hai par real-time nahi | Bug tha | Fixed ✅ (commit-before-emit, 2026-06-25) |

---

## Naya Channel ID Banana (Agar Zaroorat Pade)

```
http://localhost:3000/settings/channels
→ Web Chat → "Create New Channel" → Name: "Test Widget"
→ Channel ID copy karo → Upar ki commands mein replace karo
```

---

*Last updated: 2026-06-25 | Fix: real-time race condition resolved (commit before WebSocket emit)*
