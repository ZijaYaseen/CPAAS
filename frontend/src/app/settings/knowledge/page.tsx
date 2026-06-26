"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DocumentUpload } from "@/components/knowledge/DocumentUpload";
import { DocumentList, type KnowledgeDoc } from "@/components/knowledge/DocumentList";

export default function KnowledgeSettingsPage() {
  const [docs, setDocs] = useState<KnowledgeDoc[]>([]);

  const load = useCallback(async () => {
    const { data } = await api.get<KnowledgeDoc[]>("/knowledge/documents");
    setDocs(data);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Knowledge Base</h1>
      <p className="text-sm text-muted-foreground">
        Documents here are chunked, embedded, and used by the AI to ground its answers (RAG).
      </p>
      <DocumentUpload onUploaded={load} />
      <div>
        <h2 className="mb-2 text-lg font-semibold">Documents</h2>
        <DocumentList docs={docs} onChanged={load} />
      </div>
    </div>
  );
}
