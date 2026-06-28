---
id: "010"
title: Fix Web Chat Embed Script Display
stage: green
date: 2026-06-28
surface: agent
model: claude-sonnet-4-6
feature: 001-unified-comms-platform
branch: main
user: ZijaYaseen
command: fix webchat embed script not showing after widget creation
labels: ["webchat","ui","bug-fix","channels"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/settings/channels/page.tsx
tests:
  - manual: create widget → script shows immediately
  - manual: existing connected widget → Get Script button expands script
  - manual: API failure → red error message shown
---

## Prompt

Web Chat widget create karne ke baad embed script nahi aa rahi. User ne screenshot share kiya jisme "Testing" name daala tha lekin script nazar nahi aa rahi thi. User ne ye bhi pucha:
1. Create hone se pehle aata he kia script?
2. Real world me kese hota he ye?
3. Edit ka option q nahi a rha UI par create karne ke baad — pehle to tha

## Response snapshot

Three issues fixed in `frontend/src/app/settings/channels/page.tsx`:

1. **Silent failure bug** — `submit()` had no catch block; API errors were silently swallowed. Added try-catch with `error` state that renders a red error banner.

2. **Script inaccessible after closing panel** — The script only appeared transiently in the success screen. If user closed the panel or refreshed, there was no way to get the script again. Fixed by:
   - Extracting `WebChatEmbedScript` as a standalone component
   - Adding `scriptChannelId` state to `ChannelsPage`
   - Replacing the hidden Edit button with a **"Get Script"** button (HiCode icon) in the connected channel list for webchat channels
   - Clicking it toggles an inline `WebChatEmbedScript` panel below that row

3. **Edit button missing** — Webchat has no credentials (no API key/token), so Edit was intentionally hidden. Now replaced with the Get Script button which is the correct action for webchat.

Answered user's questions:
- Script only appears AFTER creation (needs the generated channel ID)
- Real-world pattern: Intercom/Crisp/Tidio all show script immediately after creation + accessible from settings anytime

## Outcome

- ✅ Impact: Webchat embed script now always accessible — both immediately after creation and from the connected channel list at any time
- 🧪 Tests: Manual UI test required (create widget, check script appears; click Get Script on existing widget)
- 📁 Files: 1 file modified (channels page)
- 🔁 Next prompts: Test tenant isolation end-to-end; email inbound setup
- 🧠 Reflection: Silent failures in async form handlers are a common pattern to miss — always add catch with user-visible error state

## Evaluation notes (flywheel)

- Failure modes observed: No catch block in async submit → silent failures; transient success state lost on panel close
- Graders run and results (PASS/FAIL): TypeScript tsc --noEmit → PASS (no errors)
- Prompt variant (if applicable): null
- Next experiment: Consider moving embed script to a modal for better discoverability
