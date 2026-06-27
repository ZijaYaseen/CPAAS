import Link from "next/link";

const features = [
  {
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
        <path d="M8 10h8M8 14h5M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
      </svg>
    ),
    title: "Unified Inbox",
    desc: "All your customer conversations from WhatsApp, Email, and Web Chat in a single, clean inbox. No switching tabs.",
  },
  {
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
        <path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2z" stroke="currentColor" strokeWidth="1.8"/>
        <path d="M12 8v4l3 3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
        <path d="M9 2.5C6 4 4 6 3.5 9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
      </svg>
    ),
    title: "AI Powered Automation",
    desc: "Gemini AI reads your knowledge base and responds instantly to routine queries — 24 hours a day, 7 days a week.",
  },
  {
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
        <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="1.8"/>
        <path d="M3 9h18M9 21V9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
      </svg>
    ),
    title: "Multi Tenant Platform",
    desc: "Built for agencies and SaaS businesses. Each organization gets its own isolated workspace, users, and data.",
  },
  {
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
        <path d="M3 12l4-4 4 4 4-6 4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
        <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="1.8"/>
      </svg>
    ),
    title: "Real Time Analytics",
    desc: "Track response times, conversation volumes, AI performance, and team productivity with live dashboards.",
  },
  {
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
    title: "Enterprise Security",
    desc: "Session based auth, CSRF protection, rate limiting, row level security, and full audit logs built in from day one.",
  },
  {
    icon: (
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8"/>
        <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
      </svg>
    ),
    title: "WebSocket Live Updates",
    desc: "Every new message, assignment, and status change appears instantly across all connected agents with zero refresh.",
  },
];

const stats = [
  { value: "10K+", label: "Messages per day" },
  { value: "99.9%", label: "Uptime SLA" },
  { value: "200ms", label: "Avg response time" },
  { value: "2 min", label: "Setup time" },
];

const channels = ["WhatsApp", "Email", "Web Chat"];

