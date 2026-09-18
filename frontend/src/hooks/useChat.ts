import { useState, useEffect } from "react";
import { Message, ChatSession, ModelOption, DocumentItem } from "@/types/chat";
import { sendChatMessage, sendChatMessageStream, getDocuments, uploadDocument } from "@/lib/api";

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

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (err: any) {
      console.error("Failed to fetch documents:", err);
    }
  };

  const uploadFile = async (file: File) => {
    if (!file) return;
    setIsUploading(true);
    setUploadError(null);
    try {
      await uploadDocument(file);
      await fetchDocuments();
    } catch (err: any) {
      console.error("Upload failed:", err);
      setUploadError(
        err.response?.data?.error || 
        err.message || 
        "Failed to upload document."
      );
    } finally {
      setIsUploading(false);
    }
  };

  // Fetch documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

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

  // Send a message to the active session with real-time SSE streaming
  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    const assistantMsgId = `msg-${Date.now() + 1}`;
    const initialAssistantMessage: Message = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      model: selectedModel,
      source: "ai",
      thoughtSteps: [],
      isStreaming: true,
    };

    let activeSession = sessions.find((s) => s.id === currentSessionId);
    if (!activeSession) {
      activeSession = {
        id: currentSessionId || `session-${Date.now()}`,
        title: "New Chat",
        createdAt: new Date().toISOString(),
        messages: [],
      };
    }

    let title = activeSession.title;
    if (activeSession.messages.length === 0) {
      title = content.length > 25 ? `${content.substring(0, 25)}...` : content;
    }

    const updatedMessages = [...activeSession.messages, userMessage, initialAssistantMessage];
    const updatedSession: ChatSession = {
      ...activeSession,
      title,
      messages: updatedMessages,
    };

    const updatedSessions = [
      updatedSession,
      ...sessions.filter((s) => s.id !== activeSession!.id),
    ];

    setSessions(updatedSessions);
    setCurrentSessionId(updatedSession.id);
    setIsLoading(true);
    setError(null);

    // Track stream state in local variables for smooth accumulation
    let accumulatedContent = "";
    let accumulatedSource = "ai";
    let accumulatedModel = selectedModel;
    let accumulatedSteps: any[] = [];

    const updateCurrentAssistantMessage = (patch: Partial<Message>) => {
      setSessions((prevSessions) =>
        prevSessions.map((session) => {
          if (session.id !== updatedSession.id) return session;
          return {
            ...session,
            messages: session.messages.map((m) => {
              if (m.id !== assistantMsgId) return m;
              return { ...m, ...patch };
            }),
          };
        })
      );
    };

    try {
      await sendChatMessageStream(content, selectedModel, {
        onThinking: () => {
          // Optional thinking pulse
        },
        onPlanCreated: (data) => {
          accumulatedSteps = (data.steps || []).map((s) => ({
            ...s,
            status: s.status || "pending",
          }));
          updateCurrentAssistantMessage({
            thoughtSteps: [...accumulatedSteps],
          });
        },
        onStepStart: (data) => {
          const stepIndex = accumulatedSteps.findIndex((s) => s.step_id === data.step_id);
          if (stepIndex >= 0) {
            accumulatedSteps[stepIndex] = {
              ...accumulatedSteps[stepIndex],
              status: "running",
              label: data.label || accumulatedSteps[stepIndex].label,
            };
          } else {
            accumulatedSteps.push({
              step_id: data.step_id,
              agent: data.agent,
              action: data.action,
              label: data.label,
              status: "running",
            });
          }
          updateCurrentAssistantMessage({
            thoughtSteps: [...accumulatedSteps],
          });
        },
        onStepComplete: (data) => {
          const stepIndex = accumulatedSteps.findIndex((s) => s.step_id === data.step_id);
          if (stepIndex >= 0) {
            accumulatedSteps[stepIndex] = {
              ...accumulatedSteps[stepIndex],
              status: data.status || "completed",
              summary: data.summary || accumulatedSteps[stepIndex].summary,
              data: data.data || accumulatedSteps[stepIndex].data,
            };
          } else {
            accumulatedSteps.push({
              step_id: data.step_id,
              agent: data.agent,
              action: data.action,
              label: data.label || `Step ${data.step_id}`,
              status: data.status || "completed",
              summary: data.summary,
              data: data.data,
            });
          }
          updateCurrentAssistantMessage({
            thoughtSteps: [...accumulatedSteps],
          });
        },
        onToken: (token) => {
          accumulatedContent += token;
          updateCurrentAssistantMessage({
            content: accumulatedContent,
          });
        },
        onDone: (data) => {
          accumulatedSource = data.source || accumulatedSource;
          accumulatedModel = data.model || accumulatedModel;
          if (data.response_text) {
            accumulatedContent = data.response_text;
          }

          if (data.steps && data.steps.length > 0) {
            accumulatedSteps = data.steps;
          } else {
            accumulatedSteps = accumulatedSteps.map((s) => ({
              ...s,
              status: s.status === "running" ? "completed" : s.status,
            }));
          }

          // Final update and commit to localStorage
          setSessions((prevSessions) => {
            const next = prevSessions.map((session) => {
              if (session.id !== updatedSession.id) return session;
              return {
                ...session,
                messages: session.messages.map((m) => {
                  if (m.id !== assistantMsgId) return m;
                  return {
                    ...m,
                    content: accumulatedContent,
                    source: accumulatedSource,
                    model: accumulatedModel,
                    thoughtSteps: [...accumulatedSteps],
                    isStreaming: false,
                  };
                }),
              };
            });
            localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(next));
            return next;
          });
        },
        onError: (errMsg) => {
          setError(errMsg);
          updateCurrentAssistantMessage({
            isStreaming: false,
          });
        },
      });
    } catch (err: any) {
      console.error("Streaming chat failed, checking fallback:", err);
      // Fallback: if streaming failed before any response, attempt fallback non-streaming
      if (!accumulatedContent && accumulatedSteps.length === 0) {
        try {
          const fallbackData = await sendChatMessage(content, selectedModel);
          const answerContent =
            typeof fallbackData.answer === "string"
              ? fallbackData.answer
              : fallbackData.answer?.response || "";
          const answerModel =
            typeof fallbackData.answer === "string"
              ? fallbackData.model || selectedModel
              : fallbackData.answer?.model || selectedModel;

          setSessions((prevSessions) => {
            const next = prevSessions.map((session) => {
              if (session.id !== updatedSession.id) return session;
              return {
                ...session,
                messages: session.messages.map((m) => {
                  if (m.id !== assistantMsgId) return m;
                  return {
                    ...m,
                    content: answerContent,
                    source: fallbackData.source,
                    model: answerModel,
                    isStreaming: false,
                  };
                }),
              };
            });
            localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(next));
            return next;
          });
          return;
        } catch (fallbackErr: any) {
          console.error("Fallback non-streaming also failed:", fallbackErr);
        }
      }

      updateCurrentAssistantMessage({ isStreaming: false });
      const serverError = err.message;
      if (
        serverError &&
        (serverError.includes("429") ||
          serverError.toLowerCase().includes("quota") ||
          serverError.toLowerCase().includes("rate limit"))
      ) {
        setError(
          "AI quota or rate limit exceeded. Switch model selector at bottom to alternate model."
        );
      } else {
        setError(serverError || "Failed to fetch response. Please try again.");
      }
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
    documents,
    isUploading,
    uploadError,
    uploadFile,
    fetchDocuments,
  };
};
