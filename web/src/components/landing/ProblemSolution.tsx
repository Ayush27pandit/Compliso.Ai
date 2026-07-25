import { motion } from "framer-motion";
import { AlertTriangle, Layers, Network, Clock, Shield, Check } from "lucide-react";

export function ProblemSolution() {
  const problems = [
    { icon: <AlertTriangle className="w-5 h-5 text-amber-400" />, title: "A notification drops on a Saturday. Your client is filing Monday.", body: "N/N/07/2024, dated 06 July, effective immediately. You skim it, panic-quote a paragraph to a WhatsApp group, and hope for the best." },
    { icon: <Layers className="w-5 h-5 text-amber-400" />, title: "ITC claims sit in 2A vs 2B reconciliation hell for weeks.", body: "Missing invoices, mismatched GSTINs, vendors who filed but uploaded nothing. The difference is usually a six-figure recovery — if you catch it." },
    { icon: <Network className="w-5 h-5 text-amber-400" />, title: "Multi-state registrations mean five portals, five deadlines, one of you.", body: "Karnataka GSTR-1, Maharashtra GSTR-3B, Tamil Nadu payment, Kerala e-Way Bill — and a CFO who thought the CA was handling it." },
    { icon: <Clock className="w-5 h-5 text-amber-400" />, title: "CAs spend 60% of the week reading circulars — not advising clients.", body: "The actual work — the strategy, the structuring, the relationship — gets squeezed into the hours you'd rather be sleeping." },
  ];

  return (
    <section id="problem" className="relative bg-navy-950 dot-grid">
      <div className="max-w-[1280px] mx-auto px-5 md:px-8 py-24 md:py-36">
        <div className="grid lg:grid-cols-12 gap-10 lg:gap-16">
          <div className="lg:col-span-5 lg:sticky lg:top-28 self-start">
            <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.6 }}>
              <div className="inline-flex items-center gap-2 text-[11.5px] uppercase tracking-[0.18em] text-amber-400 font-medium">
                <span className="w-6 h-px bg-amber-400/60" /> The problem
              </div>
              <h2 className="mt-5 text-[36px] md:text-[48px] leading-[1.02] tracking-tight font-semibold text-ink-50">
                GST compliance was not designed for chaos.{" "}
                <span className="font-serif italic font-normal text-ink-200/70">Your quarter is.</span>
              </h2>
              <p className="mt-6 text-[15.5px] md:text-[16.5px] text-ink-200/70 leading-relaxed max-w-md">
                The rules shift, the portals lag, the notices land. Meanwhile, your team is the human middleware between the CBIC and your clients&apos; inboxes.
              </p>
              <div className="mt-10 p-5 md:p-6 rounded-2xl border border-accent-500/20 bg-accent-500/[0.04]">
                <div className="text-[11.5px] uppercase tracking-[0.18em] text-accent-400 font-medium">Our bet</div>
                <p className="mt-3 text-[18px] md:text-[19.5px] leading-[1.45] text-ink-50 font-medium tracking-tight">
                  Compliso does the reading, the reconciliation, and the deadline tracking — so your team does the actual work.
                </p>
                <div className="mt-5 flex flex-wrap items-center gap-2.5 text-[12px] text-ink-200/70">
                  <span className="inline-flex items-center gap-1.5"><Shield className="w-3.5 h-3.5 text-accent-400" /> Built in India, for India</span>
                  <span className="w-1 h-1 rounded-full bg-ink-300/30" />
                  <span className="inline-flex items-center gap-1.5"><Check className="w-3.5 h-3.5 text-accent-400" /> 50+ CA firms as design partners</span>
                </div>
              </div>
            </motion.div>
          </div>
          <div className="lg:col-span-7">
            <ul className="space-y-3 md:space-y-4">
              {problems.map((p, i) => (
                <motion.li key={i} initial={{ opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-40px" }} transition={{ delay: i * 0.07, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
                  className="group relative flex gap-4 md:gap-5 p-5 md:p-6 rounded-2xl border border-white/[0.06] bg-navy-900/60 hover:border-white/10 hover:-translate-y-0.5 transition-all duration-300">
                  <div className="shrink-0 w-10 h-10 rounded-lg bg-white/[0.04] border border-white/[0.05] grid place-items-center">{p.icon}</div>
                  <div className="min-w-0">
                    <h3 className="text-[15.5px] md:text-[17px] font-semibold text-ink-50 tracking-tight leading-snug">{p.title}</h3>
                    <p className="mt-2 text-[13.5px] md:text-[14.5px] text-ink-200/65 leading-relaxed">{p.body}</p>
                  </div>
                </motion.li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
