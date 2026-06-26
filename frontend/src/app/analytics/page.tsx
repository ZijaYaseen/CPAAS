import { BarChart3 } from "lucide-react";
import { PostMvpPage } from "@/components/PostMvpPage";

export const metadata = { title: "Analytics — CPAAS" };

export default function AnalyticsPage() {
  return (
    <PostMvpPage
      icon={BarChart3}
      title="Analytics & Reporting"
      description="Data-driven dashboards to monitor team performance, AI deflection rates, campaign ROI, and channel-level message volume."
      color="bg-sky-100 text-sky-600"
      phase="Post-MVP · Phase 9 (Weeks 18–20)"
      features={[
        "First Response Time (FRT) & Average Resolution Time",
        "AI deflection rate & handoff breakdown",
        "Agent productivity & workload heatmaps",
        "Campaign performance (delivery, opens, replies)",
        "Channel-level volume trends",
        "CSV / Excel data export",
      ]}
    />
  );
}
