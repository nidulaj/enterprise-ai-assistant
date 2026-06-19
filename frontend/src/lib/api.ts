import axios from "axios";

// Create Axios instance using environment variable or fallback to backend default port
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000",
  headers: {
    "Content-Type": "application/json",
  },
});

interface ChatRequest {
  message: string;
}

interface ChatResponse {
  response: string;
}

/**
 * Sends a message to the backend assistant endpoint.
 * @param message The user's input text
 * @returns The response text from the assistant
 */
export const sendChatMessage = async (message: string): Promise<string> => {
  const response = await api.post<ChatResponse>("/chat", { message } as ChatRequest);
  return response.data.response;
};

export default api;
