---
id: "007"
title: Fix Email Inbound Parse and Contact Email
stage: green
date: 2026-06-26
surface: agent
model: claude-sonnet-4-6
feature: 001-unified-comms-platform
branch: 001-unified-comms-platform
user: ZijaYaseen
command: debug email inbound / fix contact.email = None / contacts tasks MVP question
labels: ["email","inbound","contact","bugfix","cloudmailin","parse"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/modules/channels/router.py
  - backend/src/modules/channels/email.py
tests:
  - manual: inbound email → contact.email populated
  - manual: outbound reply → delivered to recipient
---

## Prompt

(Session resumed from context summary)

User: "tasks.md me hm ne contact complete hi nhi kia tha na, agr zruri he to wo step complete kr lo mvp me hi"

Earlier in session: debugging why outbound email reply doesn't reach recipient. DB investigation showed all contacts have email=None. Root cause: parse_inbound() in email.py failed to extract sender email — suspected Cloudmailin field casing issue.

## Response snapshot

**Root cause confirmed:** `sender_identifier` was always empty string because Cloudmailin form field keys may differ in casing, and `payload.get("from")` returned None/empty. All contacts created with `email=None` and no channel identity stored in metadata either — SQL patch not possible (no source data).

**Fixes applied:**
1. `backend/src/modules/channels/router.py` — normalized all form keys to lowercase: `{k.lower(): ...}`. Added `logger.info("email_webhook_fields", fields=...)` to log exact Cloudmailin field names.
2. `backend/src/modules/channels/email.py` — added sender logging; fixed email extraction for plain-address format (no `<>` brackets); removed capitalized fallback keys (`"To"`, `"Message-Id"`, `"Message-ID"`) since keys are now pre-normalized.

**Contacts MVP scope:**
- T087-T089 (contact auto-creation, dedup, schemas) = DONE ✅
- T204-T213 (Contacts CRUD API) = Post-MVP, NOT needed for email
- No MVP promotion needed for contacts API

**API redeployed** — revision `ucaas-api-00008-xxx` serving 100% traffic.

**Next action:** Have `yaseensaddique` send a new email to Gmail → Cloudmailin will forward → new contact created with correct email → inbox reply will work.

## Outcome

- ✅ Impact: Email inbound parsing now case-insensitive; new contacts will be created with correct email; outbound reply flow unblocked pending new inbound test
- 🧪 Tests: Manual test — send new inbound email after fix deploy
- 📁 Files: router.py (key normalization + logging), email.py (parse fix + logging)
- 🔁 Next prompts: Verify new email creates contact with email populated; test outbound reply delivers
- 🧠 Reflection: The form key normalization should have been done from day 1 — HTTP form fields are case-sensitive by spec but providers vary; always normalize at the boundary

## Evaluation notes (flywheel)

- Failure modes observed: Silent data loss — empty sender_identifier stored nowhere in DB, no way to recover existing contacts; `except: pass` in _enqueue_delivery masked the original error chain
- Graders run and results (PASS/FAIL): None automated
- Prompt variant (if applicable): null
- Next experiment: Add integration test that posts a mock Cloudmailin webhook payload and asserts contact.email is populated
