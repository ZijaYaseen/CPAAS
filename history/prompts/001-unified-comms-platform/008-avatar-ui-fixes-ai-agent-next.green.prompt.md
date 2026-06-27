---
id: 008
title: Avatar UI Fixes & AI Agent Next Steps
stage: green
date: 2026-06-27
surface: agent
model: claude-sonnet-4-6
feature: 001-unified-comms-platform
branch: 001-unified-comms-platform
user: zijayaseen15@gmail.com
command: fix avatar display, update tasks.md
labels: ["avatar", "ui", "inbox", "ai-agents", "tasks"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/lib/utils.ts
  - frontend/src/components/messages/MessageBubble.tsx
  - frontend/src/components/messages/MessageThread.tsx
  - frontend/src/components/inbox/ConversationItem.tsx
  - frontend/src/app/inbox/page.tsx
  - specs/001-unified-comms-platform/tasks.md
tests:
  - npx tsc --noEmit (0 errors)
---

## Prompt

Avatar/profile icons fix karo — inbound messages k saath contact initials nazar nahi aa rahe, outbound pe "Me" hardcoded hai, aur colors light lag rahi hain. Tasks.md update karo completed work ke sath aur AI agents ko next priority banao.

## Response snapshot

1. **Root cause of invisible avatars**: `getAvatarColor()` Tailwind class strings return karta tha (`bg-violet-500`) lekin `src/lib/utils.ts` Tailwind content scan paths mein nahi tha (`src/pages`, `src/components`, `src/app` scan hota tha). Classes purge ho jaati theen / generate nahi hoti theen.

2. **Fix**: `getAvatarColor` ko hex colors return karne ke liye update kiya (`#7c3aed`, `#2563eb`, etc.). Sab jagah `className={getAvatarColor(...)}` → `style={{ backgroundColor: getAvatarColor(...) }}`.

3. **Contact initials in messages**: `MessageBubble` mein `contactName`/`contactId` aur `agentName`/`agentId` props add kiye. `MessageThread` props forward karta hai. `inbox/page.tsx` `active.contact` aur `user` info pass karta hai.

4. **Avatar alignment**: `items-end` (avatar below bubble due to timestamp height) → `items-center` (avatar centered with bubble).

5. **tasks.md**: S-24 through S-46 added (email parser, WhatsApp WABA, MessageComposer, internal notes UI, channel icons, avatar system, docs). RESUME HERE section replaced with AI-1 through AI-17 steps for AI agent tuning.

## Outcome

- ✅ Impact: Contact initials correctly shown next to inbound messages; agent initials next to outbound; header avatar visible with strong colors
- 🧪 Tests: TypeScript check passed (0 errors)
- 📁 Files: 6 files modified
- 🔁 Next prompts: AI agent tuning — knowledge base upload, support agent prompt, end-to-end test
- 🧠 Reflection: Tailwind content scan paths must include all files that define class names dynamically. Inline styles are more reliable for runtime-computed colors.

## Evaluation notes (flywheel)

- Failure modes observed: Tailwind purging dynamic classes from files outside content paths
- Graders run and results (PASS/FAIL): tsc --noEmit PASS
- Prompt variant (if applicable): null
- Next experiment: Add src/lib/** to Tailwind content as permanent fix (alternative to inline styles)
