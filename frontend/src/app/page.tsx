import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8 text-center">
      <h1 className="text-4xl font-bold tracking-tight">Unified Communication Platform</h1>
      <p className="max-w-xl text-muted-foreground">
        One AI-powered inbox for WhatsApp, Email, and Web Chat. Respond faster, automate the
        routine, and never lose a conversation.
      </p>
      <div className="flex gap-4">
        <Link href="/login">
          <Button>Sign in</Button>
        </Link>
        <Link href="/register">
          <Button variant="outline">Create account</Button>
        </Link>
      </div>
    </main>
  );
}
