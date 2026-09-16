import React, { useState, useEffect } from "react";
import { ThoughtStep } from "@/types/chat";
import {
  Brain,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Circle,
  Loader2,
  AlertCircle,
  Calendar,
  CheckSquare,
  Mail,
  FileText,
  Sparkles,
  ExternalLink,
} from "lucide-react";

interface ThoughtStreamProps {
  steps: ThoughtStep[];
  isStreaming?: boolean;
}

export const ThoughtStream: React.FC<ThoughtStreamProps> = ({
  steps,
  isStreaming = false,
}) => {
  // Start expanded while streaming, allow user toggle
  const [isOpen, setIsOpen] = useState(true);

  // Auto-expand when streaming begins
  useEffect(() => {
    if (isStreaming) {
      setIsOpen(true);
    }
  }, [isStreaming]);

  if (!steps || steps.length === 0) {
    return null;
  }

  const completedCount = steps.filter((s) => s.status === "completed").length;
  const hasError = steps.some((s) => s.status === "error");
  const isAllCompleted = completedCount === steps.length && !isStreaming;

  const getAgentConfig = (agentName: string) => {
    const name = (agentName || "").toLowerCase();
    switch (name) {
      case "clickup":
        return {
          name: "ClickUp",
          icon: <CheckSquare size={12} className="text-purple-600" />,
          badgeColor: "bg-purple-50 text-purple-700 border-purple-200/60",
        };
      case "calendar":
        return {
          name: "Calendar",
          icon: <Calendar size={12} className="text-teal-600" />,
          badgeColor: "bg-teal-50 text-teal-700 border-teal-200/60",
        };
      case "email":
        return {
          name: "Email",
          icon: <Mail size={12} className="text-blue-600" />,
          badgeColor: "bg-blue-50 text-blue-700 border-blue-200/60",
        };
      case "knowledge":
      case "documents":
        return {
          name: "Knowledge Base",
          icon: <FileText size={12} className="text-amber-600" />,
          badgeColor: "bg-amber-50 text-amber-700 border-amber-200/60",
        };
      default:
        return {
          name: "AI Planner",
          icon: <Sparkles size={12} className="text-indigo-600" />,
          badgeColor: "bg-indigo-50 text-indigo-700 border-indigo-200/60",
        };
    }
  };

  return (
    <div className="w-full mb-3 rounded-xl border border-slate-200/90 bg-slate-50/60 backdrop-blur-sm overflow-hidden transition-all text-xs">
      {/* Accordion Header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3.5 py-2 hover:bg-slate-100/70 transition-colors text-left select-none cursor-pointer"
      >
        <div className="flex items-center gap-2 min-w-0">
          <div
            className={`flex h-5 w-5 items-center justify-center rounded-md ${
              isStreaming
                ? "bg-indigo-100 text-indigo-600"
                : isAllCompleted
                ? "bg-emerald-100 text-emerald-600"
                : "bg-slate-200 text-slate-600"
            }`}
          >
            {isStreaming ? (
              <Loader2 size={12} className="animate-spin text-indigo-600" />
            ) : isAllCompleted ? (
              <CheckCircle2 size={12} className="text-emerald-600" />
            ) : (
              <Brain size={12} />
            )}
          </div>

          <div className="flex items-center gap-1.5 truncate">
            <span className="font-semibold text-slate-700">
              {isStreaming
                ? `Executing Agent Plan (${completedCount}/${steps.length})`
                : hasError
                ? `Agent Plan encountered an issue`
                : `Plan Execution (${steps.length} step${
                    steps.length > 1 ? "s" : ""
                  } completed)`}
            </span>
            {isStreaming && (
              <span className="flex h-1.5 w-1.5 rounded-full bg-indigo-600 animate-ping" />
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-[11px] font-medium text-slate-500">
            {isOpen ? "Hide details" : "View steps"}
          </span>
          {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </button>

      {/* Accordion Content */}
      {isOpen && (
        <div className="px-3.5 pb-3 pt-1 border-t border-slate-200/50 space-y-2">
          {steps.map((step, index) => {
            const agentCfg = getAgentConfig(step.agent);
            const isCurrent = step.status === "running";
            const isDone = step.status === "completed";
            const isFailed = step.status === "error";

            return (
              <div
                key={step.step_id || index}
                className={`flex items-start gap-2.5 p-2 rounded-lg transition-all ${
                  isCurrent
                    ? "bg-white border border-indigo-200/80 shadow-sm"
                    : isDone
                    ? "bg-white/60 border border-slate-200/50"
                    : isFailed
                    ? "bg-red-50/50 border border-red-200/60"
                    : "bg-transparent opacity-60"
                }`}
              >
                {/* Status Indicator Icon */}
                <div className="mt-0.5 shrink-0">
                  {isCurrent ? (
                    <Loader2 size={14} className="animate-spin text-indigo-600" />
                  ) : isDone ? (
                    <CheckCircle2 size={14} className="text-emerald-500" />
                  ) : isFailed ? (
                    <AlertCircle size={14} className="text-red-500" />
                  ) : (
                    <Circle size={14} className="text-slate-300" />
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {/* Agent Pill Badge */}
                    <span
                      className={`inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded border leading-none tracking-wide ${agentCfg.badgeColor}`}
                    >
                      {agentCfg.icon}
                      <span>{agentCfg.name}</span>
                    </span>

                    {/* Step Label */}
                    <span
                      className={`font-medium text-[12px] truncate ${
                        isCurrent
                          ? "text-indigo-950 font-semibold"
                          : isDone
                          ? "text-slate-800"
                          : isFailed
                          ? "text-red-700 font-semibold"
                          : "text-slate-500"
                      }`}
                    >
                      {step.label || `Step ${step.step_id}`}
                    </span>
                  </div>

                  {/* Summary / Result Text */}
                  {step.summary && (
                    <p className="mt-1 text-[11px] text-slate-600 leading-relaxed break-words">
                      {step.summary}
                    </p>
                  )}

                  {/* Link Pill if Meet URL or Web link present */}
                  {step.data?.meet_link && (
                    <a
                      href={step.data.meet_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1.5 inline-flex items-center gap-1 text-[11px] font-medium text-teal-700 bg-teal-50 border border-teal-200/80 px-2 py-0.5 rounded hover:bg-teal-100 transition-colors"
                    >
                      <span>Join Google Meet</span>
                      <ExternalLink size={10} />
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ThoughtStream;
