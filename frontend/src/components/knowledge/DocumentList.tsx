"use client";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export type KnowledgeDoc = {
  id: string;
  title: string;
  source_type: string;
  status: string;
  created_at: string;
};

const STATUS_COLOR: Record<string, string> = {
  ready: "text-green-600",
  processing: "text-amber-600",
  pending: "text-muted-foreground",
  failed: "text-destructive",
};

export function DocumentList({ docs, onChanged }: { docs: KnowledgeDoc[]; onChanged: () => void }) {
  const remove = async (id: string) => {
    await api.delete(`/knowledge/documents/${id}`);
    onChanged();
  };

  if (docs.length === 0) {
    return <p className="text-sm text-muted-foreground">No documents yet.</p>;
  }

  return (
    <div className="space-y-2">
      {docs.map((d) => (
        <Card key={d.id}>
          <CardContent className="flex items-center justify-between p-4">
            <div>
              <div className="font-medium">{d.title}</div>
              <div className="text-xs text-muted-foreground">
                {d.source_type} ·{" "}
                <span className={STATUS_COLOR[d.status] ?? ""}>{d.status}</span>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={() => remove(d.id)}>
              Delete
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
