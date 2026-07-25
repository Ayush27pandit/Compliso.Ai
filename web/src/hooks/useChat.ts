import { useCallback } from "react";
import { useChatStore } from "@/store/chatStore";
import type { StreamEvent } from "@/types";

const API_URL = import.meta.env.VITE_API_URL || "";

export function useChat() {
  const store = useChatStore();

  const sendMessage = useCallback(
    async (content: string) => {
      // Add user message
      store.addUserMessage(content);
      store.setStreaming(true);
      store.setError(null);
      store.setCurrentAnswer("");
      store.setSources([]);
      store.setIntent("");
      store.addThought("Analyzing query...");

      try {
        const response = await fetch(`${API_URL}/query/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            q: content,
            thread_id: store.threadId,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("No response body");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;

            try {
              const event: StreamEvent = JSON.parse(line.slice(6));

              switch (event.type) {
                case "status":
                  // Update last thought
                  break;

                case "thought":
                  store.addThought(event.content as string);
                  break;

                case "answer_chunk":
                  store.appendToAnswer(event.content as string);
                  break;

                case "sources":
                  store.setSources(event.content as string[]);
                  break;

                case "intent":
                  store.setIntent(event.content as string);
                  break;

                case "error":
                  store.setError(event.content as string);
                  break;

                case "done":
                  break;
              }
            } catch {
              // Skip malformed JSON lines
            }
          }
        }

        // Remove "Analyzing query..." if it's the only thought
        const state = useChatStore.getState();
        if (
          state.currentThoughts.length === 1 &&
          state.currentThoughts[0] === "Analyzing query..."
        ) {
          store.addThought(""); // will be filtered out
        }

        store.finalizeAssistantMessage();
      } catch (error) {
        store.setError(
          error instanceof Error ? error.message : "Failed to connect to backend"
        );
        store.setStreaming(false);
      }
    },
    [store]
  );

  return {
    sendMessage,
    messages: store.messages,
    isStreaming: store.isStreaming,
    currentAnswer: store.currentAnswer,
    currentThoughts: store.currentThoughts,
    error: store.error,
    clearChat: store.clearChat,
  };
}
