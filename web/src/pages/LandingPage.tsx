import { Nav } from "@/components/landing/Nav";
import { Hero } from "@/components/landing/Hero";
import { TrustBar } from "@/components/landing/TrustBar";
import { ProblemSolution } from "@/components/landing/ProblemSolution";
import { FAQ } from "@/components/landing/FAQ";
import { Footer } from "@/components/landing/Footer";

export function LandingPage() {
  return (
    <div className="bg-navy-900 text-ink-100 min-h-screen antialiased">
      <Nav />
      <main>
        <Hero />
        <TrustBar />
        <ProblemSolution />
        <FAQ />
      </main>
      <Footer />
    </div>
  );
}
