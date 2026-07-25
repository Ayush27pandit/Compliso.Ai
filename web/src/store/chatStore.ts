import { create } from "zustand";
import type { Message } from "@/types";

interface ChatStore {
  messages: Message[];
  isStreaming: boolean;
  currentAnswer: string;
  currentThoughts: string[];
  currentSources: string[];
  currentIntent: string;
  error: string | null;
  threadId: string;

  addUserMessage: (content: string) => void;
  setStreaming: (isStreaming: boolean) => void;
  setCurrentAnswer: (answer: string) => void;
  appendToAnswer: (chunk: string) => void;
  addThought: (thought: string) => void;
  setSources: (sources: string[]) => void;
  setIntent: (intent: string) => void;
  setError: (error: string | null) => void;
  finalizeAssistantMessage: () => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  isStreaming: false,
  currentAnswer: "",
  currentThoughts: [],
  currentSources: [],
  currentIntent: "",
  error: null,
  threadId: crypto.randomUUID(),

  addUserMessage: (content: string) => {
    const message: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: Date.now(),
    };
    set((state) => ({ messages: [...state.messages, message] }));
  },

  setStreaming: (isStreaming: boolean) => set({ isStreaming }),

  setCurrentAnswer: (answer: string) => set({ currentAnswer: answer }),

  appendToAnswer: (chunk: string) =>
    set((state) => ({ currentAnswer: state.currentAnswer + chunk })),

  addThought: (thought: string) =>
    set((state) => ({ currentThoughts: [...state.currentThoughts, thought] })),

  setSources: (sources: string[]) => set({ currentSources: sources }),

  setIntent: (intent: string) => set({ currentIntent: intent }),

  setError: (error: string | null) => set({ error }),

  finalizeAssistantMessage: () => {
    const state = get();
    if (!state.currentAnswer) return;

    const message: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: state.currentAnswer,
      sources: state.currentSources,
      intent: state.currentIntent,
      thoughtProcess: state.currentThoughts,
      timestamp: Date.now(),
    };

    set((s) => ({
      messages: [...s.messages, message],
      currentAnswer: "",
      currentThoughts: [],
      currentSources: [],
      currentIntent: "",
      isStreaming: false,
    }));
  },

  clearChat: () =>
    set({
      messages: [],
      isStreaming: false,
      currentAnswer: "",
      currentThoughts: [],
      currentSources: [],
      currentIntent: "",
      error: null,
      threadId: crypto.randomUUID(),
    }),
}));
