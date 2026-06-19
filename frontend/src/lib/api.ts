import axios from "axios";
import { ModelOption } from "@/types/chat";

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
  response: string;
  model: ModelOption;
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

export default api;
