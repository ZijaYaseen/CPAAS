"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

export function KillSwitch({ active, onChanged }: { active: boolean; onChanged: () => void }) {
  const [busy, setBusy] = useState(false);

  const toggle = async () => {
    setBusy(true);
    try {
      await api.post("/ai/kill-switch", { enabled: !active });
      onChanged();
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex items-center justify-between rounded-lg border p-4">
      <div>
        <div className="font-medium">AI auto-responses</div>
        <div className="text-sm text-muted-foreground">
          {active ? "Active — AI replies to incoming messages" : "Disabled — all messages go to humans"}
        </div>
      </div>
      <Button variant={active ? "destructive" : "default"} disabled={busy} onClick={toggle}>
        {active ? "Disable AI (kill-switch)" : "Enable AI"}
      </Button>
    </div>
  );
}
