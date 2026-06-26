"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { type ApiTenant } from "@/lib/api";

type TenantState = {
  tenant: ApiTenant | null;
  setTenant: (t: ApiTenant | null) => void;
};

const TenantContext = createContext<TenantState | undefined>(undefined);

export function TenantProvider({ children }: { children: ReactNode }) {
  const [tenant, setTenant] = useState<ApiTenant | null>(null);
  return (
    <TenantContext.Provider value={{ tenant, setTenant }}>{children}</TenantContext.Provider>
  );
}

export function useTenant() {
  const ctx = useContext(TenantContext);
  if (!ctx) throw new Error("useTenant must be used within TenantProvider");
  return ctx;
}
