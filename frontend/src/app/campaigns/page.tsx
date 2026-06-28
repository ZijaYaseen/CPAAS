import { Megaphone } from "lucide-react";
import { PostMvpPage } from "@/components/PostMvpPage";

export const metadata = { title: "Broadcasts — CPAAS" };

export default function CampaignsPage() {
  return (
    <PostMvpPage
      icon={Megaphone}
      title="Broadcast Campaigns"
      description="Send targeted bulk messages to segmented contact lists across WhatsApp, Email, and SMS with real-time delivery tracking."
      color="bg-orange-100 text-orange-600"
      phase="Post-MVP · Phase 5 (Weeks 15–16)"
      features={[
        "Campaign creation wizard with template editor",
        "Audience segmentation by tags & lifecycle stage",
        "Schedule sends for optimal timing",
        "WhatsApp, Email, and SMS support",
        "Real-time delivery & open tracking",
        "Pause, resume, and cancel campaigns",
      ]}
    />
  );
}
