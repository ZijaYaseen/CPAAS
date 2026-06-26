import { cn, formatTime, getInitials, getAvatarColor } from "@/lib/utils";
import type { Message } from "@/lib/inbox";
import { HiSparkles, HiLockClosed } from "react-icons/hi2";
import { RiRobotLine, RiUserReceivedLine } from "react-icons/ri";

function SenderAvatar({ name, id, isAI }: { name: string; id: string; isAI?: boolean }) {
  if (isAI) {
    return (
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-100">
        <HiSparkles className="h-3.5 w-3.5 text-indigo-600" />
      </div>
    );
  }
  return (
    <div
      className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[11px] font-bold text-white"
      style={{ backgroundColor: getAvatarColor(id) }}
    >
      {getInitials(name)}
    </div>
  );
}

function isSystemNote(content: string | null) {
  if (!content) return false;
  return content.startsWith("🤖") || content.includes("AI escalated") || content.includes("AI run error");
}

export function MessageBubble({
  message,
  contactName,
  contactId,
  agentName,
  agentId,
}: {
  message: Message;
  contactName?: string;
  contactId?: string;
  agentName?: string;
  agentId?: string;
}) {
  const isOutbound = message.direction === "outbound";
  const isAI = message.sender_type === "ai_agent";

  // Internal note
  if (message.is_internal_note) {
    const content = message.content ?? "";

    // AI system events → compact centered pill
    if (isSystemNote(content)) {
      const isEscalation = content.includes("escalated");
      return (
        <div className="my-1.5 flex items-center justify-center px-4">
          <div className="flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] text-slate-400 shadow-sm">
            {isEscalation
              ? <RiUserReceivedLine className="h-3 w-3 shrink-0" />
              : <RiRobotLine className="h-3 w-3 shrink-0" />
            }
            <span>{content.replace("🤖 ", "")}</span>
            <span className="text-slate-300">·</span>
            <span>{formatTime(message.created_at)}</span>
          </div>
        </div>
      );
    }

    // Human internal note — Intercom/Freshdesk style
    const agentLabel = message.sender_type === "ai_agent" ? "AI Agent" : "You";
    const avatarId = message.sender_id ?? message.conversation_id;

    return (
      <div className="my-3 px-4">
        <div className="relative overflow-hidden rounded-xl border border-amber-200 bg-amber-50/60 shadow-sm">
          {/* Left accent bar */}
          <div className="absolute bottom-0 left-0 top-0 w-[3px] bg-amber-400" />

          <div className="px-4 pb-3 pl-5 pt-3">
            {/* Header row */}
            <div className="mb-2 flex items-center gap-2">
              <div
                className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
                style={{ backgroundColor: getAvatarColor(avatarId) }}
              >
                {getInitials(agentLabel)}
              </div>
              <span className="text-xs font-semibold text-amber-900">{agentLabel}</span>
              <span className="text-[11px] text-amber-600/70">left a note</span>
              <div className="ml-auto flex items-center gap-1">
                <HiLockClosed className="h-2.5 w-2.5 text-amber-400" />
                <span className="text-[10px] font-medium text-amber-500">Private</span>
                <span className="mx-0.5 text-amber-300">·</span>
                <span className="text-[11px] text-amber-600/70">{formatTime(message.created_at)}</span>
              </div>
            </div>

            {/* Content */}
            <p className="text-sm leading-relaxed text-amber-950 whitespace-pre-wrap break-words">
              {content}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Inbound (customer or AI)
  if (!isOutbound) {
    const inboundName = isAI ? "AI Agent" : (contactName ?? "?");
    const inboundId = isAI
      ? (message.sender_id ?? message.conversation_id)
      : (contactId ?? message.sender_id ?? message.conversation_id);
    return (
      <div className="my-1.5 flex items-center gap-2 px-4">
        <SenderAvatar
          name={inboundName}
          id={inboundId}
          isAI={isAI}
        />
        <div className="max-w-[72%]">
          {isAI && (
            <p className="mb-1 text-[11px] font-medium text-indigo-600">AI Agent</p>
          )}
          <div
            className={cn(
              "rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm shadow-sm",
              isAI
                ? "bg-indigo-50 text-indigo-900 border border-indigo-100"
                : "bg-secondary text-foreground"
            )}
          >
            <p className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
          </div>
          <p className="mt-1 pl-1 text-[11px] text-muted-foreground">{formatTime(message.created_at)}</p>
        </div>
      </div>
    );
  }

  // Outbound (agent reply)
  const outboundLabel = agentName ?? "Me";
  const outboundId = agentId ?? message.sender_id ?? message.conversation_id;
  return (
    <div className="my-1.5 flex flex-row-reverse items-center gap-2 px-4">
      <div
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[11px] font-bold text-white"
        style={{ backgroundColor: getAvatarColor(outboundId) }}
      >
        {getInitials(outboundLabel)}
      </div>
      <div className="max-w-[72%]">
        <div className="rounded-2xl rounded-br-sm bg-primary px-4 py-2.5 text-sm text-primary-foreground shadow-sm">
          <p className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
        </div>
        <div className="mt-1 flex items-center justify-end gap-1.5 pr-1">
          <p className="text-[11px] text-muted-foreground">{formatTime(message.created_at)}</p>
          {message.latest_status && (
            <span className="text-[11px] text-muted-foreground capitalize">
              · {message.latest_status}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
