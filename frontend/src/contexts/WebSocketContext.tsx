"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useAuth } from "@/contexts/AuthContext";

export type RealtimeEvent = {
  tenant_id: string;
  type: "message_created" | "message_updated" | "assignment_changed" | string;
  data: Record<string, unknown>;
};

type Handler = (event: RealtimeEvent) => void;

type WebSocketState = {
  connected: boolean;
  subscribe: (handler: Handler) => () => void;
};

const WebSocketContext = createContext<WebSocketState | undefined>(undefined);

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [connected, setConnected] = useState(false);
  const handlers = useRef<Set<Handler>>(new Set());
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const subscribe = useCallback((handler: Handler) => {
    handlers.current.add(handler);
    return () => handlers.current.delete(handler);
  }, []);

  useEffect(() => {
    if (!user) return;
    let closed = false;

    const connect = () => {
      const ws = new WebSocket(`${WS_URL}/ws`);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onmessage = (e) => {
        try {
          const event = JSON.parse(e.data) as RealtimeEvent;
          handlers.current.forEach((h) => h(event));
        } catch {
          /* ignore malformed frames */
        }
      };
      ws.onclose = () => {
        setConnected(false);
        if (!closed) {
          reconnectRef.current = setTimeout(connect, 2000); // simple backoff
        }
      };
      ws.onerror = () => ws.close();
    };

    connect();
    return () => {
      closed = true;
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [user]);

  return (
    <WebSocketContext.Provider value={{ connected, subscribe }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const ctx = useContext(WebSocketContext);
  if (!ctx) throw new Error("useWebSocket must be used within WebSocketProvider");
  return ctx;
}
