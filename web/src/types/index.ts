export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  intent?: string;
  thoughtProcess?: string[];
  timestamp: number;
}

export interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  currentAnswer: string;
  currentThoughts: string[];
  currentSources: string[];
  currentIntent: string;
  error: string | null;
  threadId: string;
}

export interface StreamEvent {
  type: "status" | "thought" | "answer_chunk" | "sources" | "intent" | "done" | "error";
  content: string | string[];
}
