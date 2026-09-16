export interface ThoughtStep {
  id?: string;
  step_id: number;
  agent: string;
  action?: string;
  label: string;
  status: "pending" | "running" | "completed" | "error";
  summary?: string;
  data?: any;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string; // ISO string representation
  model?: ModelOption;
  source?: string;
  thoughtSteps?: ThoughtStep[];
  isStreaming?: boolean;
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
