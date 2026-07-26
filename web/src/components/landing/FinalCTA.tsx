import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

export function FinalCTA() {
  return (
    <section className="relative bg-navy-950 overflow-hidden">
      <div className="absolute inset-0 dot-grid opacity-50" />
      <div className="absolute inset-0 bg-gradient-to-b from-navy-950 via-transparent to-navy-950" />
      <div className="relative max-w-[1280px] mx-auto px-5 md:px-8 py-24 md:py-36">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="text-center max-w-3xl mx-auto"
        >
          <h2 className="text-[40px] md:text-[56px] leading-[1.02] tracking-tight font-semibold text-ink-50">
            Stop reading circulars.{" "}
            <span className="text-gradient-emerald">
              Start asking questions.
            </span>
          </h2>
          <p className="mt-6 text-[16px] md:text-[18px] text-ink-200/65 leading-relaxed max-w-xl mx-auto">
            Join 47+ CA firms who replaced their compliance research workflow with a single query.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="#chat"
              className="group inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-accent-500 hover:bg-accent-600 text-navy-950 text-[15px] font-medium transition-all duration-200 btn-shimmer"
            >
              Try Compliso Free
              <ArrowRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-0.5" />
            </a>
            <a
              href="#problem"
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl border border-white/10 bg-white/[0.03] hover:bg-white/[0.06] text-ink-100 text-[15px] font-medium transition-all duration-200"
            >
              See the problem
            </a>
          </div>
          <p className="mt-6 text-[12.5px] text-ink-300/40">
            No credit card required &middot; Free forever for solo CAs
          </p>
        </motion.div>
      </div>
    </section>
  );
}
