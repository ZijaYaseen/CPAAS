"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

const steps = [
  { label: "Organization", icon: "🏢" },
  { label: "Your info", icon: "👤" },
  { label: "Security", icon: "🔒" },
];

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [orgName, setOrgName] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const passwordStrength = (() => {
    if (password.length === 0) return 0;
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  })();

  const strengthLabel = ["", "Weak", "Fair", "Good", "Strong"][passwordStrength];
  const strengthColor = ["", "#ef4444", "#f59e0b", "#a78bfa", "#22c55e"][passwordStrength];

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register({
        organization_name: orgName,
        full_name: fullName || undefined,
        email,
        password,
      });
      router.push("/inbox");
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { error?: { message?: string } } } })?.response?.data?.error
          ?.message ?? "Registration failed. Please try again.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-screen">
      {/* LEFT PANEL */}
      <div
        className="hidden lg:flex lg:w-[45%] flex-col justify-between p-12 relative overflow-hidden"
        style={{
          background: "linear-gradient(145deg, #0f0024 0%, #1a0533 25%, #2d0a6e 60%, #4c1d95 100%)",
        }}
      >
        {/* Orbs */}
        <div
          className="auth-orb-1 absolute rounded-full pointer-events-none"
          style={{
            width: 420, height: 420,
            background: "radial-gradient(circle, rgba(192,132,252,0.3), rgba(124,58,237,0.08))",
            filter: "blur(60px)",
            top: -100, right: -100,
          }}
        />
        <div
          className="auth-orb-2 absolute rounded-full pointer-events-none"
          style={{
            width: 300, height: 300,
            background: "radial-gradient(circle, rgba(167,139,250,0.25), transparent)",
            filter: "blur(50px)",
            bottom: 60, left: -60,
          }}
        />
        <div
          className="auth-orb-3 absolute rounded-full pointer-events-none"
          style={{
            width: 180, height: 180,
            background: "radial-gradient(circle, rgba(244,114,182,0.2), transparent)",
            filter: "blur(40px)",
            top: "45%", right: 40,
          }}
        />

        {/* Grid */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
            backgroundSize: "44px 44px",
          }}
        />

        {/* Logo */}
        <div className="relative z-10 auth-slide-up-1">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #6d28d9)" }}
            >
              <svg width="22" height="22" fill="none" viewBox="0 0 24 24">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="white"/>
              </svg>
            </div>
            <span className="text-white font-bold text-xl tracking-tight">CPaaS</span>
          </div>
        </div>

        {/* Copy */}
        <div className="relative z-10 space-y-8">
          <div className="auth-slide-up-2 space-y-4">
            <div
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium text-purple-200"
              style={{
                background: "rgba(139,92,246,0.2)",
                border: "1px solid rgba(167,139,250,0.3)",
              }}
            >
              <svg width="12" height="12" fill="#c084fc" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              Free 14 day trial · No credit card
            </div>

            <h1 className="text-4xl font-bold text-white leading-tight">
              Launch your<br />
              <span style={{
                background: "linear-gradient(90deg, #c084fc, #a78bfa, #e879f9)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}>
                workspace today
              </span>
            </h1>
            <p className="text-purple-200 text-base leading-relaxed">
              Join thousands of teams using CPaaS to manage customer conversations at scale.
            </p>
          </div>

          {/* Steps */}
          <div className="space-y-3">
            <p className="text-purple-400 text-xs font-semibold uppercase tracking-widest">Setup takes 2 minutes</p>
            {steps.map((step, i) => (
              <div
                key={step.label}
                className="flex items-center gap-4 auth-slide-up"
                style={{ animationDelay: `${0.3 + i * 0.1}s`, animationFillMode: "both" }}
              >
                <div
                  className="w-9 h-9 rounded-xl flex items-center justify-center text-base flex-shrink-0"
                  style={{
                    background: "rgba(255,255,255,0.07)",
                    border: "1px solid rgba(167,139,250,0.2)",
                  }}
                >
                  {step.icon}
                </div>
                <div className="flex items-center gap-2 flex-1">
                  <span
                    className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold text-purple-200 flex-shrink-0"
                    style={{ background: "rgba(139,92,246,0.3)" }}
                  >
                    {i + 1}
                  </span>
                  <span className="text-purple-100 text-sm font-medium">{step.label}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Testimonial */}
          <div
            className="auth-slide-up-5 p-5 rounded-2xl"
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(167,139,250,0.15)",
            }}
          >
            <div className="flex items-start gap-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0"
                style={{ background: "linear-gradient(135deg, #8b5cf6, #6d28d9)" }}
              >
                A
              </div>
              <div>
                <p className="text-purple-100 text-sm leading-relaxed italic">
                  &ldquo;CPaaS reduced our response time by 60%. The AI handles routine queries so our team can focus on complex issues.&rdquo;
                </p>
                <p className="text-purple-400 text-xs mt-2 font-medium">Ali Raza · Head of Support, ABC Pvt Ltd</p>
              </div>
            </div>
          </div>
        </div>

        {/* Avatars */}
        <div className="relative z-10 auth-slide-up-5">
          <div className="flex items-center gap-3">
            <div className="flex -space-x-2">
              {["#8b5cf6", "#7c3aed", "#a855f7", "#6d28d9"].map((color, i) => (
                <div
                  key={i}
                  className="w-8 h-8 rounded-full border-2 flex items-center justify-center text-white text-xs font-bold"
                  style={{ background: color, borderColor: "#1a0533" }}
                >
                  {["Z", "A", "S", "M"][i]}
                </div>
              ))}
            </div>
            <p className="text-purple-300 text-xs">
              <span className="text-white font-semibold">2,400+ teams</span> already on CPaaS
            </p>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-white relative overflow-y-auto">
        {/* Mobile logo */}
        <div className="lg:hidden mb-8 flex items-center gap-2">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, #8b5cf6, #6d28d9)" }}
          >
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="white"/>
            </svg>
          </div>
          <span className="font-bold text-xl text-gray-900">CPaaS</span>
        </div>

        <div className="w-full max-w-md">
          <div className="auth-slide-up-1 mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Create your workspace</h2>
            <p className="text-gray-500 mt-1.5 text-sm">Set up your team in under 2 minutes</p>
          </div>

          <form onSubmit={onSubmit} className="space-y-4">
            {/* Org */}
            <div className="auth-slide-up-1 space-y-1.5">
              <label className="block text-sm font-medium text-gray-700">Organization name</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-3.5 flex items-center pointer-events-none text-gray-400">
                  <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" strokeWidth="1.8"/>
                    <path d="M9 22V12h6v10" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                  </svg>
                </div>
                <input
                  placeholder="Acme Inc."
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  required
                  className="auth-input-field w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 placeholder-gray-400 text-sm"
                />
              </div>
            </div>

            {/* Name */}
            <div className="auth-slide-up-2 space-y-1.5">
              <label className="block text-sm font-medium text-gray-700">
                Your full name <span className="text-gray-400 font-normal">(optional)</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-3.5 flex items-center pointer-events-none text-gray-400">
                  <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                    <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="1.8"/>
                  </svg>
                </div>
                <input
                  placeholder="Ali Raza"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="auth-input-field w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 placeholder-gray-400 text-sm"
                />
              </div>
            </div>

            {/* Email */}
            <div className="auth-slide-up-3 space-y-1.5">
              <label className="block text-sm font-medium text-gray-700">Work email</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-3.5 flex items-center pointer-events-none text-gray-400">
                  <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" strokeWidth="1.8"/>
                    <path d="M22 6l-10 7L2 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                  </svg>
                </div>
                <input
                  type="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="auth-input-field w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 placeholder-gray-400 text-sm"
                />
              </div>
            </div>

            {/* Password */}
            <div className="auth-slide-up-4 space-y-1.5">
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-3.5 flex items-center pointer-events-none text-gray-400">
                  <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                    <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="1.8"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                  </svg>
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Min 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={8}
                  required
                  className="auth-input-field w-full pl-10 pr-12 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 placeholder-gray-400 text-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-3.5 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showPassword ? (
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                      <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                    </svg>
                  ) : (
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" strokeWidth="1.8"/>
                      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8"/>
                    </svg>
                  )}
                </button>
              </div>

              {password.length > 0 && (
                <div className="space-y-1.5">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4].map((lvl) => (
                      <div
                        key={lvl}
                        className="flex-1 h-1 rounded-full transition-all duration-300"
                        style={{ background: lvl <= passwordStrength ? strengthColor : "#e5e7eb" }}
                      />
                    ))}
                  </div>
                  <p className="text-xs font-medium" style={{ color: strengthColor }}>
                    {strengthLabel} password
                  </p>
                </div>
              )}
            </div>

            {/* Error */}
            {error && (
              <div
                className="flex items-center gap-2.5 px-4 py-3 rounded-xl text-sm"
                style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#dc2626" }}
              >
                <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.8"/>
                  <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                  <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                {error}
              </div>
            )}

            {/* Submit */}
            <div className="auth-slide-up-5 pt-1">
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 rounded-xl text-white font-semibold text-sm disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all duration-200"
                style={{
                  background: submitting
                    ? "#7c3aed"
                    : "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%)",
                  boxShadow: submitting ? "none" : "0 4px 20px rgba(124,58,237,0.4)",
                }}
                onMouseEnter={(e) => {
                  if (!submitting) (e.currentTarget as HTMLButtonElement).style.boxShadow = "0 8px 28px rgba(124,58,237,0.55)";
                }}
                onMouseLeave={(e) => {
                  if (!submitting) (e.currentTarget as HTMLButtonElement).style.boxShadow = "0 4px 20px rgba(124,58,237,0.4)";
                }}
              >
                {submitting ? (
                  <>
                    <svg className="animate-spin" width="16" height="16" fill="none" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" stroke="white" strokeWidth="2" opacity="0.25"/>
                      <path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Creating workspace
                  </>
                ) : (
                  <>
                    Create workspace
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                      <path d="M5 12h14M13 6l6 6-6 6" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="mt-6 flex items-center gap-4">
            <div className="flex-1 h-px bg-gray-100" />
            <span className="text-xs text-gray-400">Already have a workspace?</span>
            <div className="flex-1 h-px bg-gray-100" />
          </div>

          <div className="mt-4">
            <Link
              href="/login"
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border border-gray-200 text-gray-700 text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              Sign in instead
            </Link>
          </div>

          <p className="mt-6 text-center text-xs text-gray-400 leading-relaxed">
            By creating an account you agree to our{" "}
            <span className="font-medium text-gray-600 cursor-pointer hover:underline">Terms of Service</span>
            {" and "}
            <span className="font-medium text-gray-600 cursor-pointer hover:underline">Privacy Policy</span>
          </p>
        </div>
      </div>
    </main>
  );
}
