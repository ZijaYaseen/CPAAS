"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { RiWhatsappFill } from "react-icons/ri";
import {
  HiMail,
  HiChat,
  HiCheckCircle,
  HiDuplicate,
  HiPlus,
  HiLightningBolt,
  HiShieldCheck,
  HiExternalLink,
  HiX,
} from "react-icons/hi";

// ─── Types ───────────────────────────────────────────────────────────────────

type Channel = {
  id: string;
  channel_type: string;
  name: string;
  is_active: boolean;
};

type ChannelKind = "webchat" | "email" | "whatsapp";

// ─── Small reusable pieces ────────────────────────────────────────────────────

function Badge({ children, color }: { children: React.ReactNode; color: string }) {
  return (
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", color)}>
      {children}
    </span>
  );
}

function CopySnippet({ value, label }: { value: string; label?: string }) {
  const [done, setDone] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(value);
    setDone(true);
    setTimeout(() => setDone(false), 2000);
  };
  return (
    <div className="flex items-start gap-2 rounded-lg border bg-slate-50 px-3 py-2.5">
      <code className="flex-1 break-all text-xs text-slate-700 leading-relaxed">{value}</code>
      <button
        onClick={copy}
        title={label ?? "Copy"}
        className="shrink-0 mt-0.5 flex items-center gap-1 text-xs font-medium text-primary hover:text-primary/80 transition-colors"
      >
        {done ? (
          <HiCheckCircle className="h-4 w-4 text-emerald-500" />
        ) : (
          <HiDuplicate className="h-4 w-4" />
        )}
        {done ? "Copied" : "Copy"}
      </button>
    </div>
  );
}

function FormField({
  label,
  hint,
  placeholder,
  value,
  onChange,
  type = "text",
  required = false,
}: {
  label: string;
  hint?: string;
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1">
        <label className="text-sm font-medium text-foreground">{label}</label>
        {required && <span className="text-xs text-rose-500">required</span>}
      </div>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete="off"
        className={cn(
          "w-full rounded-lg border bg-background px-3.5 py-2.5 text-sm outline-none transition-all",
          "placeholder:text-muted-foreground focus:ring-2 focus:ring-ring focus:ring-offset-1"
        )}
      />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

function InfoBox({ type, children }: { type: "tip" | "warning" | "success"; children: React.ReactNode }) {
  const styles = {
    tip:     "border-blue-100 bg-blue-50 text-blue-800",
    warning: "border-amber-100 bg-amber-50 text-amber-800",
    success: "border-emerald-100 bg-emerald-50 text-emerald-800",
  };
  const icons = {
    tip:     <HiLightningBolt className="h-4 w-4 shrink-0 mt-0.5" />,
    warning: <HiShieldCheck className="h-4 w-4 shrink-0 mt-0.5" />,
    success: <HiCheckCircle className="h-4 w-4 shrink-0 mt-0.5 text-emerald-600" />,
  };
  return (
    <div className={cn("flex gap-2.5 rounded-xl border p-4 text-sm leading-relaxed", styles[type])}>
      {icons[type]}
      <div>{children}</div>
    </div>
  );
}

function PrimaryButton({
  onClick,
  disabled,
  loading,
  children,
  color = "primary",
}: {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  color?: "primary" | "emerald" | "blue" | "violet";
}) {
  const colors = {
    primary: "bg-primary text-primary-foreground hover:bg-primary/90",
    emerald: "bg-emerald-600 text-white hover:bg-emerald-700",
    blue:    "bg-blue-600 text-white hover:bg-blue-700",
    violet:  "bg-violet-600 text-white hover:bg-violet-700",
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold transition-all",
        "disabled:cursor-not-allowed disabled:opacity-40",
        colors[color]
      )}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          Saving...
        </span>
      ) : children}
    </button>
  );
}

// ─── Channel card ─────────────────────────────────────────────────────────────

type ChannelConfig = {
  kind: ChannelKind;
  label: string;
  tagline: string;
  icon: React.ElementType;
  iconColor: string;
  iconBg: string;
  accentColor: string;
};

