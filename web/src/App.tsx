import { useState, useEffect, useRef } from "react";
import { LandingPage } from "@/pages/LandingPage";
import { useChat } from "@/hooks/useChat";
import { ChatMessage, StreamingIndicator } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { QuickPrompts } from "@/components/chat/QuickPrompts";
import { Sidebar } from "@/components/layout/Sidebar";

function ChatPage() {
  const {
    messages,
    isStreaming,
    currentAnswer,
    currentThoughts,
    error,
    sendMessage,
    clearChat,
  } = useChat();

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, currentAnswer]);

  const hasMessages = messages.length > 0 || isStreaming;

  return (
    <div className="flex h-screen bg-navy-950">
      <Sidebar messages={messages} onNewChat={clearChat} />
      <div className="flex-1 flex flex-col">
        <header className="h-14 border-b border-navy-700 bg-navy-900/80 backdrop-blur-sm flex items-center px-4">
          <a href="#" className="text-sm font-medium text-ink-50 hover:text-accent-400 transition-colors">Compliso.ai</a>
          <span className="text-xs text-ink-400 ml-2">
            GST & MSME Compliance Copilot
          </span>
        </header>
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          {!hasMessages ? (
            <QuickPrompts onSelect={sendMessage} />
          ) : (
            <div className="py-4">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              {isStreaming && (
                <>
                  {currentAnswer ? (
                    <ChatMessage
                      isStreaming
                      streamingContent={currentAnswer}
                      thoughts={currentThoughts}
                    />
                  ) : (
                    <StreamingIndicator />
                  )}
                </>
              )}
              {error && (
                <div className="px-4 py-2">
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-sm text-red-400">
                    {error}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        <ChatInput onSend={sendMessage} disabled={isStreaming} />
      </div>
    </div>
  );
}

function App() {
  const [hash, setHash] = useState(window.location.hash);

  useEffect(() => {
    const onHashChange = () => setHash(window.location.hash);
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  if (hash === "#chat") return <ChatPage />;
  return <LandingPage />;
}

export default App;
