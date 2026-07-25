import { useRef, useEffect, useState } from "react";
import { motion, useInView } from "framer-motion";

function CountUp({ to, duration = 1800, prefix = "", suffix = "", decimals = 0 }: {
  to: number; duration?: number; prefix?: string; suffix?: string; decimals?: number;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    const startTs = performance.now();
    let raf: number;
    const step = (ts: number) => {
      const p = Math.min((ts - startTs) / duration, 1);
      setVal(to * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [inView, to, duration]);
  const formatted = val.toLocaleString("en-IN", { maximumFractionDigits: decimals, minimumFractionDigits: decimals });
  return <span ref={ref}>{prefix}{formatted}{suffix}</span>;
}

export function TrustBar() {
  const stats = [
    { value: 10000, prefix: "", suffix: "+", label: "GST filings monitored every month" },
    { value: 420, prefix: "\u20B9", suffix: " Cr+", label: "in client turnover under compliance" },
    { value: 99.2, prefix: "", suffix: "%", label: "notice-prevention accuracy", decimals: 1 },
    { value: 47, prefix: "", suffix: "", label: "CA firms onboard in the last quarter" },
  ];
  const names = ["Mehra & Associates", "Iyer Tax Advisors", "KPMG India", "Kapoor Logistics", "BluePencil CA", "Sarda & Co.", "Northwind Traders", "Finsight Partners", "Aurora MSME House", "CharterLane"];

  return (
    <section className="relative bg-navy-900 border-y border-white/[0.05]">
      <div className="max-w-[1280px] mx-auto px-5 md:px-8 py-14 md:py-20">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-y-10 gap-x-6">
          {stats.map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-50px" }} transition={{ delay: i * 0.08, duration: 0.55, ease: [0.22, 1, 0.36, 1] }} className="relative md:px-2">
              {i !== 0 && <div className="hidden md:block absolute -left-3 top-1 bottom-1 w-px bg-white/[0.07]" />}
              <div className="text-[40px] md:text-[52px] leading-none tracking-tight font-semibold text-ink-50">
                <CountUp to={s.value} prefix={s.prefix} suffix={s.suffix} decimals={(s as any).decimals || 0} />
              </div>
              <div className="mt-3 text-[13px] md:text-[13.5px] text-ink-200/65 leading-snug max-w-[220px]">{s.label}</div>
            </motion.div>
          ))}
        </div>
        <div className="mt-14 md:mt-20 flex flex-wrap items-center gap-x-10 gap-y-6 justify-center md:justify-between">
          <div className="text-[11.5px] uppercase tracking-[0.2em] text-ink-300/45 font-medium">Trusted by practices across India</div>
          <div className="marquee-mask flex-1 min-w-0 overflow-hidden">
            <div className="flex items-center gap-12 md:gap-16 animate-marquee whitespace-nowrap will-change-transform">
              {[...names, ...names].map((n, i) => (
                <div key={i} className="text-[15.5px] text-ink-200/45 font-serif italic font-normal">{n}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
