import { Mail } from "lucide-react";

function IconLinkedin({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="3"/>
      <path d="M8 10v7"/><circle cx="8" cy="7" r="1.2"/><path d="M12 17v-4a2 2 0 0 1 4 0v4"/><path d="M12 10v7"/>
    </svg>
  );
}

function IconTwitter({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 4h3l-7.5 8.5L22 21h-6l-5-6-5 6H3l8-9-8-8h6l4.5 5.5L18 4z"/>
    </svg>
  );
}

export function Footer() {
  const cols = [
    { title: "Product", links: ["RAG-grounded Q&A", "Live rule tracking", "ITC reconciliation", "Notice decoder", "Deadline radar", "Integrations"] },
    { title: "Solutions", links: ["CA firms", "MSME founders", "CFO offices", "Multi-state businesses", "E-commerce sellers"] },
    { title: "Resources", links: ["GST circular index", "TDS rate card", "Notice playbook", "Changelog", "API docs", "Status"] },
    { title: "Company", links: ["About", "Customers", "Careers (hiring)", "Press", "Contact"] },
  ];
  return (
    <footer className="bg-navy-950 border-t border-white/[0.06]">
      <div className="max-w-[1280px] mx-auto px-5 md:px-8 py-16 md:py-20">
        <div className="grid lg:grid-cols-[1.3fr_repeat(4,1fr)] gap-10 lg:gap-12">
          <div>
            <div className="flex items-center gap-2.5">
              <svg className="w-8 h-8" viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="8" fill="#0F1A33" stroke="rgba(255,255,255,0.08)"/><path d="M22.5 11.5a6.5 6.5 0 1 0 0 9" stroke="#34D399" strokeWidth="2.4" strokeLinecap="round"/><circle cx="23.5" cy="16" r="1.7" fill="#34D399"/></svg>
              <span className="text-[18px] font-semibold tracking-tight text-ink-50">Compliso</span>
            </div>
            <p className="mt-5 text-[14px] text-ink-200/65 leading-relaxed max-w-xs">
              The AI compliance layer for Indian MSMEs and CA firms. Built in Bengaluru. Indexed in Mumbai. Trusted in 14 cities.
            </p>
            <div className="mt-6 flex items-center gap-3">
              <a href="#" className="w-9 h-9 rounded-full bg-white/[0.03] border border-white/[0.06] grid place-items-center text-ink-200/70 hover:text-ink-50 hover:border-white/15 hover:-translate-y-0.5 transition-all" aria-label="LinkedIn"><IconLinkedin className="w-4 h-4" /></a>
              <a href="#" className="w-9 h-9 rounded-full bg-white/[0.03] border border-white/[0.06] grid place-items-center text-ink-200/70 hover:text-ink-50 hover:border-white/15 hover:-translate-y-0.5 transition-all" aria-label="Twitter"><IconTwitter className="w-4 h-4" /></a>
              <a href="#" className="w-9 h-9 rounded-full bg-white/[0.03] border border-white/[0.06] grid place-items-center text-ink-200/70 hover:text-ink-50 hover:border-white/15 hover:-translate-y-0.5 transition-all" aria-label="Email"><Mail className="w-4 h-4" /></a>
            </div>
          </div>
          {cols.map((c, i) => (
            <div key={i}>
              <div className="text-[12px] uppercase tracking-[0.18em] text-ink-300/55 font-medium">{c.title}</div>
              <ul className="mt-5 space-y-3">
                {c.links.map((l) => (
                  <li key={l}><a href="#" className="text-[13.5px] text-ink-200/75 hover:text-ink-50 transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-14 pt-7 border-t border-white/[0.06] flex flex-wrap items-center gap-4 justify-between">
          <div className="text-[12.5px] text-ink-300/55">&copy; 2026 Compliso Technologies Pvt Ltd</div>
          <div className="flex items-center gap-5 text-[12.5px] text-ink-300/55">
            <a href="#" className="hover:text-ink-100 transition-colors">Privacy</a>
            <a href="#" className="hover:text-ink-100 transition-colors">Terms</a>
            <a href="#" className="hover:text-ink-100 transition-colors">DPA</a>
            <a href="#" className="hover:text-ink-100 transition-colors">Security</a>
            <span className="inline-flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-accent-500 animate-pulse" /> All systems normal</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
