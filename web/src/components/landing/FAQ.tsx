import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Minus } from "lucide-react";

const cls = (...x: (string | boolean | undefined | null)[]) => x.filter(Boolean).join(" ");

function FAQItem({ item, open, onToggle }: { item: { q: string; a: string }; open: boolean; onToggle: () => void }) {
  return (
    <div className="group">
      <button onClick={onToggle} className="w-full flex items-center justify-between gap-6 py-6 text-left" aria-expanded={open}>
        <span className="text-[16.5px] md:text-[18.5px] font-medium tracking-tight text-ink-50 group-hover:text-accent-400 transition-colors">{item.q}</span>
        <span className={cls("shrink-0 w-9 h-9 rounded-full grid place-items-center border transition-all duration-300", open ? "bg-accent-500 border-accent-500 text-navy-950 rotate-180" : "bg-white/[0.03] border-white/10 text-ink-200")}>
          {open ? <Minus className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
        </span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }} className="overflow-hidden">
            <p className="pb-6 pr-12 text-[14.5px] md:text-[15.5px] text-ink-200/70 leading-[1.65] max-w-3xl">{item.a}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function FAQ() {
  const data = [
    { q: "How current is Compliso's knowledge base, really?", a: "We index CBIC notifications, circulars, press releases, state GST releases, ICAI materials and high court / ITAT rulings — within minutes of publication. Our retrieval pipeline is timestamped per source, so every answer shows you exactly how fresh the underlying material is." },
    { q: "Does Compliso replace our CA?", a: "No — and that is the point. Compliso handles the reading, the reconciliation, the deadline tracking and the first-draft replies. Your CA does the strategy, the client relationship, the judgement call. Think of it as the most diligent junior associate your practice has ever had." },
    { q: "Which portals and tools does it integrate with?", a: "GSTN (GSTR-1/3B/9, 2A/2B), Income Tax e-filing (TDS, ITR, AIS), MCA21, ICEGATE, e-Way Bill, E-Invoice IRP, plus read-only sync with Tally Prime, Zoho Books, Busy, Vyapar, SAP Business One, and QuickBooks." },
    { q: "How is client data handled? Is it secure?", a: "All data stays in AWS Mumbai (ap-south-1). Encryption at rest (AES-256) and in transit (TLS 1.3). SOC 2 Type II audited. We never train our base models on your data — your filings, your prompts, your clients are isolated." },
    { q: "Is there a CA-only or firm-only plan?", a: "Yes — the Practice plan is built for firms handling 5–25 clients. If you are a single CA with 50+ clients or run a multi-branch firm, the Firm plan covers unlimited client workspaces, SSO and a named CSM." },
    { q: "Can I cancel anytime?", a: "Yes — month-to-month, no minimum commitment. 30-day money-back on the first invoice, no questions asked. Your data exports cleanly (JSON / Excel / PDF) — we do not hold it hostage." },
  ];
  const [open, setOpen] = useState(0);
  return (
    <section id="faq" className="relative bg-navy-900 border-t border-white/[0.05]">
      <div className="max-w-[1080px] mx-auto px-5 md:px-8 py-24 md:py-32">
        <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.6 }} className="max-w-2xl">
          <div className="inline-flex items-center gap-2 text-[11.5px] uppercase tracking-[0.18em] text-accent-400 font-medium">
            <span className="w-6 h-px bg-accent-400/60" /> Frequently asked
          </div>
          <h2 className="mt-5 text-[36px] md:text-[48px] leading-[1.04] tracking-tight font-semibold text-ink-50">
            The questions every CA asks before signing up.
          </h2>
        </motion.div>
        <div className="mt-12 divide-y divide-white/[0.06] border-t border-white/[0.06]">
          {data.map((it, i) => (
            <FAQItem key={i} item={it} open={open === i} onToggle={() => setOpen(open === i ? -1 : i)} />
          ))}
        </div>
        <div className="mt-12 flex flex-wrap items-center gap-3 text-[13.5px] text-ink-200/70">
          <span>Still wondering?</span>
          <a href="#" className="inline-flex items-center gap-1.5 text-ink-50 hover:text-accent-400 transition-colors font-medium">
            Talk to a human &middot; hello@compliso.app
          </a>
        </div>
      </div>
    </section>
  );
}
