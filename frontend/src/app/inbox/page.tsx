"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useWebSocket, type RealtimeEvent } from "@/contexts/WebSocketContext";
import { ConversationList } from "@/components/inbox/ConversationList";
import { MessageThread } from "@/components/messages/MessageThread";
import { MessageComposer } from "@/components/messages/MessageComposer";
import { AssignmentDropdown } from "@/components/inbox/AssignmentDropdown";
import {
  addNote,
  fetchConversations,
  fetchMessages,
  sendMessage,
  type Conversation,
  type Message,
} from "@/lib/inbox";
import { cn, getInitials, getAvatarColor } from "@/lib/utils";
import { HiArrowLeft } from "react-icons/hi";
import { RiWhatsappFill } from "react-icons/ri";
import { HiMail, HiChat, HiDotsVertical } from "react-icons/hi";

const CHANNEL_META: Record<string, { label: string; icon: React.ElementType; color: string }> = {
  whatsapp: { label: "WhatsApp", icon: RiWhatsappFill, color: "text-emerald-600 bg-emerald-50 border-emerald-200" },
  email: { label: "Email", icon: HiMail, color: "text-blue-600 bg-blue-50 border-blue-200" },
  webchat: { label: "Web Chat", icon: HiChat, color: "text-violet-600 bg-violet-50 border-violet-200" },
};

const STATUS_COLORS: Record<string, string> = {
  open: "bg-emerald-100 text-emerald-700",
  resolved: "bg-slate-100 text-slate-600",
  pending: "bg-amber-100 text-amber-700",
};

export default function InboxPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const { connected, subscribe } = useWebSocket();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [active, setActive] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  // Mobile: show thread panel when a conversation is selected
  const [showThread, setShowThread] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [loading, user, router]);

  const loadConversations = useCallback(async () => {
    setConversations(await fetchConversations());
  }, []);

  const loadMessages = useCallback(async (conversationId: string) => {
    setMessages(await fetchMessages(conversationId));
  }, []);

  useEffect(() => {
    if (user) void loadConversations();
  }, [user, loadConversations]);

  useEffect(() => {
    const unsub = subscribe((event: RealtimeEvent) => {
      if (["message_created", "message_updated", "assignment_changed"].includes(event.type)) {
        void loadConversations();
        const convId = event.data?.conversation_id as string | undefined;
        if (active && convId === active.id) void loadMessages(active.id);
      }
    });
    return unsub;
  }, [subscribe, active, loadConversations, loadMessages]);

  const onSelect = async (c: Conversation) => {
    setActive(c);
    await loadMessages(c.id);
    setShowThread(true);
  };

  const onBack = () => {
    setShowThread(false);
  };

  const onSend = async (content: string) => {
    if (!active) return;
    await sendMessage(active.id, content);
    await loadMessages(active.id);
  };

  const onAddNote = async (content: string) => {
    if (!active) return;
    await addNote(active.id, content);
    await loadMessages(active.id);
  };

  if (loading || !user) return null;

  const contactName =
    active?.contact.full_name ||
    active?.contact.email ||
    active?.contact.phone ||
    "Unknown";

  const statusColor = active ? (STATUS_COLORS[active.status] ?? "bg-slate-100 text-slate-600") : "";

  return (
    <div className="flex h-full overflow-hidden bg-background">
      {/* ── Conversation list panel ── */}
      <div
        className={cn(
          "flex h-full flex-col",
          // Mobile: full width, hidden when thread is shown
          "w-full sm:w-80 lg:w-96",
          showThread ? "hidden sm:flex" : "flex"
        )}
      >
        <ConversationList
          conversations={conversations}
          activeId={active?.id ?? null}
          onSelect={onSelect}
          currentUserId={user.id}
        />
      </div>

      {/* ── Thread panel ── */}
      <div
        className={cn(
          "flex min-w-0 flex-1 flex-col overflow-hidden",
          // Mobile: full width, shown only when thread is open
          showThread ? "flex" : "hidden sm:flex"
        )}
      >
        {active ? (
          <>
            {/* Conversation header */}
            <header className="flex shrink-0 items-center gap-3 border-b bg-card px-4 py-3">
              {/* Mobile back button */}
              <button
                onClick={onBack}
                className="rounded-md p-1.5 hover:bg-secondary transition-colors sm:hidden"
                aria-label="Back to conversations"
              >
                <HiArrowLeft className="h-5 w-5" />
              </button>

              {/* Contact avatar */}
              <div
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
                style={{ backgroundColor: getAvatarColor(active.contact.id) }}
              >
                {getInitials(contactName)}
              </div>

              {/* Contact info */}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="truncate text-sm font-semibold">{contactName}</p>
                  {/* Status badge */}
                  <span
                    className={cn(
                      "hidden rounded-full px-2 py-0.5 text-[11px] font-medium capitalize sm:inline-block",
                      statusColor
                    )}
                  >
                    {active.status}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      "text-[11px]",
                      connected ? "text-emerald-600" : "text-muted-foreground"
                    )}
                  >
                    {connected ? "● Live" : "○ Reconnecting…"}
                  </span>
                  {active.contact.email && (
                    <span className="hidden text-[11px] text-muted-foreground sm:block">
                      · {active.contact.email}
                    </span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex shrink-0 items-center gap-2">
                <AssignmentDropdown
                  conversationId={active.id}
                  assignedToUserId={active.assigned_to_user_id}
                  onChanged={loadConversations}
                />
                <button className="rounded-md p-1.5 hover:bg-secondary transition-colors text-muted-foreground">
                  <HiDotsVertical className="h-4 w-4" />
                </button>
              </div>
            </header>

            {/* Messages */}
            <MessageThread
              messages={messages}
              contactName={contactName}
              contactId={active.contact.id}
              agentName={user.full_name ?? user.email}
              agentId={user.id}
            />

            {/* Composer */}
            <MessageComposer onSend={onSend} onAddNote={onAddNote} />
          </>
        ) : (
          /* Empty state — no conversation selected */
          <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-secondary">
              <HiChat className="h-9 w-9 text-muted-foreground" />
            </div>
            <div>
              <p className="text-base font-semibold">No conversation selected</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Choose a conversation from the list to view messages
              </p>
            </div>
            {/* Channel quick-links */}
            <div className="mt-2 flex flex-wrap justify-center gap-2">
              {Object.entries(CHANNEL_META).map(([key, { label, icon: Icon, color }]) => (
                <span
                  key={key}
                  className={cn(
                    "flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium",
                    color
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                  {label}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
