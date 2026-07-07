import React from "react";
import { Message } from "@/types/chat";
import { Bot, User } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isAssistant = message.role === "assistant";
  
  // Format the ISO timestamp to a readable time (e.g. "5:30 PM")
  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  };

  const getBadge = (source?: string) => {
    if (source === "documents") {
      return {
        text: "Knowledge Assistant",
        emoji: "📄",
        color: "bg-emerald-50 text-emerald-700 border-emerald-200/50"
      };
    }
    if (source === "clickup") {
      return {
        text: "ClickUp Agent",
        emoji: "📋",
        color: "bg-amber-50 text-amber-700 border-amber-200/50"
      };
    }
    return {
      text: "AI Assistant",
      emoji: "🤖",
      color: "bg-indigo-50 text-indigo-700 border-indigo-200/50"
    };
  };

  return (
    <div
      className={`flex w-full items-start gap-4 py-6 px-4 sm:px-6 transition-all duration-300 animate-fadeIn ${
        isAssistant
          ? "bg-slate-50/50 border-y border-slate-100/50"
          : "bg-transparent"
      }`}
    >
      <div className={`flex w-full max-w-4xl mx-auto gap-4 ${!isAssistant ? "flex-row-reverse" : "flex-row"}`}>
        {/* Avatar */}
        <div
          className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-lg text-sm font-semibold shadow-sm ${
            isAssistant
              ? "bg-gradient-to-tr from-indigo-600 to-violet-500 text-white"
              : "bg-slate-200 text-slate-700"
          }`}
        >
          {isAssistant ? (
            <Bot size={18} className="animate-pulse-slow" />
          ) : (
            <User size={18} />
          )}
        </div>

        {/* Message Content Container */}
        <div className={`flex flex-col max-w-[85%] ${!isAssistant ? "items-end" : "items-start"}`}>
          {/* Sender Role Label */}
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-xs font-semibold text-slate-500">
              {isAssistant ? "Enterprise AI" : "You"}
            </span>
            {isAssistant && (
              (() => {
                const badge = getBadge(message.source);
                return (
                  <span className={`inline-flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded-md border leading-none tracking-wide ${badge.color}`}>
                    <span>{badge.emoji}</span>
                    <span>{badge.text}</span>
                  </span>
                );
              })()
            )}
            {isAssistant && message.model && (
              <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded-md bg-slate-100 border border-slate-200/80 text-slate-600 tracking-wider">
                {message.model}
              </span>
            )}
            <span className="text-[10px] text-slate-400">
              {formatTime(message.timestamp)}
            </span>
          </div>

          {/* Actual Bubble Text */}
          <div
            className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              isAssistant
                ? "bg-white text-slate-800 border border-slate-100 shadow-sm whitespace-pre-wrap"
                : "bg-slate-900 text-slate-50 shadow-md whitespace-pre-wrap"
            }`}
          >
            {message.content}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
