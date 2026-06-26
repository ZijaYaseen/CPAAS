"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { KillSwitch } from "@/components/ai/KillSwitch";
import { AgentConfigForm, type AgentConfig } from "@/components/ai/AgentConfigForm";
import { Button } from "@/components/ui/button";

const MVP_AGENTS = ["router", "support"];

export default function AISettingsPage() {
  const [configs, setConfigs] = useState<AgentConfig[]>([]);

  const load = useCallback(async () => {
    const { data } = await api.get<AgentConfig[]>("/ai/configurations");
    // Ensure both MVP agents appear even if not yet persisted (default-on).
    const byType = new Map(data.map((c) => [c.agent_type, c]));
    const merged = MVP_AGENTS.map(
      (t) =>
        byType.get(t) ?? {
          id: t,
          agent_type: t,
          is_enabled: true,
          system_prompt: null,
        },
    );
    setConfigs(merged);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const routerActive = configs.find((c) => c.agent_type === "router")?.is_enabled ?? true;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">AI Settings</h1>
        <Link href="/settings/ai/runs">
          <Button variant="outline">View AI run logs</Button>
        </Link>
      </div>

      <KillSwitch active={routerActive} onChanged={load} />

      <p className="text-sm text-muted-foreground">
        MVP: agents are read-only (search knowledge base, look up contacts/orders). They cannot
        modify data — write actions are escalated to a human.
      </p>

      {configs.map((c) => (
        <AgentConfigForm key={c.agent_type} config={c} onSaved={load} />
      ))}
    </div>
  );
}
