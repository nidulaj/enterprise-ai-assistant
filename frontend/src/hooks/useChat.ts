import { useState, useEffect } from "react";
import { Message, ChatSession, ModelOption } from "@/types/chat";
import { sendChatMessage } from "@/lib/api";

const LOCAL_STORAGE_KEY = "enterprise_ai_sessions";
const MODEL_STORAGE_KEY = "enterprise_ai_model";

// Mock initial chat history for a premium user experience
const MOCK_SESSIONS: ChatSession[] = [
  {
    id: "session-1",
    title: "AI Integration Strategy",
    createdAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    messages: [
      {
        id: "msg-1-1",
        role: "user",
        content: "What are the key pillars of a successful enterprise AI strategy?",
        timestamp: new Date(Date.now() - 3600000 * 2).toISOString(),
      },
      {
        id: "msg-1-2",
        role: "assistant",
        content: "A successful enterprise AI strategy relies on four core pillars:\n\n1. **Data Infrastructure**: Ensuring clean, accessible, and secure data pipeline architectures.\n2. **Governance & Trust**: Establishing ethical frameworks, compliance checks, and model explainability.\n3. **Use Case Alignment**: Targeting high-value, measurable problems rather than adopting AI for its own sake.\n4. **Talent & Enablement**: Training existing staff and hiring specialists to maintain and iterate on AI systems.",
        timestamp: new Date(Date.now() - 3600000 * 2 + 1000).toISOString(),
      },
    ],
  },
  {
    id: "session-2",
    title: "Next.js App Router Optimization",
    createdAt: new Date(Date.now() - 3600000 * 24).toISOString(),
    messages: [
      {
        id: "msg-2-1",
        role: "user",
        content: "How do I optimize dynamic routes in Next.js using generateStaticParams?",
        timestamp: new Date(Date.now() - 3600000 * 24).toISOString(),
      },
      {
        id: "msg-2-2",
        role: "assistant",
        content: "To optimize dynamic routes with `generateStaticParams`, you can pre-render page paths at build time instead of on-demand. This transforms dynamic routes into static pages, significantly improving Response times and caching behavior on CDNs.",
        timestamp: new Date(Date.now() - 3600000 * 24 + 2000).toISOString(),
      },
    ],
  },
];

export const useChat = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<ModelOption>("auto");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize chat sessions and model preference
  useEffect(() => {
    const savedSessions = localStorage.getItem(LOCAL_STORAGE_KEY);
    const savedModel = localStorage.getItem(MODEL_STORAGE_KEY) as ModelOption;

    if (savedModel) {
      setSelectedModel(savedModel);
    }

    if (savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions);
        if (parsed && parsed.length > 0) {
          setSessions(parsed);
          setCurrentSessionId(parsed[0].id);
          return;
        }
      } catch (e) {
        console.error("Failed to parse saved sessions", e);
      }
    }

    // Default initializer if no history exists
    setSessions(MOCK_SESSIONS);
    setCurrentSessionId(MOCK_SESSIONS[0].id);
  }, []);

  // Save sessions to localStorage when they change
  const saveSessions = (updatedSessions: ChatSession[]) => {
    setSessions(updatedSessions);
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(updatedSessions));
  };

  // Change model selection
  const changeModel = (model: ModelOption) => {
    setSelectedModel(model);
    localStorage.setItem(MODEL_STORAGE_KEY, model);
  };

  // Get current active session messages
  const currentSession = sessions.find((s) => s.id === currentSessionId);
  const messages = currentSession ? currentSession.messages : [];

  // Start a brand new empty chat session
  const startNewChat = () => {
    const newSession: ChatSession = {
      id: `session-${Date.now()}`,
      title: "New Chat",
      createdAt: new Date().toISOString(),
      messages: [],
    };
    const updated = [newSession, ...sessions];
    saveSessions(updated);
    setCurrentSessionId(newSession.id);
    setError(null);
  };

  // Select a specific chat session
  const selectSession = (id: string) => {
    setCurrentSessionId(id);
    setError(null);
  };

  // Delete a specific session
  const deleteSession = (id: string, event: React.MouseEvent) => {
    event.stopPropagation();
    const updated = sessions.filter((s) => s.id !== id);
    saveSessions(updated);

    if (currentSessionId === id) {
      if (updated.length > 0) {
        setCurrentSessionId(updated[0].id);
      } else {
        // If no sessions remain, create a clean one
        const fallbackSession: ChatSession = {
          id: `session-${Date.now()}`,
          title: "New Chat",
          createdAt: new Date().toISOString(),
          messages: [],
        };
        saveSessions([fallbackSession]);
        setCurrentSessionId(fallbackSession.id);
      }
    }
  };

  // Send a message to the active session
  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    // Update session state with the user message
    let activeSession = sessions.find((s) => s.id === currentSessionId);
    if (!activeSession) {
      // Create a fallback session if one doesn't exist
      activeSession = {
        id: currentSessionId || `session-${Date.now()}`,
        title: "New Chat",
        createdAt: new Date().toISOString(),
        messages: [],
      };
    }

    const updatedMessages = [...activeSession.messages, userMessage];
    
    // Auto-update the session title on the first message
    let title = activeSession.title;
    if (activeSession.messages.length === 0) {
      // Use the first 25 characters of the user's message as the title
      title = content.length > 25 ? `${content.substring(0, 25)}...` : content;
    }

    const updatedSession: ChatSession = {
      ...activeSession,
      title,
      messages: updatedMessages,
    };

    const updatedSessions = sessions.map((s) =>
      s.id === activeSession!.id ? updatedSession : s
    );
    
    // Put current session at the top of the history list
    const sortedSessions = [
      updatedSession,
      ...updatedSessions.filter((s) => s.id !== activeSession!.id),
    ];

    saveSessions(sortedSessions);
    setCurrentSessionId(updatedSession.id);
    setIsLoading(true);
    setError(null);

    try {
      const responseData = await sendChatMessage(content, selectedModel);
      
      const assistantMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: "assistant",
        content: responseData.response,
        timestamp: new Date().toISOString(),
        model: responseData.model,
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      const finalSession = {
        ...updatedSession,
        messages: finalMessages,
      };

      const finalSessions = sortedSessions.map((s) =>
        s.id === finalSession.id ? finalSession : s
      );

      saveSessions(finalSessions);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.message || err.message || "Failed to fetch AI response. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return {
    sessions,
    currentSessionId,
    messages,
    selectedModel,
    isLoading,
    error,
    changeModel,
    startNewChat,
    selectSession,
    deleteSession,
    sendMessage,
  };
};
