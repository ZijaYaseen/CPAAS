import { Users } from "lucide-react";
import { PostMvpPage } from "@/components/PostMvpPage";

export const metadata = { title: "Contacts — CPAAS" };

export default function ContactsPage() {
  return (
    <PostMvpPage
      icon={Users}
      title="Contact Management"
      description="A full CRM layer with rich contact profiles, segmentation, and lifecycle tracking — all linked to your conversations."
      color="bg-violet-100 text-violet-600"
      phase="Post-MVP · Phase 7 (Weeks 13–14)"
      features={[
        "Rich contact profiles with custom fields",
        "Tag-based segmentation & filtering",
        "Lifecycle stage tracking (Lead → Customer)",
        "Full conversation & ticket timeline per contact",
        "Bulk CSV import / export",
        "Duplicate detection & merge",
      ]}
    />
  );
}