const CHANNEL_CONFIGS: ChannelConfig[] = [
  {
    kind: "webchat",
    label: "Web Chat",
    tagline: "Add a live chat widget to your website in minutes",
    icon: HiChat,
    iconColor: "text-violet-600",
    iconBg: "bg-violet-100",
    accentColor: "violet",
  },
  {
    kind: "email",
    label: "Email",
    tagline: "Receive and reply to emails right from your inbox",
    icon: HiMail,
    iconColor: "text-blue-600",
    iconBg: "bg-blue-100",
    accentColor: "blue",
  },
  {
    kind: "whatsapp",
    label: "WhatsApp Business",
    tagline: "Connect your WhatsApp Business number to handle customer chats",
    icon: RiWhatsappFill,
    iconColor: "text-emerald-600",
    iconBg: "bg-emerald-100",
    accentColor: "emerald",
  },
];

// ─── Individual forms ─────────────────────────────────────────────────────────

function WebChatForm({
  onSuccess,
  loading,
  setLoading,
}: {
  onSuccess: (ch: Channel) => void;
  loading: boolean;
  setLoading: (v: boolean) => void;
}) {
  const [name, setName] = useState("");
  const [done, setDone] = useState<Channel | null>(null);
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const frontBase = typeof window !== "undefined" ? window.location.origin : "http://localhost:3000";

  const submit = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      const { data } = await api.post<Channel>("/channels/webchat/create", { name });
      setDone(data);
      setName("");
      onSuccess(data);
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    const snippet = `<script src="${frontBase}/webchat-widget.js" data-account="${done.id}" data-api="${apiBase}"></script>`;
    return (
      <div className="space-y-4">
        <InfoBox type="success">
          <p className="font-semibold">Widget created successfully!</p>
          <p className="mt-0.5">Copy the snippet below and paste it before the closing body tag on your website.</p>
        </InfoBox>
        <div className="space-y-1.5">
          <p className="text-sm font-medium">Embed snippet</p>
          <CopySnippet value={snippet} label="Copy snippet" />
        </div>
        <div className="space-y-1.5">
          <p className="text-sm font-medium">Channel ID</p>
          <CopySnippet value={done.id} label="Copy ID" />
          <p className="text-xs text-muted-foreground">Use this ID if you are integrating the widget manually.</p>
        </div>
        <button
          onClick={() => setDone(null)}
          className="text-sm text-primary underline underline-offset-2"
        >
          Add another widget
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <InfoBox type="tip">
        No external account needed. Create the widget, copy the script tag, and paste it on your site. Messages from visitors will appear instantly in your inbox.
      </InfoBox>
      <FormField
        label="Widget Name"
        placeholder="Website Support"
        value={name}
        onChange={setName}
        hint="This name appears in your connected channels list."
        required
      />
      <PrimaryButton onClick={submit} disabled={!name.trim()} loading={loading} color="violet">
        <HiPlus className="h-4 w-4" />
        Create Widget
      </PrimaryButton>
    </div>
  );
}

