import type { Message } from "@/lib/inbox";

export function InternalNotes({ messages }: { messages: Message[] }) {
  const notes = messages.filter((m) => m.is_internal_note);
  return (
    <div className="border-t p-4">
      <h3 className="mb-2 text-sm font-semibold">Internal notes</h3>
      {notes.length === 0 ? (
        <p className="text-xs text-muted-foreground">No notes yet.</p>
      ) : (
        <ul className="space-y-2">
          {notes.map((n) => (
            <li key={n.id} className="rounded bg-amber-50 px-2 py-1 text-xs text-amber-900">
              {n.content}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
