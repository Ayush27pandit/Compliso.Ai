import { Scale, Plus, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Message } from "@/types";

interface SidebarProps {
  messages: Message[];
  onNewChat: () => void;
}

const TOPICS = [
  "GST Registration",
  "GST Rate Slabs",
  "GST Returns & Due Dates",
  "GST Composition Scheme",
  "Udyam Registration",
  "MSME Payment Protection",
];

export function Sidebar({ messages, onNewChat }: SidebarProps) {
  const userMessages = messages.filter((m) => m.role === "user");

  return (
    <div className="w-64 h-full bg-navy-900 border-r border-navy-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-navy-700">
        <div className="flex items-center gap-2 mb-1">
          <Scale className="w-5 h-5 text-accent-400" />
          <span className="font-semibold text-ink-50">Compliso</span>
        </div>
        <p className="text-xs text-ink-400">GST & MSME Compliance</p>
      </div>

      {/* New Chat */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className={cn(
            "w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm",
            "bg-navy-800 border border-navy-700 text-ink-200",
            "hover:border-accent-500/50 hover:text-ink-50 transition-all"
          )}
        >
          <Plus className="w-4 h-4" />
          New Conversation
        </button>
      </div>

      {/* Topics */}
      <div className="px-3 py-2">
        <p className="text-xs text-ink-400 uppercase tracking-wider mb-2 px-1">
          Topics
        </p>
        <div className="space-y-1">
          {TOPICS.map((topic, i) => (
            <div
              key={i}
              className="text-xs text-ink-300 px-2 py-1.5 rounded-md hover:bg-navy-800 transition-colors"
            >
              {topic}
            </div>
          ))}
        </div>
      </div>

      {/* History */}
      {userMessages.length > 0 && (
        <div className="px-3 py-2 flex-1 overflow-y-auto">
          <p className="text-xs text-ink-400 uppercase tracking-wider mb-2 px-1">
            History
          </p>
          <div className="space-y-1">
            {userMessages.map((msg) => (
              <div
                key={msg.id}
                className="text-xs text-ink-300 px-2 py-1.5 rounded-md hover:bg-navy-800 transition-colors truncate flex items-center gap-2"
              >
                <MessageSquare className="w-3 h-3 flex-shrink-0" />
                {msg.content.substring(0, 30)}
                {msg.content.length > 30 ? "..." : ""}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="p-3 border-t border-navy-700 mt-auto">
        <p className="text-[10px] text-ink-400 leading-relaxed">
          ⚠️ Informational guidance only. Verify against official portals or a
          qualified CA.
        </p>
      </div>
    </div>
  );
}
