import React, { useRef, useEffect } from "react";
import { Message, ModelOption } from "@/types/chat";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import ChatInput from "./ChatInput";
import { Menu, Wifi, Sparkles, Terminal, BookOpen, MessageSquarePlus } from "lucide-react";

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  selectedModel: ModelOption;
  onChangeModel: (model: ModelOption) => void;
  onSendMessage: (content: string) => void;
  onToggleSidebar: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  error,
  selectedModel,
  onChangeModel,
  onSendMessage,
  onToggleSidebar,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Suggested starting prompts for empty state
  const SUGGESTIONS = [
    {
      icon: <Terminal size={18} className="text-violet-500" />,
      title: "Debug a Query",
      desc: "Analyze and optimize a slow PostgreSQL query.",
      prompt: "Can you help me analyze and optimize a slow-running PostgreSQL database query? Here is the structure...",
    },
    {
      icon: <Sparkles size={18} className="text-amber-500" />,
      title: "Review Architecture",
      desc: "Compare Next.js App vs Pages Router layouts.",
      prompt: "What are the main differences between Next.js App Router and Pages Router, and which one is better suited for a data-heavy enterprise dashboard?",
    },
    {
      icon: <BookOpen size={18} className="text-emerald-500" />,
      title: "Draft Policy",
      desc: "Create an enterprise internal AI usage guide.",
      prompt: "Draft an employee internal policy document outlining the responsible and compliant use of generative AI tools in the workplace.",
    },
  ];

  return (
    <div className="flex flex-1 flex-col h-full bg-slate-50 relative overflow-hidden">
      {/* Top Header */}
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 md:px-6 shadow-sm z-10">
        <div className="flex items-center gap-3">
          {/* Hamburger Menu Toggle */}
          <button
            onClick={onToggleSidebar}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 md:hidden transition-colors"
          >
            <Menu size={20} />
          </button>
          
          <div className="flex flex-col">
            <h1 className="text-sm font-bold text-slate-800 flex items-center gap-1.5 leading-none">
              Enterprise AI Assistant
            </h1>
            <span className="text-[10px] text-slate-400 font-semibold flex items-center gap-1 mt-1">
              <Wifi size={10} className="text-emerald-500 animate-pulse" />
              Connected
            </span>
          </div>
        </div>

      </header>

      {/* Main Messages Panel */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden flex flex-col">
        {messages.length === 0 ? (
          /* Landing/Empty State */
          <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-4xl mx-auto w-full">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 border border-indigo-100 shadow-sm text-indigo-600 mb-4 animate-bounce-slow">
              <Sparkles size={24} />
            </div>
            
            <h2 className="text-2xl font-bold text-slate-800 tracking-tight">
              Hello, how can I assist you today?
            </h2>
            <p className="mt-2 text-sm text-slate-500 max-w-md">
              Ask about database designs, strategic planning, writing code, or optimizing pipelines.
            </p>

            {/* Suggestions Grid */}
            <div className="mt-10 grid gap-4 sm:grid-cols-3 w-full">
              {SUGGESTIONS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => onSendMessage(s.prompt)}
                  className="flex flex-col items-start text-left p-4 rounded-2xl border border-slate-200/80 bg-white hover:border-indigo-400 hover:shadow-md active:scale-98 transition-all group cursor-pointer"
                >
                  <div className="p-2 bg-slate-50 rounded-xl mb-3 group-hover:bg-indigo-50 transition-colors">
                    {s.icon}
                  </div>
                  <h3 className="text-xs font-bold text-slate-800">{s.title}</h3>
                  <p className="mt-1 text-[11px] leading-normal text-slate-500">{s.desc}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Chat Message List */
          <div className="flex-1 flex flex-col py-2 w-full">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}

            {/* Loading / Typing indicator */}
            {isLoading && <TypingIndicator />}

            {/* Backend connection error notification */}
            {error && (
              <div className="flex w-full items-start gap-4 py-4 px-4 sm:px-6 bg-red-50/50 border-y border-red-100/50">
                <div className="flex w-full max-w-4xl mx-auto items-center justify-between text-xs text-red-700 bg-red-50 border border-red-200/60 rounded-xl px-4 py-3 shadow-sm">
                  <span className="font-semibold">{error}</span>
                  <button 
                    onClick={() => {
                      const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
                      if (lastUserMsg) onSendMessage(lastUserMsg.content);
                    }}
                    className="ml-4 underline hover:text-red-900 cursor-pointer font-bold shrink-0"
                  >
                    Retry send
                  </button>
                </div>
              </div>
            )}

            {/* Dummy element for scroll anchoring */}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        )}
      </div>

      {/* Input Form Panel */}
      <footer className="shrink-0 bg-slate-50 border-t border-slate-200/60 z-10">
        <ChatInput
          onSendMessage={onSendMessage}
          isLoading={isLoading}
          selectedModel={selectedModel}
          onChangeModel={onChangeModel}
        />
      </footer>
    </div>
  );
};

export default ChatWindow;
