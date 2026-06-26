"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { RunDetailsModal } from "@/components/ai/RunDetailsModal";
import { Card, CardContent } from "@/components/ui/card";

type Run = {
  id: string;
  agent_type: string;
  prompt: string;
  response: string | null;
  escalated_to_human: boolean;
  created_at: string;
};

export default function AIRunsPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    void api.get<Run[]>("/ai/runs").then(({ data }) => setRuns(data));
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-bold">AI Run Logs</h1>
      {runs.length === 0 ? (
        <p className="text-sm text-muted-foreground">No AI runs yet.</p>
      ) : (
        runs.map((r) => (
          <Card key={r.id} className="cursor-pointer hover:bg-secondary" >
            <CardContent className="p-4" onClick={() => setSelected(r.id)}>
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase text-muted-foreground">{r.agent_type}</span>
                <span className="text-xs text-muted-foreground">
                  {new Date(r.created_at).toLocaleString()}
                </span>
              </div>
              <p className="mt-1 line-clamp-1 font-medium">{r.prompt}</p>
              <p className="line-clamp-1 text-sm text-muted-foreground">
                {r.escalated_to_human ? "↗ Escalated to human" : r.response ?? "—"}
              </p>
            </CardContent>
          </Card>
        ))
      )}
      {selected && <RunDetailsModal runId={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
