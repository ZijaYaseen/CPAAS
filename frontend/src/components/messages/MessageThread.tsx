"use client";

import { useEffect, useRef } from "react";
import { MessageBubble } from "@/components/messages/MessageBubble";
import { formatDateSeparator } from "@/lib/utils";
import type { Message } from "@/lib/inbox";
import { HiChat } from "react-icons/hi";

function isSameDay(a: string, b: string) {
  return new Date(a).toDateString() === new Date(b).toDateString();
}

export function MessageThread({
  messages,
  contactName,
  contactId,
  agentName,
  agentId,
}: {
  messages: Message[];
  contactName?: string;
  contactId?: string;
  agentName?: string;
  agentId?: string;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center px-6">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-secondary">
          <HiChat className="h-6 w-6 text-muted-foreground" />
        </div>
        <p className="text-sm font-medium text-muted-foreground">No messages yet</p>
        <p className="text-xs text-muted-foreground">Send a message to start the conversation</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto py-4">
      {messages.map((m, i) => {
        const showDateSep = i === 0 || !isSameDay(m.created_at, messages[i - 1].created_at);
        return (
          <div key={m.id}>
            {showDateSep && (
              <div className="my-4 flex items-center gap-3 px-6">
                <div className="h-px flex-1 bg-border" />
                <span className="rounded-full border bg-card px-3 py-1 text-[11px] font-medium text-muted-foreground">
                  {formatDateSeparator(m.created_at)}
                </span>
                <div className="h-px flex-1 bg-border" />
              </div>
            )}
            <MessageBubble
              message={m}
              contactName={contactName}
              contactId={contactId}
              agentName={agentName}
              agentId={agentId}
            />
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