function EmailInboundGuide({ channelId }: { channelId: string }) {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const webhookUrl = `${apiBase}/api/v1/webhooks/email`;

  const appsScript = `// Paste this in script.google.com → New Project
const WEBHOOK_URL = "${webhookUrl}";
const CHANNEL_ID  = "${channelId}";

function forwardToInbox() {
  const threads = GmailApp.search("is:unread label:inbox", 0, 20);
  threads.forEach(thread => {
    const msg = thread.getMessages().slice(-1)[0];
    UrlFetchApp.fetch(WEBHOOK_URL, {
      method: "post",
      contentType: "application/x-www-form-urlencoded",
      payload: {
        from:               msg.getFrom(),
        to:                 msg.getTo(),
        subject:            msg.getSubject(),
        text:               msg.getPlainBody(),
        message_id:         msg.getId(),
        channel_account_id: CHANNEL_ID,
      },
      muteHttpExceptions: true,
    });
    thread.markRead();
  });
}`;

  return (
    <div className="mt-6 space-y-5 border-t pt-6">
      <div>
        <p className="text-sm font-semibold text-foreground">Step 2 — Enable Inbound Emails</p>
        <p className="mt-1 text-xs text-muted-foreground">
          So that emails sent to your Gmail appear here in the inbox, set up a 2-minute Google Apps Script.
          No domain or paid service required.
        </p>
      </div>

      <InfoBox type="tip">
        <p className="font-semibold">How it works</p>
        <p className="mt-0.5 text-xs">
          A Google Apps Script runs every minute, checks your Gmail for new emails, and forwards them
          to this inbox automatically. It uses your existing Gmail — no extra account needed.
        </p>
      </InfoBox>

      {/* Webhook URL */}
      <div className="space-y-1.5">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Your Webhook URL</p>
        <CopySnippet value={webhookUrl} label="Copy URL" />
      </div>

      {/* Step by step */}
      <div className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Setup Steps</p>
        <ol className="space-y-2 text-sm text-foreground">
          {[
            <>Go to <a href="https://script.google.com" target="_blank" rel="noopener noreferrer" className="font-semibold text-primary underline underline-offset-2 inline-flex items-center gap-0.5">script.google.com <HiExternalLink className="h-3 w-3" /></a> and click <strong>New Project</strong></>,
            <>Paste the script below into the editor and click <strong>Save</strong></>,
            <>Click the <strong>clock icon (Triggers)</strong> on the left sidebar</>,
            <>Add trigger: function <code className="rounded bg-slate-100 px-1 py-0.5 text-xs">forwardToInbox</code> · Time-driven · Minutes timer · <strong>Every minute</strong></>,
            <>Click <strong>Save</strong> and allow permissions when prompted</>,
            <>Send a test email to your Gmail and watch it appear here within 60 seconds ✅</>,
          ].map((step, i) => (
            <li key={i} className="flex gap-3">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-100 text-[11px] font-bold text-blue-700">{i + 1}</span>
              <span className="leading-relaxed">{step}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Script */}
      <div className="space-y-1.5">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Apps Script (pre-filled)</p>
        <CopySnippet value={appsScript} label="Copy script" />
      </div>

      <InfoBox type="warning">
        <p className="font-semibold">Production / Custom Domain?</p>
        <p className="mt-0.5 text-xs">
          If your client has their own domain (e.g. support@company.com), they can point their domain&apos;s
          MX record to SendGrid Inbound Parse and use the webhook URL above — no Apps Script needed.
          This scales to thousands of emails per day.
        </p>
      </InfoBox>
    </div>
  );
}

function EmailForm({
  onSuccess,
  loading,
  setLoading,
}: {
  onSuccess: (ch: Channel) => void;
  loading: boolean;
  setLoading: (v: boolean) => void;
}) {
  const [name, setName]     = useState("");
  const [from, setFrom]     = useState("");
  const [host, setHost]     = useState("smtp.gmail.com");
  const [port, setPort]     = useState("587");
  const [user, setUser]     = useState("");
  const [pass, setPass]     = useState("");
  const [done, setDone]     = useState<Channel | null>(null);

  const ready = name && from && host && port && user && pass;

  const submit = async () => {
    if (!ready) return;
    setLoading(true);
    try {
      const { data } = await api.post<Channel>("/channels/email/connect", {
        name,
        from_address: from,
        smtp_host: host,
        smtp_port: parseInt(port),
        smtp_user: user,
        smtp_password: pass,
        inbound_address: from,
      });
      setDone(data);
      onSuccess(data);
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <div className="space-y-4">
        <InfoBox type="success">
          <p className="font-semibold">Email channel connected!</p>
          <p className="mt-0.5 text-xs">
            Outbound replies are ready. Follow Step 2 below so incoming emails also appear in your inbox.
          </p>
        </InfoBox>
        <EmailInboundGuide channelId={done.id} />
        <button
          onClick={() => setDone(null)}
          className="text-sm text-primary underline underline-offset-2"
        >
          Connect another email
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <InfoBox type="warning">
        <p className="font-semibold">Using Gmail? Generate an App Password first.</p>
        <p className="mt-0.5 text-xs">
          Go to Google Account → Security → App Passwords and generate one for &quot;Mail&quot;.
          Use that 16-character password below — not your regular Gmail password.
        </p>
        <a
          href="https://myaccount.google.com/apppasswords"
          target="_blank"
          rel="noopener noreferrer"
          className="mt-1.5 inline-flex items-center gap-1 text-xs font-semibold underline underline-offset-2"
        >
          Open App Passwords <HiExternalLink className="h-3 w-3" />
        </a>
      </InfoBox>

      <div className="grid gap-4 sm:grid-cols-2">
        <FormField label="Channel Name" placeholder="Support Inbox" value={name} onChange={setName} required />
        <FormField label="From Address" placeholder="support@gmail.com" value={from} onChange={setFrom} required />
        <FormField
          label="SMTP Host"
          placeholder="smtp.gmail.com"
          value={host}
          onChange={setHost}
          hint="Gmail → smtp.gmail.com · Outlook → smtp.office365.com"
          required
        />
        <FormField
          label="SMTP Port"
          placeholder="587"
          value={port}
          onChange={setPort}
          hint="587 for TLS (recommended) · 465 for SSL"
          required
        />
        <FormField label="SMTP Username" placeholder="your@gmail.com" value={user} onChange={setUser} required />
        <FormField
          label="App Password"
          placeholder="16-character app password"
          value={pass}
          onChange={setPass}
          type="password"
          hint="Stored securely and never shown again."
          required
        />
      </div>

      <PrimaryButton onClick={submit} disabled={!ready} loading={loading} color="blue">
        <HiPlus className="h-4 w-4" />
        Connect Email
      </PrimaryButton>
    </div>
  );
}

function WhatsAppForm({
  onSuccess,
  loading,
  setLoading,
}: {
  onSuccess: (ch: Channel) => void;
  loading: boolean;
  setLoading: (v: boolean) => void;
}) {
  const [name,    setName]    = useState("");
  const [phoneId, setPhoneId] = useState("");
  const [wabaId,  setWabaId]  = useState("");
  const [token,   setToken]   = useState("");
  const [secret,  setSecret]  = useState("");
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const webhookUrl = `${apiBase}/webhooks/whatsapp`;

  const ready = name && phoneId && wabaId && token;

  const submit = async () => {
    if (!ready) return;
    setLoading(true);
    try {
      const { data } = await api.post<Channel>("/channels/whatsapp/connect", {
        name,
        phone_number_id: phoneId,
        access_token: token,
        app_secret: secret || undefined,
        waba_id: wabaId,
      });
      onSuccess(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <InfoBox type="tip">
        <p className="font-semibold">How to get these credentials</p>
        <ol className="mt-1.5 space-y-1 text-xs list-decimal list-inside">
          <li>Go to developers.facebook.com → Create a Business app → Add WhatsApp product</li>
          <li>Open WhatsApp → API Setup to find Phone Number ID, WABA ID, and Access Token</li>
          <li>Under Configuration, set the Webhook URL below and Verify Token: <strong>whatsapp-verify-token</strong></li>
          <li>Subscribe to the <strong>messages</strong> webhook field</li>
        </ol>
      </InfoBox>

      <div className="space-y-2">
        <p className="text-sm font-medium">Your Webhook URL</p>
        <CopySnippet value={webhookUrl} label="Copy webhook URL" />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <FormField label="Channel Name" placeholder="WhatsApp Support" value={name} onChange={setName} required />
        <FormField
          label="Phone Number ID"
          placeholder="123456789012345"
          value={phoneId}
          onChange={setPhoneId}
          hint="WhatsApp → API Setup → Phone Number ID"
          required
        />
        <FormField
          label="WhatsApp Business Account ID"
          placeholder="1312735957151574"
          value={wabaId}
          onChange={setWabaId}
          hint="WhatsApp → API Setup → WhatsApp Business Account ID"
          required
        />
        <div className="sm:col-span-2">
          <FormField
            label="Access Token"
            placeholder="EAAxxxxxxxxxxxxx"
            value={token}
            onChange={setToken}
            type="password"
            hint="WhatsApp → API Setup → Temporary or permanent access token"
            required
          />
        </div>
        <div className="sm:col-span-2">
          <FormField
            label="App Secret"
            placeholder="Optional but recommended"
            value={secret}
            onChange={setSecret}
            type="password"
            hint="App Settings → Basic → App Secret"
          />
        </div>
      </div>

      <PrimaryButton onClick={submit} disabled={!ready} loading={loading} color="emerald">
        <HiPlus className="h-4 w-4" />
        Connect WhatsApp
      </PrimaryButton>
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function ChannelsPage() {
  const [channels, setChannels]       = useState<Channel[]>([]);
  const [activeKind, setActiveKind]   = useState<ChannelKind | null>(null);
  const [loading, setLoading]         = useState(false);
  const [toast, setToast]             = useState("");

  const reload = async () => {
    const { data } = await api.get<Channel[]>("/channels");
    setChannels(data);
  };

  useEffect(() => { void reload(); }, []);

  const handleSuccess = (ch: Channel) => {
    void reload();
    setToast(`${ch.name} connected successfully`);
    setTimeout(() => setToast(""), 4000);
    if (ch.channel_type !== "webchat") setActiveKind(null);
  };

  const channelsByType = (kind: string) => channels.filter((c) => c.channel_type === kind);

  return (
    <div className="mx-auto max-w-2xl space-y-6 pb-12">

      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Channels</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Connect your communication channels. All messages from every channel land in one unified inbox.
        </p>
      </div>

      {/* Toast */}
      {toast && (
        <div className="flex items-center justify-between gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
          <div className="flex items-center gap-2">
            <HiCheckCircle className="h-4 w-4 shrink-0" />
            {toast}
          </div>
          <button onClick={() => setToast("")}><HiX className="h-4 w-4" /></button>
        </div>
      )}

      {/* Channel cards */}
      <div className="space-y-3">
        {CHANNEL_CONFIGS.map((cfg) => {
          const Icon = cfg.icon;
          const connected = channelsByType(cfg.kind);
          const isOpen = activeKind === cfg.kind;

          return (
            <div
              key={cfg.kind}
              className={cn(
                "rounded-2xl border bg-card shadow-sm overflow-hidden transition-all",
                isOpen && "ring-2 ring-primary"
              )}
            >
              {/* Card header */}
              <div className="flex items-center gap-4 p-5">
                <div className={cn("flex h-12 w-12 shrink-0 items-center justify-center rounded-xl", cfg.iconBg)}>
                  <Icon className={cn("h-6 w-6", cfg.iconColor)} />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold">{cfg.label}</p>
                    {connected.length > 0 && (
                      <Badge color="bg-emerald-100 text-emerald-700">
                        {connected.length} connected
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">{cfg.tagline}</p>
                </div>

                <button
                  onClick={() => setActiveKind(isOpen ? null : cfg.kind)}
                  className={cn(
                    "shrink-0 flex items-center gap-1.5 rounded-lg border px-3.5 py-2 text-sm font-medium transition-all",
                    isOpen
                      ? "border-border bg-secondary text-foreground"
                      : "border-primary/20 bg-primary/5 text-primary hover:bg-primary/10"
                  )}
                >
                  <HiPlus className={cn("h-4 w-4 transition-transform", isOpen && "rotate-45")} />
                  {isOpen ? "Cancel" : "Connect"}
                </button>
              </div>

              {/* Connected list */}
              {connected.length > 0 && !isOpen && (
                <div className="border-t">
                  {connected.map((c) => (
                    <div key={c.id} className="flex items-center justify-between border-b last:border-0 px-5 py-3 bg-secondary/30">
                      <span className="text-sm font-medium">{c.name}</span>
                      <Badge color="bg-emerald-100 text-emerald-700">Active</Badge>
                    </div>
                  ))}
                </div>
              )}

              {/* Expanded form */}
              {isOpen && (
                <div className="border-t bg-background px-5 py-6">
                  {cfg.kind === "webchat" && (
                    <WebChatForm onSuccess={handleSuccess} loading={loading} setLoading={setLoading} />
                  )}
                  {cfg.kind === "email" && (
                    <EmailForm onSuccess={handleSuccess} loading={loading} setLoading={setLoading} />
                  )}
                  {cfg.kind === "whatsapp" && (
                    <WhatsAppForm onSuccess={handleSuccess} loading={loading} setLoading={setLoading} />
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty state */}
      {channels.length === 0 && !activeKind && (
        <div className="rounded-2xl border border-dashed bg-card p-10 text-center">
          <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-secondary">
            <HiLightningBolt className="h-6 w-6 text-muted-foreground" />
          </div>
          <p className="font-semibold">No channels connected yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Start with Web Chat — it takes less than one minute and requires no external account.
          </p>
        </div>
      )}
    </div>
  );
}
