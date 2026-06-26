"use client";

import { useState, useMemo } from "react";
import { ConversationItem } from "@/components/inbox/ConversationItem";
import type { Conversation } from "@/lib/inbox";
import { HiSearch, HiFilter } from "react-icons/hi";
import { cn } from "@/lib/utils";

type Filter = "all" | "open" | "mine" | "resolved";

const TABS: { key: Filter; label: string }[] = [
  { key: "all", label: "All" },
  { key: "open", label: "Open" },
  { key: "mine", label: "Mine" },
  { key: "resolved", label: "Resolved" },
];

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  currentUserId,
}: {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (c: Conversation) => void;
  currentUserId?: string;
}) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<Filter>("all");

  const filtered = useMemo(() => {
    let list = conversations;
    if (filter === "open") list = list.filter((c) => c.status === "open");
    if (filter === "resolved") list = list.filter((c) => c.status === "resolved");
    if (filter === "mine") list = list.filter((c) => c.assigned_to_user_id === currentUserId);
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (c) =>
          c.contact.full_name?.toLowerCase().includes(q) ||
          c.contact.email?.toLowerCase().includes(q) ||
          c.contact.phone?.toLowerCase().includes(q) ||
          c.last_message_preview?.toLowerCase().includes(q)
      );
    }
    return list;
  }, [conversations, filter, search, currentUserId]);

  const openCount = conversations.filter((c) => c.status === "open").length;

  return (
    <div className="flex h-full w-full flex-col border-r bg-card">
      {/* Header */}
      <div className="shrink-0 border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold">Conversations</h2>
            {openCount > 0 && (
              <span className="rounded-full bg-primary px-2 py-0.5 text-[11px] font-semibold text-primary-foreground">
                {openCount}
              </span>
            )}
          </div>
          <button className="rounded-md p-1.5 hover:bg-secondary transition-colors text-muted-foreground">
            <HiFilter className="h-4 w-4" />
          </button>
        </div>

        {/* Search */}
        <div className="relative mt-2.5">
          <HiSearch className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search conversations…"
            className="w-full rounded-lg border bg-background py-2 pl-9 pr-3 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-ring placeholder:text-muted-foreground"
          />
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex shrink-0 border-b">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={cn(
              "flex-1 py-2 text-xs font-medium transition-colors",
              filter === tab.key
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-secondary">
              <HiSearch className="h-5 w-5 text-muted-foreground" />
            </div>
            <p className="text-sm font-medium">No conversations found</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {search ? "Try a different search term" : "New conversations will appear here"}
            </p>
          </div>
        ) : (
          filtered.map((c) => (
            <ConversationItem
              key={c.id}
              conversation={c}
              active={c.id === activeId}
              onClick={() => onSelect(c)}
            />
          ))
        )}
      </div>
    </div>
  );
}
