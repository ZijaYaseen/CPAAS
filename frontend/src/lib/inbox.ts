import { api } from "@/lib/api";

export type ContactSummary = {
  id: string;
  full_name: string | null;
  email: string | null;
  phone: string | null;
};

export type Conversation = {
  id: string;
  status: string;
  channel_account_id: string | null;
  assigned_to_user_id: string | null;
  assigned_to_team_id: string | null;
  last_message_at: string | null;
  created_at: string;
  contact: ContactSummary;
  last_message_preview: string | null;
};

export type Message = {
  id: string;
  conversation_id: string;
  direction: "inbound" | "outbound";
  sender_type: "contact" | "user" | "ai_agent";
  sender_id: string | null;
  content: string | null;
  media_urls: string[] | null;
  is_internal_note: boolean;
  created_at: string;
  latest_status: string | null;
};

export async function fetchConversations(): Promise<Conversation[]> {
  const { data } = await api.get<Conversation[]>("/inbox/conversations");
  return data;
}

export async function fetchMessages(conversationId: string): Promise<Message[]> {
  const { data } = await api.get<Message[]>(`/inbox/conversations/${conversationId}/messages`);
  return data;
}

export async function sendMessage(conversationId: string, content: string): Promise<Message> {
  const { data } = await api.post<Message>(`/inbox/conversations/${conversationId}/messages`, {
    content,
  });
  return data;
}

export async function addNote(conversationId: string, content: string): Promise<Message> {
  const { data } = await api.post<Message>(`/inbox/conversations/${conversationId}/notes`, {
    content,
  });
  return data;
}
