import { Scale, FileText, Calendar, Shield, Receipt, Landmark } from "lucide-react";

interface QuickPromptsProps {
  onSelect: (prompt: string) => void;
}

const PROMPTS = [
  {
    icon: Scale,
    text: "What is the GST composition scheme turnover limit?",
  },
  {
    icon: FileText,
    text: "How do I register for Udyam?",
  },
  {
    icon: Calendar,
    text: "What are the GST return filing due dates?",
  },
  {
    icon: Shield,
    text: "What protection does MSMED Act offer for delayed payments?",
  },
  {
    icon: Receipt,
    text: "What are the current GST rate slabs?",
  },
  {
    icon: Landmark,
    text: "Is ITC available on rent for commercial property?",
  },
];

export function QuickPrompts({ onSelect }: QuickPromptsProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4">
      <div className="text-center mb-10">
        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-accent-500/20 flex items-center justify-center">
          <Scale className="w-8 h-8 text-accent-400" />
        </div>
        <h1 className="text-2xl font-semibold text-ink-50 mb-2">
          Compliso.ai
        </h1>
        <p className="text-sm text-ink-300">
          Your AI compliance copilot for Indian GST & MSME law
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
        {PROMPTS.map((prompt, i) => (
          <button
            key={i}
            onClick={() => onSelect(prompt.text)}
            className="flex items-start gap-3 p-4 rounded-xl bg-navy-800 border border-navy-700 hover:border-accent-500/50 hover:bg-navy-750 transition-all text-left group"
          >
            <prompt.icon className="w-5 h-5 text-accent-400 flex-shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
            <span className="text-sm text-ink-200 group-hover:text-ink-50 transition-colors">
              {prompt.text}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
