import { Nav } from "@/components/landing/Nav";
import { Hero } from "@/components/landing/Hero";
import { TrustBar } from "@/components/landing/TrustBar";
import { ProblemSolution } from "@/components/landing/ProblemSolution";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Pricing } from "@/components/landing/Pricing";
import { Testimonials } from "@/components/landing/Testimonials";
import { FAQ } from "@/components/landing/FAQ";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { Footer } from "@/components/landing/Footer";

export function LandingPage() {
  return (
    <div className="bg-navy-900 text-ink-100 min-h-screen antialiased">
      <Nav />
      <main>
        <Hero />
        <TrustBar />
        <ProblemSolution />
        <Features />
        <HowItWorks />
        <Pricing />
        <Testimonials />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}
