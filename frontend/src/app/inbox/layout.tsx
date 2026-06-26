import { WebSocketProvider } from "@/contexts/WebSocketContext";
import { AppLayout } from "@/components/AppLayout";

export default function InboxLayout({ children }: { children: React.ReactNode }) {
  return (
    <WebSocketProvider>
      <AppLayout>{children}</AppLayout>
    </WebSocketProvider>
  );
}
