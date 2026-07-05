export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string; // ISO string representation
  model?: ModelOption;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: string;
  messages: Message[];
}

export type ModelOption = "auto" | "gemini" | "groq";

export interface DocumentItem {
  id: string;
  name: string;
  file_url: string;
  uploaded_at: string;
}
