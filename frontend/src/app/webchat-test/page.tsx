"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const DEFAULT_CHANNEL_ID = "";
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const POLL_INTERVAL = 3000;

type Message = {
  id: string;
  content: string;
  direction: "visitor" | "agent";
  time: string;
};

function generateSessionId() {
  return "wc_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function nowTime() {
  return new Date().toLocaleTimeString("en-PK", { hour: "2-digit", minute: "2-digit" });
}

export default function WebChatTestPage() {
  const [channelId, setChannelId] = useState(DEFAULT_CHANNEL_ID);
  const [visitorName, setVisitorName] = useState("Test Visitor");
  const [sessionId] = useState(() => generateSessionId());
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [started, setStarted] = useState(false);
  const seenIds = useRef<Set<string>>(new Set());
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const pollMessages = useCallback(async () => {
    if (!started) return;
    try {
      const res = await fetch(
        `${API_BASE}/api/v1/webchat/messages?channel_account_id=${channelId}&session_id=${encodeURIComponent(sessionId)}`
      );
      const data = await res.json();
      const incoming = (data.messages ?? []) as {
        id: string;
        content: string;
        direction: string;
        sender_type: string;
        created_at: string;
      }[];

      const newAgentMsgs: Message[] = [];
      for (const m of incoming) {
        if (seenIds.current.has(m.id)) continue;
        seenIds.current.add(m.id);
        // Only show outbound messages (agent replies) — visitor msgs already shown on send
        if (m.direction === "outbound") {
          newAgentMsgs.push({
            id: m.id,
            content: m.content,
            direction: "agent",
            time: new Date(m.created_at).toLocaleTimeString("en-PK", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          });
        }
      }
      if (newAgentMsgs.length > 0) {
        setMessages((prev) => [...prev, ...newAgentMsgs]);
      }
    } catch {
      // silent — no network error shown for polling
    }
  }, [started, channelId, sessionId]);

  useEffect(() => {
    if (!started) return;
    pollMessages();
    const id = setInterval(pollMessages, POLL_INTERVAL);
    return () => clearInterval(id);
  }, [started, pollMessages]);

  async function send() {
    const content = input.trim();
    if (!content || sending) return;
    setInput("");
    setSending(true);
    setError("");

    const tempId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      { id: tempId, content, direction: "visitor", time: nowTime() },
    ]);

    try {
      const res = await fetch(`${API_BASE}/api/v1/webchat/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channel_account_id: channelId,
          session_id: sessionId,
          content,
          visitor_name: visitorName,
        }),
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(JSON.stringify(d.detail ?? d));
      }
      const { message_id } = await res.json();
      // Replace tempId with real ID so polling doesn't re-add it
      seenIds.current.add(message_id);
      setMessages((prev) =>
        prev.map((m) => (m.id === tempId ? { ...m, id: message_id } : m))
      );
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Send failed");
      setMessages((prev) => prev.filter((m) => m.id !== tempId));
    } finally {
      setSending(false);
    }
  }

  if (!started) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 space-y-5">
          <div className="text-center">
            <div className="text-3xl mb-2">💬</div>
            <h1 className="text-xl font-bold text-slate-800">Web Chat Test</h1>
            <p className="text-sm text-slate-500 mt-1">Visitor side simulator</p>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-xs font-medium text-slate-600 block mb-1">Your Name</label>
              <input
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-400"
                value={visitorName}
                onChange={(e) => setVisitorName(e.target.value)}
                placeholder="Visitor name"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 block mb-1">Channel ID</label>
              <input
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm font-mono outline-none focus:ring-2 focus:ring-indigo-400"
                value={channelId}
                onChange={(e) => setChannelId(e.target.value)}
              />
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-xs text-slate-500 space-y-1">
              <div><span className="font-medium text-slate-700">Session ID:</span> {sessionId}</div>
              <div className="text-slate-400">Ek session = ek conversation in inbox.</div>
            </div>
          </div>

          <button
            onClick={() => setStarted(true)}
            disabled={!channelId.trim() || !visitorName.trim()}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-semibold py-2.5 rounded-xl transition-colors"
          >
            Start Chat
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div
        className="bg-white rounded-2xl shadow-xl w-full max-w-sm flex flex-col overflow-hidden"
        style={{ height: "600px" }}
      >
        {/* Header */}
        <div className="bg-indigo-600 px-4 py-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center text-white font-bold text-sm">
            {visitorName[0]?.toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white font-semibold text-sm truncate">{visitorName}</p>
            <p className="text-indigo-200 text-xs">Agent replies har 3 sec mein aate hain</p>
          </div>
          <span className="text-xs bg-white/20 text-white px-2 py-0.5 rounded-full shrink-0">
            Live
          </span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50">
          {messages.length === 0 && (
            <div className="text-center text-slate-400 text-sm mt-8">
              <div className="text-2xl mb-2">👋</div>
              <p>Kuch likho — agent inbox mein dekhega aur reply karega</p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.direction === "visitor" ? "justify-end" : "justify-start"}`}
            >
              {msg.direction === "agent" && (
                <div className="w-7 h-7 rounded-full bg-slate-300 flex items-center justify-center text-xs font-bold text-slate-600 mr-2 shrink-0 self-end">
                  A
                </div>
              )}
              <div
                className={`max-w-[75%] px-3 py-2 rounded-2xl text-sm ${
                  msg.direction === "visitor"
                    ? "bg-indigo-600 text-white rounded-br-sm"
                    : "bg-white text-slate-800 border border-slate-200 rounded-bl-sm shadow-sm"
                }`}
              >
                <p>{msg.content}</p>
                <p
                  className={`text-[10px] mt-1 ${
                    msg.direction === "visitor" ? "text-indigo-200 text-right" : "text-slate-400"
                  }`}
                >
                  {msg.direction === "agent" ? "Agent · " : ""}{msg.time}
                </p>
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex justify-end">
              <div className="bg-indigo-100 text-indigo-400 text-xs px-3 py-2 rounded-2xl">
                Sending…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {error && (
          <div className="px-4 py-2 bg-red-50 text-red-600 text-xs border-t border-red-100">
            ⚠ {error}
          </div>
        )}

        {/* Composer */}
        <div className="border-t border-slate-200 bg-white flex items-end gap-2 px-3 py-3">
          <textarea
            rows={1}
            className="flex-1 resize-none border border-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-400 max-h-24"
            placeholder="Message likho… (Enter = send)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send();
              }
            }}
          />
          <button
            onClick={() => void send()}
            disabled={!input.trim() || sending}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white rounded-xl px-4 py-2 text-sm font-medium transition-colors shrink-0"
          >
            Send
          </button>
        </div>
      </div>

      {/* Side info */}
      <div className="absolute bottom-4 left-4 bg-white rounded-xl shadow-lg p-3 text-xs text-slate-500 max-w-xs hidden md:block">
        <p className="font-semibold text-slate-700 mb-1">Demo flow:</p>
        <ol className="space-y-1 list-decimal list-inside">
          <li>Yahan visitor message bhejo</li>
          <li>Inbox <span className="font-mono text-indigo-600">localhost:3000/inbox</span> mein aayega</li>
          <li>Agent wahan reply kare</li>
          <li>3 sec mein yahan bhi dikhega ✅</li>
        </ol>
      </div>
    </div>
  );
}
