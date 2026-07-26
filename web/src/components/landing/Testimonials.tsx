import { motion } from "framer-motion";
import { Star } from "lucide-react";

const testimonials = [
  {
    name: "Priya Sharma",
    role: "Partner, Sharma & Verma Associates",
    location: "Mumbai",
    quote: "We went from spending 3 hours every Saturday reading circulars to asking Compliso a question and getting the answer in 10 seconds. The GST 2.0 update was seamless — no downtime, no confusion.",
    stars: 5,
  },
  {
    name: "Arjun Mehta",
    role: "Senior CA, Mehta Tax Advisors",
    location: "Delhi",
    quote: "The composition scheme confusion is finally over. Compliso tells us exactly who qualifies, what the rate is, and when the deadline is — all in one answer. Our junior CAs love it.",
    stars: 5,
  },
  {
    name: "Kavitha Raman",
    role: "Director, Raman & Co.",
    location: "Chennai",
    quote: "We had a client asking about Udyam registration for a trading business. Compliso immediately flagged that trading businesses can't register. Saved us from giving wrong advice.",
    stars: 5,
  },
  {
    name: "Rohit Gupta",
    role: "Managing Partner, Gupta Associates",
    location: "Bangalore",
    quote: "The MSME payment protection insights are gold. We caught three overdue payments that Section 43B(h) would have hit us on. Compliso paid for itself in the first month.",
    stars: 5,
  },
];

export function Testimonials() {
  return (
    <section id="testimonials" className="relative bg-navy-900">
      <div className="max-w-[1280px] mx-auto px-5 md:px-8 py-24 md:py-36">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-2xl mx-auto mb-16 md:mb-20"
        >
          <div className="inline-flex items-center gap-2 text-[11.5px] uppercase tracking-[0.18em] text-accent-400 font-medium">
            <span className="w-6 h-px bg-accent-400/60" /> Testimonials
            <span className="w-6 h-px bg-accent-400/60" />
          </div>
          <h2 className="mt-5 text-[36px] md:text-[48px] leading-[1.02] tracking-tight font-semibold text-ink-50">
            Trusted by{" "}
            <span className="font-serif italic font-normal text-ink-200/70">practices across India</span>
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6">
          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{
                delay: i * 0.08,
                duration: 0.55,
                ease: [0.22, 1, 0.36, 1],
              }}
              className="relative p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-navy-950/60 hover:border-white/10 transition-all duration-300"
            >
              <div className="flex items-center gap-0.5 mb-4">
                {Array.from({ length: t.stars }).map((_, j) => (
                  <Star
                    key={j}
                    className="w-4 h-4 fill-accent-400 text-accent-400"
                  />
                ))}
              </div>
              <p className="text-[15px] md:text-[16px] text-ink-100/85 leading-relaxed mb-6 font-serif italic">
                &ldquo;{t.quote}&rdquo;
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-accent-500/15 border border-accent-500/20 grid place-items-center text-[14px] font-semibold text-accent-400">
                  {t.name[0]}
                </div>
                <div>
                  <div className="text-[14px] font-medium text-ink-50">{t.name}</div>
                  <div className="text-[12.5px] text-ink-200/50">
                    {t.role} &middot; {t.location}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
