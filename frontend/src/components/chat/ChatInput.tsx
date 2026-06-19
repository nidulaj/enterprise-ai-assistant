import React, { useRef, useEffect, useState } from "react";
import { Send, ArrowUp } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-grow textarea height based on content
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to calculate scrollHeight correctly
    textarea.style.height = "auto";
    // Set to scrollHeight but clamp it at a reasonable max-height
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, [input]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSendMessage(input);
    setInput("");
    
    // Focus back on textarea and reset height
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.style.height = "auto";
      }
    }, 50);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-4 md:py-6">
      <div className="relative flex items-end w-full rounded-2xl border border-slate-200 bg-white shadow-sm focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message to Enterprise AI..."
          disabled={isLoading}
          className="flex-1 resize-none bg-transparent py-4 pl-4 pr-14 text-sm text-slate-800 placeholder-slate-400 focus:outline-none max-h-48 min-h-[52px]"
          style={{ height: "auto" }}
        />
        <div className="absolute right-3 bottom-3 flex items-center">
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`flex h-8 w-8 items-center justify-center rounded-lg transition-all ${
              input.trim() && !isLoading
                ? "bg-slate-900 text-white hover:bg-slate-800"
                : "bg-slate-100 text-slate-400 cursor-not-allowed"
            }`}
          >
            {isLoading ? (
              <span className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></span>
            ) : (
              <ArrowUp size={18} />
            )}
          </button>
        </div>
      </div>
      <p className="mt-2 text-center text-xs text-slate-400">
        Enterprise AI Assistant can make mistakes. Consider checking important information.
      </p>
    </div>
  );
};

export default ChatInput;
