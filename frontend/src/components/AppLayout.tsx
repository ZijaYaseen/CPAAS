"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Inbox,
  Users,
  Ticket,
  Megaphone,
  BarChart3,
  Bot,
  BookOpen,
  Settings,
  X,
  ChevronRight,
} from "lucide-react";
import { HiMenuAlt2 } from "react-icons/hi";
import { cn } from "@/lib/utils";

const MAIN_NAV = [
  { href: "/inbox", label: "Inbox", icon: Inbox },
  { href: "/contacts", label: "Contacts", icon: Users },
  { href: "/tickets", label: "Tickets", icon: Ticket },
  { href: "/campaigns", label: "Broadcasts", icon: Megaphone },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
];

const CONFIG_NAV = [
  { href: "/settings/ai", label: "AI Agents", icon: Bot },
  { href: "/settings/knowledge", label: "Knowledge Base", icon: BookOpen },
  { href: "/settings/channels", label: "Channels", icon: Settings },
];

const POST_MVP = ["/contacts", "/tickets", "/campaigns", "/analytics"];

function NavItem({
  href,
  label,
  icon: Icon,
  active,
  onClick,
}: {
  href: string;
  label: string;
  icon: React.ElementType;
  active: boolean;
  onClick?: () => void;
}) {
  const isPostMvp = POST_MVP.includes(href);
  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(
        "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
        active
          ? "bg-primary text-primary-foreground shadow-sm"
          : "text-muted-foreground hover:bg-secondary hover:text-foreground"
      )}
    >
      <Icon className="h-[18px] w-[18px] shrink-0" />
      <span className="flex-1">{label}</span>
      {isPostMvp && (
        <span
          className={cn(
            "rounded-full px-1.5 py-0.5 text-[10px] font-semibold leading-none",
            active
              ? "bg-primary-foreground/20 text-primary-foreground"
              : "bg-amber-100 text-amber-700"
          )}
        >
          Soon
        </span>
      )}
    </Link>
  );
}

function SidebarContent({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname();

  return (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center justify-between border-b px-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary shadow-sm">
            <span className="text-xs font-bold text-primary-foreground">CP</span>
          </div>
          <div>
            <p className="text-sm font-bold leading-none">CPAAS</p>
            <p className="text-[11px] text-muted-foreground">Unified Platform</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-md p-1.5 hover:bg-secondary transition-colors lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
          Workspace
        </p>
        <div className="space-y-0.5">
          {MAIN_NAV.map(({ href, label, icon }) => (
            <NavItem
              key={href}
              href={href}
              label={label}
              icon={icon}
              active={pathname.startsWith(href)}
              onClick={onClose}
            />
          ))}
        </div>

        <p className="mb-2 mt-6 px-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
          Configuration
        </p>
        <div className="space-y-0.5">
          {CONFIG_NAV.map(({ href, label, icon }) => (
            <NavItem
              key={href}
              href={href}
              label={label}
              icon={icon}
              active={pathname.startsWith(href)}
              onClick={onClose}
            />
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="shrink-0 border-t px-4 py-3">
        <p className="text-[11px] text-muted-foreground">MVP v1.0 · 2026</p>
      </div>
    </div>
  );
}

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setDrawerOpen(false);
  }, [pathname]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawerOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // Lock body scroll when drawer is open on mobile
  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [drawerOpen]);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 flex-col border-r bg-card lg:flex">
        <SidebarContent />
      </aside>

      {/* Right-side column */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Mobile top bar */}
        <header className="flex h-14 shrink-0 items-center gap-3 border-b bg-card px-4 lg:hidden">
          <button
            onClick={() => setDrawerOpen(true)}
            className="rounded-md p-1.5 transition-colors hover:bg-secondary"
            aria-label="Open navigation menu"
          >
            <HiMenuAlt2 className="h-6 w-6" />
          </button>
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
              <span className="text-[10px] font-bold text-primary-foreground">CP</span>
            </div>
            <span className="text-sm font-semibold">CPAAS Platform</span>
          </div>
        </header>

        {/* Page content */}
        <div className="flex-1 overflow-hidden">{children}</div>
      </div>

      {/* Mobile drawer */}
      {drawerOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
            onClick={() => setDrawerOpen(false)}
          />
          <aside className="fixed left-0 top-0 z-50 h-full w-72 bg-card shadow-2xl lg:hidden">
            <SidebarContent onClose={() => setDrawerOpen(false)} />
          </aside>
        </>
      )}
    </div>
  );
}
