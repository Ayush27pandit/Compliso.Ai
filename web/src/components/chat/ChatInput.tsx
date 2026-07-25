import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        160
      )}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-navy-700 bg-navy-900/80 backdrop-blur-sm p-4">
      <div className="max-w-3xl mx-auto">
        <div className="relative flex items-end gap-2 bg-navy-800 border border-navy-600 rounded-2xl px-4 py-3 focus-within:border-accent-500/50 transition-colors">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about GST, MSME, Udyam registration..."
            disabled={disabled}
            rows={1}
            className={cn(
              "flex-1 bg-transparent text-sm text-ink-50 placeholder:text-ink-400",
              "outline-none resize-none max-h-40",
              "disabled:opacity-50"
            )}
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || disabled}
            className={cn(
              "flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center transition-all",
              input.trim() && !disabled
                ? "bg-accent-500 hover:bg-accent-600 text-white"
                : "bg-navy-700 text-ink-400 cursor-not-allowed"
            )}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[11px] text-ink-400 text-center mt-2">
          Compliso provides informational guidance only. Verify against{" "}
          <a
            href="https://gst.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="text-accent-400 hover:underline"
          >
            gst.gov.in
          </a>{" "}
          or a qualified CA.
        </p>
      </div>
    </div>
  );
}
