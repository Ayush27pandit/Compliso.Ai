import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence, useScroll, useTransform } from "framer-motion";
import { Sparkles, ArrowRight, CheckCircle2 } from "lucide-react";

export function Hero() {
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ["start start", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [0, 120]);
  const opacity = useTransform(scrollYProgress, [0, 0.9], [1, 0]);
  const [typeIdx, setTypeIdx] = useState(0);
  const queries = [
    "Is ITC available on festive marketing expenses?",
    "What changed in GSTR-9 for FY 2024-25?",
    "Reconcile my 2A vs 2B for the last quarter.",
    "Decode this DRC-01 notice I just received.",
  ];
  useEffect(() => {
    const t = setInterval(() => setTypeIdx((i) => (i + 1) % queries.length), 3200);
    return () => clearInterval(t);
  }, []);

  return (
    <section ref={heroRef} className="relative min-h-[100svh] flex items-end overflow-hidden">
      <div className="absolute inset-0 z-0">
        <video autoPlay muted loop playsInline preload="auto" className="w-full h-full object-cover scale-105">
          <source src="https://v1.pinimg.com/videos/iht/av1Mp4-control-v2/12/96/98/1296984b461073d0fd1437f012d85ca1_720w.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 hero-overlay" />
        <div className="absolute inset-0 grain" />
      </div>

      <motion.div style={{ y, opacity }} className="relative z-10 w-full max-w-[1280px] mx-auto px-5 md:px-8 pt-40 md:pt-44 pb-20 md:pb-28">
        <div className="max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="inline-flex items-center gap-2.5 px-3 h-8 rounded-full bg-white/[0.04] border border-white/10 text-[12.5px] font-medium text-ink-200 backdrop-blur-md"
          >
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inset-0 rounded-full bg-accent-400 animate-ping opacity-70" />
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-accent-400" />
            </span>
            New &middot; CBIC Notification 04/2026 indexed 2h ago
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.18, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="mt-7 text-[44px] sm:text-[58px] md:text-[76px] lg:text-[88px] leading-[0.96] tracking-tight font-semibold text-ink-50"
          >
            Stay compliant <br className="hidden sm:block" />
            <span className="font-serif italic font-normal text-gradient-emerald pr-1">even when the rules</span>{" "}
            <br className="hidden md:block" />
            change mid&#8209;quarter.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.32, duration: 0.6 }}
            className="mt-7 max-w-2xl text-[16.5px] md:text-[18.5px] leading-[1.6] text-ink-200/80"
          >
            Compliso is the AI compliance layer for Indian MSMEs and CA firms — grounded in the latest GST, TDS and Income&nbsp;Tax circulars, trained on the queries your peers actually ask, and ready the moment a new notification drops.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.46, duration: 0.6 }}
            className="mt-9 flex flex-wrap items-center gap-3.5"
          >
            <a href="#chat" className="group relative inline-flex items-center gap-2 h-12 md:h-[52px] px-6 md:px-7 rounded-full bg-accent-500 text-navy-950 text-[14.5px] md:text-[15px] font-semibold tracking-tight shadow-glow-accent animate-pulse-glow hover:bg-accent-400 hover:-translate-y-0.5 transition-all duration-300 overflow-hidden">
              <span className="relative z-10">Start 14&#8209;day free trial</span>
              <ArrowRight className="w-4 h-4 relative z-10 transition-transform group-hover:translate-x-1" />
              <span className="absolute inset-0 btn-shimmer" />
            </a>
            <a href="#how" className="group inline-flex items-center gap-2 h-12 md:h-[52px] px-6 md:px-7 rounded-full bg-white/[0.04] border border-white/10 text-ink-100 text-[14.5px] md:text-[15px] font-semibold hover:bg-white/[0.08] hover:border-white/20 hover:-translate-y-0.5 transition-all duration-300 backdrop-blur-md">
              <span className="w-7 h-7 rounded-full bg-ink-50 text-navy-900 grid place-items-center">
                <svg className="w-3 h-3 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              </span>
              See a 2&#8209;min live demo
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 text-[12.5px] text-ink-200/65"
          >
            <span className="inline-flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-accent-400" /> No credit card</span>
            <span className="inline-flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-accent-400" /> SOC&nbsp;2 Type&nbsp;II</span>
            <span className="inline-flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-accent-400" /> Data stays in India</span>
          </motion.div>
        </div>

        <motion.aside
          initial={{ opacity: 0, x: 30, y: 20 }}
          animate={{ opacity: 1, x: 0, y: 0 }}
          transition={{ delay: 0.55, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="hidden xl:block absolute right-8 bottom-16 w-[420px]"
        >
          <div className="relative rounded-2xl border border-white/10 bg-navy-900/80 backdrop-blur-xl p-5 shadow-card">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-[11px] font-medium text-ink-300/70">
                <span className="w-1.5 h-1.5 rounded-full bg-accent-400" />
                Live &middot; Compliso Co-pilot
              </div>
              <div className="text-[11px] text-ink-300/50 font-mono">v3.2</div>
            </div>
            <div className="mt-4 text-[13.5px] text-ink-300/70">Ask anything &mdash;</div>
            <AnimatePresence mode="wait">
              <motion.div
                key={typeIdx}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.35 }}
                className="mt-1 text-[15px] text-ink-50 font-medium leading-snug caret"
              >
                {queries[typeIdx]}
              </motion.div>
            </AnimatePresence>
            <div className="mt-4 grid grid-cols-3 gap-2">
              {["GST", "TDS", "IT Act"].map((t) => (
                <div key={t} className="text-[11px] text-ink-300/80 text-center py-1.5 rounded-md bg-white/[0.03] border border-white/5">{t}</div>
              ))}
            </div>
            <div className="mt-4 flex items-center gap-2 text-[11.5px] text-ink-300/60">
              <Sparkles className="w-3.5 h-3.5 text-accent-400" />
              Backed by 14,200+ indexed circulars
            </div>
          </div>
        </motion.aside>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.6 }}
        className="absolute bottom-5 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-2"
      >
        <span className="text-[10.5px] uppercase tracking-[0.18em] text-ink-200/55 font-medium">Scroll</span>
        <span className="block w-px h-9 bg-gradient-to-b from-ink-200/40 to-transparent overflow-hidden">
          <span className="block w-px h-3 bg-ink-50 animate-scroll-cue" />
        </span>
      </motion.div>
    </section>
  );
}
