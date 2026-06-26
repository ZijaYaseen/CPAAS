import { type LucideIcon, CheckCircle2, Clock, Rocket } from "lucide-react";

interface Props {
  icon: LucideIcon;
  title: string;
  description: string;
  features: string[];
  phase: string;
  color: string;
}

export function PostMvpPage({ icon: Icon, title, description, features, phase, color }: Props) {
  return (
    <div className="flex h-full flex-col items-center justify-center p-6 sm:p-10">
      <div className="w-full max-w-lg">
        {/* Icon badge */}
        <div className={`mb-6 inline-flex rounded-2xl p-4 ${color}`}>
          <Icon className="h-8 w-8" />
        </div>

        {/* Heading */}
        <h1 className="mb-3 text-2xl font-bold tracking-tight sm:text-3xl">{title}</h1>
        <p className="mb-8 text-base text-muted-foreground leading-relaxed">{description}</p>

        {/* Features list */}
        <div className="mb-8 rounded-xl border bg-card p-5 shadow-sm">
          <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            What&apos;s included
          </p>
          <ul className="space-y-2.5">
            {features.map((f) => (
              <li key={f} className="flex items-start gap-2.5 text-sm">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Timeline badge */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2 rounded-lg border bg-amber-50 px-4 py-2.5 text-sm text-amber-800">
            <Clock className="h-4 w-4 shrink-0" />
            <span className="font-medium">{phase}</span>
          </div>
          <div className="flex items-center gap-2 rounded-lg border bg-blue-50 px-4 py-2.5 text-sm text-blue-800">
            <Rocket className="h-4 w-4 shrink-0" />
            <span>Launching after MVP validation</span>
          </div>
        </div>
      </div>
    </div>
  );
}
