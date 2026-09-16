import React from "react";
import { Message } from "@/types/chat";
import { Bot, User, Copy, Check } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ThoughtStream from "./ThoughtStream";


interface CodeBlockProps {
  language: string;
  code: string;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ language, code }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code: ", err);
    }
  };

  return (
    <div className="my-3 overflow-hidden rounded-xl border border-slate-200/80 shadow-sm bg-slate-950 text-slate-200 font-mono text-xs w-full max-w-full">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800/80 text-slate-400 select-none">
        <span className="text-[10px] font-bold tracking-wider uppercase">
          {language}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] font-semibold hover:text-slate-100 hover:bg-slate-800 transition-all cursor-pointer active:scale-95"
        >
          {copied ? (
            <>
              <Check size={12} className="text-emerald-400" />
              <span className="text-emerald-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy size={12} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      {/* Code Area */}
      <div className="p-4 overflow-x-auto scrollbar-thin">
        <pre className="m-0 leading-relaxed whitespace-pre font-mono">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};


interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isAssistant = message.role === "assistant";

  const components = React.useMemo(() => {
    return {
      h1: ({ children }: any) => (
        <h1 className={`text-base font-bold mt-4 mb-2 first:mt-0 ${isAssistant ? "text-slate-900" : "text-white"}`}>
          {children}
        </h1>
      ),
      h2: ({ children }: any) => (
        <h2 className={`text-sm font-bold mt-3 mb-1.5 first:mt-0 ${isAssistant ? "text-slate-900" : "text-white"}`}>
          {children}
        </h2>
      ),
      h3: ({ children }: any) => (
        <h3 className={`text-sm font-bold mt-2.5 mb-1.5 first:mt-0 ${isAssistant ? "text-slate-800" : "text-slate-100"}`}>
          {children}
        </h3>
      ),
      h4: ({ children }: any) => (
        <h4 className={`text-[13px] font-bold mt-2 mb-1 first:mt-0 ${isAssistant ? "text-slate-800" : "text-slate-200"}`}>
          {children}
        </h4>
      ),
      p: ({ children }: any) => (
        <p className={`mb-3 last:mb-0 leading-relaxed whitespace-pre-wrap ${isAssistant ? "text-slate-700" : "text-slate-200"}`}>
          {children}
        </p>
      ),
      ul: ({ children }: any) => (
        <ul className="list-disc pl-5 mb-3 last:mb-0 space-y-1">
          {children}
        </ul>
      ),
      ol: ({ children }: any) => (
        <ol className="list-decimal pl-5 mb-3 last:mb-0 space-y-1">
          {children}
        </ol>
      ),
      li: ({ children }: any) => (
        <li className={`pl-0.5 text-sm ${isAssistant ? "text-slate-700" : "text-slate-200"}`}>
          {children}
        </li>
      ),
      strong: ({ children }: any) => (
        <strong className={`font-bold ${isAssistant ? "text-slate-900" : "text-white"}`}>
          {children}
        </strong>
      ),
      em: ({ children }: any) => (
        <em className="italic">
          {children}
        </em>
      ),
      a: ({ href, children }: any) => (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className={`hover:underline break-all font-medium ${isAssistant ? "text-indigo-600" : "text-indigo-300"}`}
        >
          {children}
        </a>
      ),
      code: ({ className, children, ...props }: any) => {
        const match = /language-(\w+)/.exec(className || "");
        const codeContent = String(children).replace(/\n$/, "");
        const isInline = !className && !codeContent.includes('\n');

        if (isInline) {
          return (
            <code
              className={`font-mono text-xs px-1.5 py-0.5 rounded font-semibold ${
                isAssistant
                  ? "bg-slate-100 text-slate-800 border border-slate-200/50"
                  : "bg-slate-800 text-slate-200 border border-slate-700/50"
              }`}
              {...props}
            >
              {children}
            </code>
          );
        }

        return (
          <CodeBlock language={match ? match[1] : "text"} code={codeContent} />
        );
      }
    };
  }, [isAssistant]);
  
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
    if (source === "email") {
      return {
        text: "Email Agent",
        emoji: "✉️",
        color: "bg-blue-50 text-blue-700 border-blue-200/50"
      };
    }
    if (source === "calendar") {
      return {
        text: "Calendar Agent",
        emoji: "📅",
        color: "bg-teal-50 text-teal-700 border-teal-200/50"
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

          {/* Render Thought Stream if steps are present */}
          {isAssistant && message.thoughtSteps && message.thoughtSteps.length > 0 && (
            <ThoughtStream
              steps={message.thoughtSteps}
              isStreaming={message.isStreaming}
            />
          )}

          {/* Actual Bubble Text */}
          {(message.content || !message.isStreaming) && (
            <div
              className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                isAssistant
                  ? "bg-white text-slate-800 border border-slate-100 shadow-sm"
                  : "bg-slate-900 text-slate-50 shadow-md"
              }`}
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                {message.content}
              </ReactMarkdown>
              {message.isStreaming && (
                <span className="inline-block w-1.5 h-4 ml-1 bg-indigo-600 animate-pulse align-middle rounded-sm" />
              )}
            </div>
          )}

          {/* If streaming with no content yet and no thought steps, show initializing status */}
          {message.isStreaming && !message.content && (!message.thoughtSteps || message.thoughtSteps.length === 0) && (
            <div className="bg-white border border-slate-100 shadow-sm rounded-2xl px-4 py-3 text-xs text-slate-500 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-ping" />
              <span>Supervisor analyzing query and preparing agent plan...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
