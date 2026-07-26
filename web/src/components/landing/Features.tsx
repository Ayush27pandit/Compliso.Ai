import { motion } from "framer-motion";
import {
  Brain,
  FileSearch,
  Shield,
  Clock,
  Database,
  Zap,
  MessageSquare,
  AlertCircle,
} from "lucide-react";

const features = [
  {
    icon: <Brain className="w-6 h-6 text-accent-400" />,
    title: "LangGraph AI Agent",
    body: "Multi-step reasoning that breaks complex questions into sub-queries, retrieves across all your documents, and synthesizes accurate answers.",
    span: "md:col-span-2 md:row-span-2",
    accent: true,
  },
  {
    icon: <FileSearch className="w-5 h-5 text-accent-400" />,
    title: "Smart Retrieval + Reranking",
    body: "Qdrant vector search with FlashRank reranking. Only the most relevant chunks make it to the LLM.",
    span: "md:col-span-1",
    accent: false,
  },
  {
    icon: <Shield className="w-5 h-5 text-accent-400" />,
    title: "Custom Guardrails",
    body: "Input filtering, output validation, and hallucination detection — all under 20ms overhead.",
    span: "md:col-span-1",
    accent: false,
  },
  {
    icon: <Clock className="w-5 h-5 text-accent-400" />,
    title: "Deadline Tracking",
    body: "GSTR-1, 3B, 9, composition — know exactly what's due and when. Never miss a filing.",
    span: "md:col-span-1",
    accent: false,
  },
  {
    icon: <Database className="w-5 h-5 text-accent-400" />,
    title: "GST 2.0 Updated Knowledge",
    body: "Always current with the latest rates, thresholds, and reforms. No outdated information.",
    span: "md:col-span-1",
    accent: false,
  },
  {
    icon: <Zap className="w-5 h-5 text-accent-400" />,
    title: "SSE Streaming Responses",
    body: "Answers stream in real-time. No waiting for the full response — start reading as it generates.",
    span: "md:col-span-1",
    accent: false,
  },
  {
    icon: <MessageSquare className="w-5 h-5 text-accent-400" />,
    title: "Natural Language Interface",
    body: "Ask in plain English or Hinglish. No forms, no dropdowns, no GST portal navigation.",
    span: "md:col-span-1",
    accent: false,
  },
  {
    icon: <AlertCircle className="w-5 h-5 text-accent-400" />,
    title: "Outdated Info Detection",
    body: "Automatically flags speculative or outdated information from external sources before it reaches your answer.",
    span: "md:col-span-1",
    accent: false,
  },
];

export function Features() {
  return (
    <section id="features" className="relative bg-navy-950 dot-grid">
      <div className="max-w-[1280px] mx-auto px-5 md:px-8 py-24 md:py-36">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-2xl mx-auto mb-16 md:mb-20"
        >
          <div className="inline-flex items-center gap-2 text-[11.5px] uppercase tracking-[0.18em] text-accent-400 font-medium">
            <span className="w-6 h-px bg-accent-400/60" /> Capabilities
            <span className="w-6 h-px bg-accent-400/60" />
          </div>
          <h2 className="mt-5 text-[36px] md:text-[48px] leading-[1.02] tracking-tight font-semibold text-ink-50">
            Built for how CAs{" "}
            <span className="font-serif italic font-normal text-ink-200/70">actually work</span>
          </h2>
          <p className="mt-5 text-[15.5px] md:text-[16.5px] text-ink-200/65 leading-relaxed">
            Every feature is designed to reduce cognitive load, not add another tool to learn.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
          {features.map((f, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{
                delay: i * 0.05,
                duration: 0.55,
                ease: [0.22, 1, 0.36, 1],
              }}
              className={`group relative p-6 md:p-8 rounded-2xl border transition-all duration-300 hover:-translate-y-0.5 ${
                f.accent
                  ? "border-accent-500/25 bg-accent-500/[0.05] hover:border-accent-500/40"
                  : "border-white/[0.06] bg-navy-900/60 hover:border-white/10"
              } ${f.span}`}
            >
              <div className="w-10 h-10 rounded-lg bg-white/[0.04] border border-white/[0.05] grid place-items-center mb-5">
                {f.icon}
              </div>
              <h3 className="text-[17px] md:text-[18px] font-semibold text-ink-50 tracking-tight leading-snug">
                {f.title}
              </h3>
              <p className="mt-3 text-[13.5px] md:text-[14.5px] text-ink-200/65 leading-relaxed">
                {f.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
