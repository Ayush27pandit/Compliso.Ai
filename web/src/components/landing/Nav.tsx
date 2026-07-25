import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, ArrowRight } from "lucide-react";

const cls = (...x: (string | boolean | undefined | null)[]) => x.filter(Boolean).join(" ");

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const links = [
    { label: "Product", href: "#features" },
    { label: "How it works", href: "#how" },
    { label: "Pricing", href: "#pricing" },
    { label: "Customers", href: "#testimonials" },
    { label: "FAQ", href: "#faq" },
  ];

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className={cls(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled
          ? "backdrop-blur-xl bg-navy-900/80 border-b border-white/[0.06] shadow-lg"
          : "bg-transparent"
      )}
    >
      <div className="max-w-[1280px] mx-auto px-5 md:px-8 h-16 md:h-[72px] flex items-center justify-between">
        <a href="#" className="flex items-center gap-2.5">
          <svg className="w-8 h-8" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="#0F1A33" stroke="rgba(255,255,255,0.08)"/>
            <path d="M22.5 11.5a6.5 6.5 0 1 0 0 9" stroke="#34D399" strokeWidth="2.4" strokeLinecap="round"/>
            <circle cx="23.5" cy="16" r="1.7" fill="#34D399"/>
          </svg>
          <span className="text-[17px] font-semibold tracking-tight text-ink-50">Compliso</span>
        </a>

        <nav className="hidden lg:flex items-center gap-8">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="nav-link text-[14px] font-medium text-ink-200/80 hover:text-ink-50 transition-colors">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="hidden lg:flex items-center gap-3">
          <a href="#" className="text-[14px] font-medium text-ink-200/80 hover:text-ink-50 transition-colors">Sign in</a>
          <a href="#chat" className="group inline-flex items-center gap-1.5 h-9 px-4 rounded-full bg-ink-50 text-navy-900 text-[13.5px] font-semibold tracking-tight hover:shadow-lg transition-all duration-300 hover:-translate-y-px">
            Start free trial
            <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
          </a>
        </div>

        <button onClick={() => setOpen(!open)} className="lg:hidden p-2 text-ink-100" aria-label="Menu">
          {open ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="lg:hidden overflow-hidden bg-navy-900/95 backdrop-blur-xl border-t border-white/[0.06]"
          >
            <div className="px-5 py-5 flex flex-col gap-3">
              {links.map((l) => (
                <a key={l.href} href={l.href} onClick={() => setOpen(false)} className="text-[15px] font-medium text-ink-200/85 py-2">{l.label}</a>
              ))}
              <a href="#chat" onClick={() => setOpen(false)} className="mt-2 inline-flex justify-center items-center h-11 rounded-full bg-ink-50 text-navy-900 font-semibold">
                Start free trial
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
