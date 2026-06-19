import React, { useRef, useEffect, useState } from "react";
import { ArrowUp, Sparkles, Brain, Zap, ChevronUp } from "lucide-react";
import { ModelOption } from "@/types/chat";

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  isLoading: boolean;
  selectedModel: ModelOption;
  onChangeModel: (model: ModelOption) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  selectedModel,
  onChangeModel,
}) => {
  const [input, setInput] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
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
      <div className="relative flex flex-col w-full rounded-2xl border border-slate-200 bg-white shadow-sm focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message to Enterprise AI..."
          disabled={isLoading}
          className="w-full resize-none bg-transparent pt-4 pb-2 px-4 text-sm text-slate-800 placeholder-slate-400 focus:outline-none max-h-48 min-h-[52px]"
          style={{ height: "auto" }}
        />
        
        <div className="flex items-center justify-between px-3 pb-3 pt-1 border-t border-slate-50">
          {/* Model Selection on Left */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200/60 text-slate-600 hover:text-slate-800 text-xs font-semibold transition-all cursor-pointer select-none"
            >
              {selectedModel === "auto" && <Sparkles size={13} className="text-violet-500" />}
              {selectedModel === "gemini" && <Brain size={13} className="text-indigo-500" />}
              {selectedModel === "groq" && <Zap size={13} className="text-amber-500" />}
              <span className="capitalize">{selectedModel}</span>
              <ChevronUp size={12} className={`transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Upward Dropdown Menu */}
            {isDropdownOpen && (
              <>
                {/* Overlay to close */}
                <div className="fixed inset-0 z-20" onClick={() => setIsDropdownOpen(false)} />
                
                <div className="absolute bottom-full left-0 mb-2 w-56 rounded-xl border border-slate-200 bg-white p-1.5 shadow-xl ring-1 ring-black/5 z-30 animate-fadeIn">
                  {(["auto", "gemini", "groq"] as ModelOption[]).map((model) => (
                    <button
                      key={model}
                      type="button"
                      onClick={() => {
                        onChangeModel(model);
                        setIsDropdownOpen(false);
                      }}
                      className={`flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2 text-left transition-colors cursor-pointer ${
                        selectedModel === model
                          ? "bg-slate-50 text-slate-900"
                          : "text-slate-600 hover:bg-slate-50/70 hover:text-slate-900"
                      }`}
                    >
                      <div className="mt-0.5">
                        {model === "auto" && <Sparkles size={14} className="text-violet-500" />}
                        {model === "gemini" && <Brain size={14} className="text-indigo-500" />}
                        {model === "groq" && <Zap size={14} className="text-amber-500" />}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs font-bold capitalize">{model}</span>
                        <span className="text-[10px] text-slate-400">
                          {model === "auto" && "Best response from any model"}
                          {model === "gemini" && "Gemini 2.5 Flash"}
                          {model === "groq" && "Groq (Llama 3.3)"}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Send Button on Right */}
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
