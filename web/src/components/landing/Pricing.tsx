import { motion } from "framer-motion";
import { Check, Zap, Building2, Crown } from "lucide-react";

const plans = [
  {
    name: "Starter",
    price: "Free",
    period: "forever",
    description: "For solo CAs exploring Compliso",
    icon: <Zap className="w-5 h-5 text-accent-400" />,
    features: [
      "50 queries/month",
      "GST knowledge base access",
      "Basic compliance checks",
      "Community support",
    ],
    cta: "Get Started",
    accent: false,
  },
  {
    name: "Professional",
    price: "\u20B92,999",
    period: "/month",
    description: "For growing CA practices",
    icon: <Building2 className="w-5 h-5 text-accent-400" />,
    features: [
      "Unlimited queries",
      "Custom document ingestion",
      "Advanced guardrails",
      "Priority support",
      "SSE streaming",
      "Multi-user (up to 5)",
    ],
    cta: "Start Free Trial",
    accent: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For large firms and institutions",
    icon: <Crown className="w-5 h-5 text-accent-400" />,
    features: [
      "Everything in Professional",
      "Custom deployment",
      "SSO & team management",
      "Dedicated support",
      "SLA guarantees",
      "On-premise option",
    ],
    cta: "Contact Sales",
    accent: false,
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="relative bg-navy-950 dot-grid">
      <div className="max-w-[1280px] mx-auto px-5 md:px-8 py-24 md:py-36">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-2xl mx-auto mb-16 md:mb-20"
        >
          <div className="inline-flex items-center gap-2 text-[11.5px] uppercase tracking-[0.18em] text-accent-400 font-medium">
            <span className="w-6 h-px bg-accent-400/60" /> Pricing
            <span className="w-6 h-px bg-accent-400/60" />
          </div>
          <h2 className="mt-5 text-[36px] md:text-[48px] leading-[1.02] tracking-tight font-semibold text-ink-50">
            Start free.{" "}
            <span className="font-serif italic font-normal text-ink-200/70">Scale when ready.</span>
          </h2>
          <p className="mt-5 text-[15.5px] md:text-[16.5px] text-ink-200/65 leading-relaxed">
            No credit card required. Upgrade as your practice grows.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6 max-w-5xl mx-auto">
          {plans.map((p, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{
                delay: i * 0.1,
                duration: 0.6,
                ease: [0.22, 1, 0.36, 1],
              }}
              className={`relative flex flex-col p-7 md:p-8 rounded-2xl border transition-all duration-300 hover:-translate-y-1 ${
                p.accent
                  ? "border-accent-500/30 bg-accent-500/[0.06] shadow-glow-accent"
                  : "border-white/[0.06] bg-navy-900/60 hover:border-white/10"
              }`}
            >
              {p.accent && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[10px] uppercase tracking-[0.18em] bg-accent-500 text-navy-950 font-semibold px-3 py-1 rounded-full">
                  Most Popular
                </div>
              )}
              <div className="flex items-center gap-2 mb-4">
                {p.icon}
                <span className="text-[13px] uppercase tracking-[0.15em] text-ink-300/60 font-medium">
                  {p.name}
                </span>
              </div>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="text-[36px] md:text-[42px] font-semibold text-ink-50 tracking-tight">
                  {p.price}
                </span>
                {p.period && (
                  <span className="text-[14px] text-ink-200/50">{p.period}</span>
                )}
              </div>
              <p className="text-[13.5px] text-ink-200/60 leading-relaxed mb-6">
                {p.description}
              </p>
              <ul className="space-y-3 flex-1 mb-8">
                {p.features.map((f, j) => (
                  <li
                    key={j}
                    className="flex items-start gap-2.5 text-[13.5px] text-ink-200/75"
                  >
                    <Check className="w-4 h-4 text-accent-400 mt-0.5 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <button
                className={`w-full py-3 rounded-xl text-[14px] font-medium transition-all duration-200 ${
                  p.accent
                    ? "bg-accent-500 hover:bg-accent-600 text-navy-950 btn-shimmer"
                    : "border border-white/10 bg-white/[0.03] hover:bg-white/[0.06] text-ink-100"
                }`}
              >
                {p.cta}
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
