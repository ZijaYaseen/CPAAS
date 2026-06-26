import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { TenantProvider } from "@/contexts/TenantContext";

export const metadata: Metadata = {
  title: "Unified Communication Platform",
  description: "AI-powered unified inbox for multi-channel customer communication",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <TenantProvider>{children}</TenantProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
