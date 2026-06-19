import React from "react";
import { Bot } from "lucide-react";

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex w-full items-start gap-4 py-6 px-4 sm:px-6 bg-slate-50/50 border-y border-slate-100/50">
      <div className="flex w-full max-w-4xl mx-auto gap-4">
        {/* Assistant Avatar */}
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-lg text-sm font-semibold shadow-sm bg-gradient-to-tr from-indigo-600 to-violet-500 text-white">
          <Bot size={18} className="animate-pulse" />
        </div>

        {/* Message Container */}
        <div className="flex flex-col items-start">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-slate-500">Enterprise AI</span>
            <span className="text-[10px] text-slate-400">thinking...</span>
          </div>

          {/* Bouncing Dots Bubble */}
          <div className="bg-white border border-slate-100 shadow-sm rounded-2xl px-5 py-3.5 flex items-center gap-1.5 h-10">
            <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]"></span>
            <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]"></span>
            <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
