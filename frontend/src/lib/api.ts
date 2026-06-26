import axios from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Shared API client. `withCredentials` sends the HttpOnly session cookie issued
 * by the FastAPI backend on every request (backend is the auth source of truth).
 */
export const api = axios.create({
  baseURL: `${baseURL}/api/v1`,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

export type ApiUser = {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
};

export type ApiTenant = {
  id: string;
  name: string;
  slug: string;
  subscription_tier: string;
};
