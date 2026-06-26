"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

type ToolCall = {
  id: string;
  tool_name: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  error: string | null;
};

type RunDetail = {
  id: string;
  agent_type: string;
  prompt: string;
  response: string | null;
  escalated_to_human: boolean;
  escalation_reason: string | null;
  tool_calls: ToolCall[];
};

export function RunDetailsModal({ runId, onClose }: { runId: string; onClose: () => void }) {
  const [run, setRun] = useState<RunDetail | null>(null);

  useEffect(() => {
    void api.get<RunDetail>(`/ai/runs/${runId}`).then(({ data }) => setRun(data));
  }, [runId]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="max-h-[80vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-card p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">AI Run</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
        {!run ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : (
          <div className="space-y-3 text-sm">
            <Field label="Prompt" value={run.prompt} />
            <Field label="Response" value={run.response ?? "—"} />
            {run.escalated_to_human && (
              <div className="rounded bg-amber-50 p-2 text-amber-900">
                Escalated to human: {run.escalation_reason ?? "uncertain"}
              </div>
            )}
            <div>
              <div className="mb-1 font-medium">Tool calls ({run.tool_calls.length})</div>
              {run.tool_calls.length === 0 ? (
                <p className="text-muted-foreground">No tools used.</p>
              ) : (
                <ul className="space-y-2">
                  {run.tool_calls.map((t) => (
                    <li key={t.id} className="rounded border p-2">
                      <div className="font-mono text-xs font-semibold">{t.tool_name}</div>
                      <pre className="overflow-x-auto text-xs text-muted-foreground">
                        {JSON.stringify({ input: t.input, output: t.output }, null, 2)}
                      </pre>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="mb-1 font-medium">{label}</div>
      <div className="whitespace-pre-wrap rounded bg-secondary p-2">{value}</div>
    </div>
  );
}
