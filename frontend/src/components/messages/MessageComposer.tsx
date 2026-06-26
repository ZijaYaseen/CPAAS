"use client";

import { useState, useRef, useCallback } from "react";
import { cn } from "@/lib/utils";
import { HiPaperAirplane } from "react-icons/hi2";
import { RiStickyNoteFill } from "react-icons/ri";

type Mode = "reply" | "note";

type Props = {
  onSend: (content: string) => Promise<void>;
  onAddNote: (content: string) => Promise<void>;
  disabled?: boolean;
};

export function MessageComposer({ onSend, onAddNote, disabled }: Props) {
  const [value, setValue] = useState("");
  const [mode, setMode] = useState<Mode>("reply");
  const [busy, setBusy] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const submit = useCallback(async () => {
    const content = value.trim();
    if (!content || busy || disabled) return;
    setBusy(true);
    try {
      if (mode === "note") await onAddNote(content);
      else await onSend(content);
      setValue("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    } finally {
      setBusy(false);
    }
  }, [value, busy, disabled, mode, onAddNote, onSend]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      void submit();
    }
  };

  const onInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    // Auto-resize
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  const isNote = mode === "note";

  return (
    <div
      className={cn(
        "shrink-0 border-t transition-colors",
        isNote ? "border-amber-200 bg-amber-50/50" : "bg-card"
      )}
    >
      {/* Mode tabs */}
      <div className="flex border-b border-inherit">
        <button
          onClick={() => setMode("reply")}
          className={cn(
            "flex items-center gap-1.5 px-4 py-2 text-xs font-medium transition-colors",
            !isNote
              ? "border-b-2 border-primary text-primary bg-card"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <HiPaperAirplane className="h-3.5 w-3.5" />
          Reply
        </button>
        <button
          onClick={() => setMode("note")}
          className={cn(
            "flex items-center gap-1.5 px-4 py-2 text-xs font-medium transition-colors",
            isNote
              ? "border-b-2 border-amber-500 text-amber-700"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <RiStickyNoteFill className="h-3.5 w-3.5" />
          Internal Note
        </button>
      </div>

      {/* Textarea area */}
      <div className="p-3">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={onInput}
          onKeyDown={onKeyDown}
          disabled={disabled || busy}
          rows={2}
          placeholder={
            isNote
              ? "Add an internal note (only visible to your team)…"
              : "Type your reply… (⌘ Enter to send)"
          }
          className={cn(
            "w-full resize-none rounded-xl border px-3.5 py-2.5 text-sm outline-none transition-all",
            "placeholder:text-muted-foreground focus:ring-2 focus:ring-offset-1",
            "disabled:cursor-not-allowed disabled:opacity-50",
            isNote
              ? "border-amber-200 bg-amber-50 focus:ring-amber-300"
              : "border-border bg-background focus:ring-ring"
          )}
        />

        {/* Bottom bar */}
        <div className="mt-2 flex items-center justify-between">
          <p className="text-[11px] text-muted-foreground">
            {isNote ? "Only visible to your team" : "⌘ Enter to send"}
          </p>
          <button
            onClick={submit}
            disabled={!value.trim() || busy || disabled}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-4 py-2 text-xs font-semibold transition-all",
              "disabled:cursor-not-allowed disabled:opacity-40",
              isNote
                ? "bg-amber-500 text-white hover:bg-amber-600"
                : "bg-primary text-primary-foreground hover:bg-primary/90"
            )}
          >
            {isNote ? (
              <>
                <RiStickyNoteFill className="h-3.5 w-3.5" />
                {busy ? "Saving…" : "Add Note"}
              </>
            ) : (
              <>
                {busy ? "Sending…" : "Send"}
                <HiPaperAirplane className="h-3.5 w-3.5" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
