"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";
import { HiUserAdd, HiUserRemove } from "react-icons/hi";

export function AssignmentDropdown({
  conversationId,
  assignedToUserId,
  onChanged,
}: {
  conversationId: string;
  assignedToUserId: string | null;
  onChanged: () => void;
}) {
  const { user } = useAuth();
  const [busy, setBusy] = useState(false);
  const assignedToMe = !!(assignedToUserId && user && assignedToUserId === user.id);

  const toggle = async () => {
    setBusy(true);
    try {
      await api.put(`/inbox/conversations/${conversationId}/assign`, {
        assigned_to_user_id: assignedToMe ? null : user?.id,
      });
      onChanged();
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      onClick={toggle}
      disabled={busy}
      className={cn(
        "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all",
        "disabled:cursor-not-allowed disabled:opacity-50",
        assignedToMe
          ? "border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100"
          : "border-border bg-secondary text-foreground hover:bg-secondary/80"
      )}
    >
      {assignedToMe ? (
        <>
          <HiUserRemove className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Unassign</span>
        </>
      ) : (
        <>
          <HiUserAdd className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Assign to me</span>
        </>
      )}
    </button>
  );
}
