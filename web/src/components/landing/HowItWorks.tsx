import { motion } from "framer-motion";
import { MessageSquare, Search, Sparkles } from "lucide-react";

const steps = [
  {
    num: "01",
    icon: <MessageSquare className="w-6 h-6 text-accent-400" />,
    title: "Ask your question",
    body: "Type in natural language — English or Hinglish. No portal navigation, no form fields.",
  },
  {
    num: "02",
    icon: <Search className="w-6 h-6 text-accent-400" />,
    title: "Agent reasons over your data",
    body: "LangGraph breaks it into sub-queries, retrieves across all your documents, reranks, and validates.",
  },
  {
    num: "03",
    icon: <Sparkles className="w-6 h-6 text-accent-400" />,
    title: "Get an answer you can trust",
    body: "Cited, up-to-date, and validated against custom guardrails. If something's outdated, it flags it.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="relative bg-navy-900">
      <div className="max-w-[1280px] mx-auto px-5 md:px-8 py-24 md:py-36">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-2xl mx-auto mb-16 md:mb-20"
        >
          <div className="inline-flex items-center gap-2 text-[11.5px] uppercase tracking-[0.18em] text-accent-400 font-medium">
            <span className="w-6 h-px bg-accent-400/60" /> How it works
            <span className="w-6 h-px bg-accent-400/60" />
          </div>
          <h2 className="mt-5 text-[36px] md:text-[48px] leading-[1.02] tracking-tight font-semibold text-ink-50">
            Three steps.{" "}
            <span className="font-serif italic font-normal text-ink-200/70">No dashboard.</span>
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          {steps.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{
                delay: i * 0.12,
                duration: 0.6,
                ease: [0.22, 1, 0.36, 1],
              }}
              className="relative text-center md:text-left"
            >
              {i < steps.length - 1 && (
                <div className="hidden md:block absolute top-10 left-[calc(50%+60px)] w-[calc(100%-40px)] h-px bg-gradient-to-r from-accent-500/30 to-transparent" />
              )}
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-accent-500/[0.08] border border-accent-500/20 mb-6">
                {s.icon}
              </div>
              <div className="text-[11px] uppercase tracking-[0.2em] text-ink-300/40 font-medium mb-2">
                Step {s.num}
              </div>
              <h3 className="text-[20px] md:text-[22px] font-semibold text-ink-50 tracking-tight leading-snug">
                {s.title}
              </h3>
              <p className="mt-3 text-[14.5px] md:text-[15.5px] text-ink-200/65 leading-relaxed max-w-sm mx-auto md:mx-0">
                {s.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
