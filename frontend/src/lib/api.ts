import axios from "axios";
import { ModelOption, DocumentItem, ThoughtStep } from "@/types/chat";

// Create Axios instance using environment variable or fallback to backend default port
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000",
  headers: {
    "Content-Type": "application/json",
  },
});

export interface StreamCallbacks {
  onThinking?: (data: { message: string }) => void;
  onPlanCreated?: (data: { is_multi_step: boolean; steps: ThoughtStep[] }) => void;
  onStepStart?: (data: { step_id: number; agent: string; action?: string; label: string }) => void;
  onStepComplete?: (data: {
    step_id: number;
    agent: string;
    action?: string;
    status: "completed" | "error";
    summary?: string;
    label?: string;
    data?: any;
  }) => void;
  onToken?: (token: string) => void;
  onDone?: (data: {
    source: string;
    response_text: string;
    model: ModelOption;
    steps?: ThoughtStep[];
  }) => void;
  onError?: (error: string) => void;
}

interface ChatRequest {
  message: string;
  model: ModelOption;
}

interface ChatResponse {
  source: string;
  answer:
    | string
    | {
        response: string;
        model: ModelOption;
      };
  model?: ModelOption;
}

/**
 * Sends a message to the backend assistant streaming endpoint using Server-Sent Events (SSE).
 */
export const sendChatMessageStream = async (
  message: string,
  model: ModelOption,
  callbacks: StreamCallbacks
): Promise<void> => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
  const response = await fetch(`${baseUrl}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, model }),
  });

  if (!response.ok) {
    let errorMsg = `Server error: ${response.status} ${response.statusText}`;
    try {
      const errData = await response.json();
      if (errData.error) errorMsg = errData.error;
    } catch (_) {}
    callbacks.onError?.(errorMsg);
    throw new Error(errorMsg);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Failed to get response stream reader.");
  }

  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      let currentEvent = "message";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) {
          currentEvent = "message";
          continue;
        }

        if (trimmed.startsWith("event:")) {
          currentEvent = trimmed.slice(6).trim();
        } else if (trimmed.startsWith("data:")) {
          const rawData = trimmed.slice(5).trim();
          try {
            const data = JSON.parse(rawData);
            switch (currentEvent) {
              case "thinking":
                callbacks.onThinking?.(data);
                break;
              case "plan_created":
                callbacks.onPlanCreated?.(data);
                break;
              case "step_start":
                callbacks.onStepStart?.(data);
                break;
              case "step_complete":
                callbacks.onStepComplete?.(data);
                break;
              case "token":
                if (data.token) {
                  callbacks.onToken?.(data.token);
                }
                break;
              case "done":
                callbacks.onDone?.(data);
                break;
              case "error":
                callbacks.onError?.(data.error || "An unknown stream error occurred.");
                break;
              default:
                break;
            }
          } catch (e) {
            console.warn("Failed to parse SSE JSON data:", rawData, e);
          }
        }
      }
    }
  } catch (err: any) {
    callbacks.onError?.(err.message || "Connection error during stream.");
    throw err;
  }
};

/**
 * Sends a message to the backend assistant endpoint (legacy / fallback non-streaming).
 * @param message The user's input text
 * @param model The selected AI model
 * @returns The response from the assistant, including content and generating model
 */
export const sendChatMessage = async (
  message: string,
  model: ModelOption
): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>("/chat", { message, model });
  return response.data;
};


export const getDocuments = async (): Promise<DocumentItem[]> => {
  const response = await api.get<DocumentItem[]>("/documents");
  return response.data;
};

export const uploadDocument = async (file: File): Promise<{
  message: string;
  document_id: string;
  chunks: number;
  file_url: string;
}> => {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await api.post("/documents/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export default api;
