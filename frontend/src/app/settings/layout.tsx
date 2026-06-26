import { AppLayout } from "@/components/AppLayout";

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppLayout>
      <div className="h-full overflow-y-auto p-6">{children}</div>
    </AppLayout>
  );
}
