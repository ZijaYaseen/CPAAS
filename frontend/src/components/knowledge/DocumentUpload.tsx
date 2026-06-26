"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function DocumentUpload({ onUploaded }: { onUploaded: () => void }) {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);

  const addText = async () => {
    setBusy(true);
    try {
      await api.post("/knowledge/documents", {
        title: title || "Untitled",
        source_type: "text",
        content: text,
      });
      setTitle("");
      setText("");
      onUploaded();
    } finally {
      setBusy(false);
    }
  };

  const addUrl = async () => {
    setBusy(true);
    try {
      await api.post("/knowledge/documents", {
        title: title || url,
        source_type: "url",
        source_url: url,
      });
      setTitle("");
      setUrl("");
      onUploaded();
    } finally {
      setBusy(false);
    }
  };

  const uploadFile = async (file: File) => {
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", file);
      await api.post("/knowledge/documents/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onUploaded();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Add knowledge</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />

        <div className="space-y-2">
          <textarea
            className="min-h-[100px] w-full rounded-md border border-input bg-background p-3 text-sm"
            placeholder="Paste text content..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <Button onClick={addText} disabled={busy || !text}>
            Add text
          </Button>
        </div>

        <div className="flex gap-2">
          <Input placeholder="https://docs.example.com/faq" value={url} onChange={(e) => setUrl(e.target.value)} />
          <Button onClick={addUrl} disabled={busy || !url}>
            Add URL
          </Button>
        </div>

        <div>
          <label className="text-sm font-medium">Upload file (PDF / text)</label>
          <input
            type="file"
            accept=".pdf,.txt,.md"
            className="mt-1 block w-full text-sm"
            disabled={busy}
            onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])}
          />
        </div>
      </CardContent>
    </Card>
  );
}
