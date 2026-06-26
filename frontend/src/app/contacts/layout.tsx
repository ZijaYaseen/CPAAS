import { AppLayout } from "@/components/AppLayout";

export default function ContactsLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppLayout>
      <div className="h-full overflow-y-auto">{children}</div>
    </AppLayout>
  );
}
