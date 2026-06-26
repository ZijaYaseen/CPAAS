import { Ticket } from "lucide-react";
import { PostMvpPage } from "@/components/PostMvpPage";

export const metadata = { title: "Tickets — CPAAS" };

export default function TicketsPage() {
  return (
    <PostMvpPage
      icon={Ticket}
      title="Ticket Management"
      description="Track customer issues end-to-end with SLA enforcement, priority queues, and automated escalation rules."
      color="bg-rose-100 text-rose-600"
      phase="Post-MVP · Phase 6 (Weeks 13–14)"
      features={[
        "Create tickets directly from conversations",
        "Priority levels: Low / Medium / High / Critical",
        "SLA deadlines with breach alerts",
        "Auto-escalation rules engine",
        "Ticket history & audit trail",
        "Team assignment & workload view",
      ]}
    />
  );
}
