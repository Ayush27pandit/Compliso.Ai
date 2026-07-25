import { cn } from "@/lib/utils";
import { Bot, User, Loader2 } from "lucide-react";
import type { Message } from "@/types";

interface ChatMessageProps {
  message?: Message;
  isStreaming?: boolean;
  streamingContent?: string;
  thoughts?: string[];
  sources?: string[];
}

export function ChatMessage({
  message,
  isStreaming,
  streamingContent,
  thoughts,
  sources,
}: ChatMessageProps) {
  const isUser = message?.role === "user";
  const content = isUser ? message?.content : streamingContent || message?.content;

  return (
    <div
      className={cn(
        "flex gap-3 px-4 py-6",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-500/20 flex items-center justify-center">
          <Bot className="w-4 h-4 text-accent-400" />
        </div>
      )}

      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3",
          isUser
            ? "bg-accent-500 text-white"
            : "bg-navy-800 text-ink-50 border border-navy-700"
        )}
      >
        {/* Thought process */}
        {!isUser && thoughts && thoughts.length > 0 && (
          <div className="mb-3 pb-3 border-b border-navy-700">
            <div className="text-xs text-ink-300 mb-1">Thinking...</div>
            {thoughts.map((thought, i) => (
              <div
                key={i}
                className="text-xs text-ink-400 flex items-center gap-1.5"
              >
                <span className="text-accent-400">▸</span>
                {thought}
              </div>
            ))}
          </div>
        )}

        {/* Message content */}
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {content}
          {isStreaming && (
            <span className="inline-block w-2 h-4 ml-0.5 bg-accent-400 animate-pulse" />
          )}
        </div>

        {/* Sources */}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-navy-700">
            <div className="text-xs text-ink-300 mb-2">Sources</div>
            <div className="flex flex-wrap gap-2">
              {sources.map((source, i) => (
                <div
                  key={i}
                  className="text-xs bg-navy-700/50 text-ink-200 px-2 py-1 rounded-md max-w-[200px] truncate"
                  title={source}
                >
                  {source.substring(0, 60)}
                  {source.length > 60 ? "..." : ""}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-navy-700 flex items-center justify-center">
          <User className="w-4 h-4 text-ink-300" />
        </div>
      )}
    </div>
  );
}

export function StreamingIndicator() {
  return (
    <div className="flex gap-3 px-4 py-6">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-500/20 flex items-center justify-center">
        <Loader2 className="w-4 h-4 text-accent-400 animate-spin" />
      </div>
      <div className="bg-navy-800 border border-navy-700 rounded-2xl px-4 py-3">
        <div className="flex items-center gap-2 text-sm text-ink-300">
          <span className="animate-pulse">Researching</span>
          <span className="flex gap-1">
            <span className="w-1.5 h-1.5 bg-accent-400 rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-1.5 h-1.5 bg-accent-400 rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-1.5 h-1.5 bg-accent-400 rounded-full animate-bounce [animation-delay:300ms]" />
          </span>
        </div>
      </div>
    </div>
  );
}