export default function Home() {
  return (
    <div style={{ fontFamily: "system-ui, -apple-system, sans-serif" }}>

      {/* ── HERO ── */}
      <section
        className="relative min-h-screen flex flex-col overflow-hidden"
        style={{
          background: "linear-gradient(145deg, #0f0024 0%, #1a0533 30%, #2d0a6e 65%, #4c1d95 100%)",
        }}
      >
        {/* Orbs */}
        <div
          className="auth-orb-1 absolute rounded-full pointer-events-none"
          style={{
            width: 600, height: 600,
            background: "radial-gradient(circle, rgba(167,139,250,0.25), rgba(124,58,237,0.05))",
            filter: "blur(80px)",
            top: -200, left: -150,
          }}
        />
        <div
          className="auth-orb-2 absolute rounded-full pointer-events-none"
          style={{
            width: 500, height: 500,
            background: "radial-gradient(circle, rgba(192,132,252,0.2), transparent)",
            filter: "blur(70px)",
            bottom: -100, right: -100,
          }}
        />
        <div
          className="auth-orb-3 absolute rounded-full pointer-events-none"
          style={{
            width: 300, height: 300,
            background: "radial-gradient(circle, rgba(244,114,182,0.15), transparent)",
            filter: "blur(60px)",
            top: "40%", right: "20%",
          }}
        />

        {/* Grid */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />

        {/* Navbar */}
        <nav className="relative z-10 flex items-center justify-between px-8 py-6 max-w-6xl mx-auto w-full">
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #6d28d9)" }}
            >
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="white"/>
              </svg>
            </div>
            <span className="text-white font-bold text-xl tracking-tight">CPaaS</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-purple-200 text-sm font-medium px-4 py-2 rounded-lg hover:text-white hover:bg-white/10 transition-all"
            >
              Sign in
            </Link>
            <Link
              href="/register"
              className="text-white text-sm font-semibold px-5 py-2 rounded-xl transition-all duration-200"
              style={{
                background: "linear-gradient(135deg, #8b5cf6, #7c3aed)",
                boxShadow: "0 4px 15px rgba(124,58,237,0.4)",
              }}
            >
              Get started free
            </Link>
          </div>
        </nav>

        {/* Hero content */}
        <div className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 py-20 max-w-5xl mx-auto w-full">
          <div
            className="auth-slide-up-1 inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium text-purple-200 mb-8"
            style={{
              background: "rgba(139,92,246,0.2)",
              border: "1px solid rgba(167,139,250,0.3)",
            }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            Now live · Powered by Gemini AI
          </div>

          <h1
            className="auth-slide-up-2 text-5xl md:text-7xl font-bold text-white leading-tight mb-6"
          >
            Every customer<br />conversation,{" "}
            <span style={{
              background: "linear-gradient(90deg, #c084fc, #a78bfa, #e879f9)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}>
              one inbox
            </span>
          </h1>

          <p className="auth-slide-up-3 text-purple-200 text-lg md:text-xl max-w-2xl leading-relaxed mb-10">
            CPaaS unifies WhatsApp, Email, and Web Chat into a single AI powered workspace.
            Automate responses, assign conversations, and delight customers at scale.
          </p>

          {/* CTA buttons */}
          <div className="auth-slide-up-4 flex flex-col sm:flex-row items-center gap-4 mb-14">
            <Link
              href="/register"
              className="flex items-center gap-2 px-8 py-4 rounded-xl text-white font-semibold text-base transition-all duration-200"
              style={{
                background: "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%)",
                boxShadow: "0 6px 24px rgba(124,58,237,0.5)",
              }}
            >
              Start free trial
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
                <path d="M5 12h14M13 6l6 6-6 6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
            <Link
              href="/login"
              className="flex items-center gap-2 px-8 py-4 rounded-xl text-purple-100 font-semibold text-base transition-all duration-200 hover:bg-white/10"
              style={{ border: "1px solid rgba(167,139,250,0.35)" }}
            >
              Sign in to workspace
            </Link>
          </div>

          {/* Channel badges */}
          <div className="auth-slide-up-5 flex items-center gap-3 flex-wrap justify-center">
            <span className="text-purple-400 text-sm">Connects with</span>
            {channels.map((ch) => (
              <span
                key={ch}
                className="px-3 py-1 rounded-full text-xs font-medium text-purple-200"
                style={{
                  background: "rgba(255,255,255,0.07)",
                  border: "1px solid rgba(167,139,250,0.2)",
                }}
              >
                {ch}
              </span>
            ))}
          </div>
        </div>

        {/* Stats bar */}
        <div className="relative z-10 w-full max-w-4xl mx-auto px-6 pb-16">
          <div
            className="grid grid-cols-2 md:grid-cols-4 gap-px rounded-2xl overflow-hidden"
            style={{ background: "rgba(167,139,250,0.15)" }}
          >
            {stats.map(({ value, label }) => (
              <div
                key={label}
                className="flex flex-col items-center justify-center py-6 px-4 text-center"
                style={{ background: "rgba(15,0,36,0.6)", backdropFilter: "blur(12px)" }}
              >
                <p
                  className="text-2xl font-bold mb-1"
                  style={{
                    background: "linear-gradient(90deg, #c084fc, #a78bfa)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }}
                >
                  {value}
                </p>
                <p className="text-purple-300 text-xs">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section className="bg-white py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold text-purple-700 mb-4"
              style={{ background: "#f3e8ff", border: "1px solid #e9d5ff" }}
            >
              Everything you need
            </div>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Built for modern support teams
            </h2>
            <p className="text-gray-500 text-lg max-w-xl mx-auto">
              From AI automation to real time analytics — CPaaS has every tool your team needs to deliver exceptional customer experiences.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <div
                key={f.title}
                className="p-6 rounded-2xl border border-gray-100 hover:border-purple-200 transition-all duration-200 group"
                style={{ background: i % 2 === 0 ? "#fafafa" : "white" }}
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 text-purple-600 group-hover:scale-110 transition-transform duration-200"
                  style={{ background: "#f3e8ff" }}
                >
                  {f.icon}
                </div>
                <h3 className="font-semibold text-gray-900 text-base mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── BOTTOM CTA ── */}
      <section
        className="relative py-24 px-6 overflow-hidden"
        style={{
          background: "linear-gradient(135deg, #0f0024 0%, #2d0a6e 50%, #4c1d95 100%)",
        }}
      >
        <div
          className="auth-orb-1 absolute rounded-full pointer-events-none"
          style={{
            width: 500, height: 500,
            background: "radial-gradient(circle, rgba(192,132,252,0.2), transparent)",
            filter: "blur(80px)",
            top: -150, left: -100,
          }}
        />
        <div
          className="auth-orb-2 absolute rounded-full pointer-events-none"
          style={{
            width: 400, height: 400,
            background: "radial-gradient(circle, rgba(167,139,250,0.15), transparent)",
            filter: "blur(70px)",
            bottom: -100, right: -100,
          }}
        />

        <div className="relative z-10 max-w-3xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to transform your{" "}
            <span style={{
              background: "linear-gradient(90deg, #c084fc, #e879f9)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}>
              customer support?
            </span>
          </h2>
          <p className="text-purple-200 text-lg mb-10 leading-relaxed">
            Set up your workspace in 2 minutes. No credit card required.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="flex items-center gap-2 px-8 py-4 rounded-xl text-white font-semibold text-base transition-all duration-200"
              style={{
                background: "linear-gradient(135deg, #8b5cf6, #7c3aed)",
                boxShadow: "0 6px 24px rgba(124,58,237,0.5)",
              }}
            >
              Create free workspace
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
                <path d="M5 12h14M13 6l6 6-6 6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 rounded-xl text-purple-200 font-medium text-base hover:text-white transition-colors"
            >
              Already have an account?
            </Link>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer
        className="py-8 px-6 text-center"
        style={{ background: "#0f0024", borderTop: "1px solid rgba(167,139,250,0.1)" }}
      >
        <div className="flex items-center justify-center gap-2 mb-3">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, #8b5cf6, #6d28d9)" }}
          >
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="white"/>
            </svg>
          </div>
          <span className="text-white font-bold">CPaaS</span>
        </div>
        <p className="text-purple-500 text-xs">
          AI powered unified communication platform · Built with Next.js and FastAPI
        </p>
      </footer>

    </div>
  );
}
