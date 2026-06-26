export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-3 py-2 text-muted-foreground">
      <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-current" />
    </div>
  );
}
