"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export type AgentConfig = {
  id: string;
  agent_type: string;
  is_enabled: boolean;
  system_prompt: string | null;
};

export function AgentConfigForm({ config, onSaved }: { config: AgentConfig; onSaved: () => void }) {
  const [prompt, setPrompt] = useState(config.system_prompt ?? "");
  const [enabled, setEnabled] = useState(config.is_enabled);
  const [busy, setBusy] = useState(false);

  const save = async () => {
    setBusy(true);
    try {
      await api.put(`/ai/configurations/${config.agent_type}`, {
        is_enabled: enabled,
        system_prompt: prompt || null,
      });
      onSaved();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg capitalize">{config.agent_type} agent</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} />
          Enabled
        </label>
        <textarea
          className="min-h-[120px] w-full rounded-md border border-input bg-background p-3 text-sm"
          placeholder="System prompt (leave blank for default)"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <Button onClick={save} disabled={busy}>
          {busy ? "Saving..." : "Save"}
        </Button>
      </CardContent>
    </Card>
  );
}
