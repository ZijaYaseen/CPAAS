"use client";

import { cn, timeAgo, getInitials, getAvatarColor } from "@/lib/utils";
import type { Conversation } from "@/lib/inbox";
import { RiWhatsappFill } from "react-icons/ri";
import { HiMail, HiChat } from "react-icons/hi";

const STATUS_DOT: Record<string, string> = {
  open: "bg-emerald-500",
  pending: "bg-amber-400",
  resolved: "bg-slate-400",
  snoozed: "bg-blue-400",
};

const CHANNEL_META: Record<string, { label: string; icon: React.ElementType; color: string }> = {
  whatsapp: { label: "WhatsApp", icon: RiWhatsappFill, color: "text-emerald-600 bg-emerald-50" },
  email: { label: "Email", icon: HiMail, color: "text-blue-600 bg-blue-50" },
  webchat: { label: "Web Chat", icon: HiChat, color: "text-violet-600 bg-violet-50" },
};

export function ConversationItem({
  conversation,
  active,
  channelType,
  onClick,
}: {
  conversation: Conversation;
  active: boolean;
  channelType?: string;
  onClick: () => void;
}) {
  const name =
    conversation.contact.full_name ||
    conversation.contact.email ||
    conversation.contact.phone ||
    "Unknown";

  const initials = getInitials(name);
  const avatarColor = getAvatarColor(conversation.contact.id);
  const statusDot = STATUS_DOT[conversation.status] ?? "bg-slate-400";
  const channel = channelType ? CHANNEL_META[channelType] : null;
  const ChIcon = channel?.icon;

  return (
    <button
      onClick={onClick}
      className={cn(
        "group relative flex w-full items-start gap-3 px-4 py-3.5 text-left transition-colors",
        "border-b border-border/60 hover:bg-secondary/60",
        active ? "bg-primary/5 border-l-2 border-l-primary hover:bg-primary/5" : "border-l-2 border-l-transparent"
      )}
    >
      {/* Avatar */}
      <div className="relative shrink-0">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold text-white shadow-sm"
          style={{ backgroundColor: avatarColor }}
        >
          {initials}
        </div>
        {/* Channel icon badge */}
        {ChIcon && (
          <div
            className={cn(
              "absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full ring-2 ring-card",
              channel!.color
            )}
          >
            <ChIcon className="h-2.5 w-2.5" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <span className={cn("truncate text-sm", active ? "font-semibold" : "font-medium")}>
            {name}
          </span>
          <span className="shrink-0 text-[11px] text-muted-foreground">
            {timeAgo(conversation.last_message_at ?? conversation.created_at)}
          </span>
        </div>

        <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">
          {conversation.last_message_preview ?? "No messages yet"}
        </p>

        {/* Footer row */}
        <div className="mt-1.5 flex items-center gap-2">
          <span className={cn("h-1.5 w-1.5 rounded-full shrink-0", statusDot)} />
          <span className="text-[11px] capitalize text-muted-foreground">{conversation.status}</span>
          {conversation.assigned_to_user_id && (
            <span className="ml-auto rounded-full bg-secondary px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
              Assigned
            </span>
          )}
        </div>
      </div>
    </button>
  );
}
