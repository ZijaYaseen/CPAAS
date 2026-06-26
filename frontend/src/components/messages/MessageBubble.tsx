import { cn, formatTime, getInitials, getAvatarColor } from "@/lib/utils";
import type { Message } from "@/lib/inbox";
import { HiSparkles } from "react-icons/hi2";
import { RiStickyNoteFill } from "react-icons/ri";

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
      className={cn(
        "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[11px] font-bold text-white",
        getAvatarColor(id)
      )}
    >
      {getInitials(name)}
    </div>
  );
}

export function MessageBubble({ message }: { message: Message }) {
  const isOutbound = message.direction === "outbound";
  const isAI = message.sender_type === "ai_agent";

  // Internal note
  if (message.is_internal_note) {
    return (
      <div className="my-3 flex items-start gap-2 px-4">
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-amber-100 mt-0.5">
          <RiStickyNoteFill className="h-3 w-3 text-amber-600" />
        </div>
        <div className="flex-1 rounded-xl rounded-tl-sm border border-amber-200 bg-amber-50 px-3.5 py-2.5">
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-amber-700">
            Internal Note
          </p>
          <p className="text-sm text-amber-900 whitespace-pre-wrap break-words">{message.content}</p>
          <p className="mt-1.5 text-[11px] text-amber-600/70">{formatTime(message.created_at)}</p>
        </div>
      </div>
    );
  }

  // Inbound (customer or AI)
  if (!isOutbound) {
    return (
      <div className="my-1.5 flex items-end gap-2 px-4">
        <SenderAvatar
          name={isAI ? "AI Agent" : "Contact"}
          id={message.sender_id ?? message.conversation_id}
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
  return (
    <div className="my-1.5 flex flex-row-reverse items-end gap-2 px-4">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-[11px] font-bold text-primary-foreground">
        Me
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
