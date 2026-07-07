import axios from "axios";
import { ModelOption, DocumentItem } from "@/types/chat";

// Create Axios instance using environment variable or fallback to backend default port
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000",
  headers: {
    "Content-Type": "application/json",
  },
});

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
 * Sends a message to the backend assistant endpoint.
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
