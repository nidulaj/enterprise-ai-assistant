import React, { useState, useEffect } from "react";
import { ThoughtStep } from "@/types/chat";
import {
  Brain,
  ChevronDown,
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

export const formatActionName = (action?: string, label?: string) => {
  if (action && action !== "general_chat") {
    return action.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  }
  return label || "Action";
};

export const getAgentConfig = (agentName: string) => {
  const name = (agentName || "").toLowerCase();
  switch (name) {
    case "clickup":
      return {
        name: "ClickUp",
        icon: <CheckSquare size={11} className="text-purple-600" />,
        badgeColor: "bg-purple-50 text-purple-700 border-purple-200/60",
      };
    case "calendar":
      return {
        name: "Calendar",
        icon: <Calendar size={11} className="text-teal-600" />,
        badgeColor: "bg-teal-50 text-teal-700 border-teal-200/60",
      };
    case "email":
      return {
        name: "Email",
        icon: <Mail size={11} className="text-blue-600" />,
        badgeColor: "bg-blue-50 text-blue-700 border-blue-200/60",
      };
    case "knowledge":
    case "documents":
      return {
        name: "Knowledge Base",
        icon: <FileText size={11} className="text-amber-600" />,
        badgeColor: "bg-amber-50 text-amber-700 border-amber-200/60",
      };
    default:
      return {
        name: "Planner",
        icon: <Sparkles size={11} className="text-indigo-600" />,
        badgeColor: "bg-indigo-50 text-indigo-700 border-indigo-200/60",
      };
  }
};

interface ActiveExecutionBannerProps {
  runningStep?: ThoughtStep;
  nextStep?: ThoughtStep;
  completedCount: number;
  totalSteps: number;
}

export const ActiveExecutionBanner: React.FC<ActiveExecutionBannerProps> = ({
  runningStep,
  nextStep,
  completedCount,
  totalSteps,
}) => {
  if (!runningStep && !nextStep) return null;

  const activeStep = runningStep || nextStep;
  const cfg = activeStep ? getAgentConfig(activeStep.agent) : null;
  const isRunning = Boolean(runningStep);

  return (
    <div className="mt-3.5 pt-2.5 border-t border-slate-100 flex items-center justify-between gap-3 text-xs bg-indigo-50/70 border border-indigo-100/90 rounded-xl px-3.5 py-2.5 animate-fadeIn">
      <div className="flex items-center gap-2.5 min-w-0">
        <Loader2 size={13} className="animate-spin text-indigo-600 shrink-0" />
        <div className="flex items-center gap-2 truncate">
          <span className="font-semibold text-slate-500 text-[11px] uppercase tracking-wider shrink-0">
            {isRunning
              ? `Currently Executing (${completedCount + 1}/${totalSteps}):`
              : "Starting Next Step:"}
          </span>
          {cfg && (
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded border leading-none tracking-wide shrink-0 ${cfg.badgeColor}`}
            >
              {cfg.icon}
              <span>{cfg.name}</span>
            </span>
          )}
          <span className="font-semibold text-indigo-950 text-[12px] truncate">
            {formatActionName(activeStep?.action, activeStep?.label)}
          </span>
        </div>
      </div>

      {isRunning && nextStep && (
        <div className="hidden sm:flex items-center gap-1.5 text-[11px] text-slate-400 shrink-0">
          <span className="text-slate-400 font-normal">Next:</span>
          <span className="font-medium text-slate-600 truncate max-w-[150px]">
            {formatActionName(nextStep.action, nextStep.label)}
          </span>
        </div>
      )}
    </div>
  );
};

interface ThoughtStreamProps {
  steps: ThoughtStep[];
  isStreaming?: boolean;
}

export const ThoughtStream: React.FC<ThoughtStreamProps> = ({
  steps,
  isStreaming = false,
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const [startTime] = useState<number>(() => Date.now());
  const [durationSec, setDurationSec] = useState<number | null>(null);

  useEffect(() => {
    if (!isStreaming && durationSec === null) {
      const elapsed = Math.max(1, Math.round((Date.now() - startTime) / 1000));
      setDurationSec(elapsed);
    }
  }, [isStreaming, durationSec, startTime]);

  if (!steps || steps.length === 0) {
    return null;
  }

  const completedCount = steps.filter((s) => s.status === "completed").length;
  const runningStep = steps.find((s) => s.status === "running");
  const nextStep = steps.find((s) => s.status === "pending");
  const hasError = steps.some((s) => s.status === "error");
  const isAllCompleted = completedCount === steps.length && !isStreaming;
  const durationText = durationSec ? `${durationSec}s` : "a few seconds";

  return (
    <div className="w-full text-xs transition-all">
      {/* Accordion Toggle Header (ChatGPT / Antigravity style) */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="group flex items-center justify-between w-full py-1 px-1.5 -ml-1 rounded-lg hover:bg-slate-50 transition-colors select-none cursor-pointer text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <div
            className={`flex h-5 w-5 items-center justify-center rounded-md ${
              isStreaming
                ? "bg-indigo-50 text-indigo-600"
                : isAllCompleted
                ? "bg-emerald-50 text-emerald-600"
                : "bg-slate-100 text-slate-500"
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
            <span className="text-xs font-semibold text-slate-700 group-hover:text-slate-900 transition-colors">
              {isStreaming
                ? runningStep
                  ? `Thinking (Running: ${formatActionName(runningStep.action, runningStep.label)} ${completedCount + 1}/${steps.length})...`
                  : `Thinking (Executing ${completedCount}/${steps.length} steps)...`
                : hasError
                ? `Thought for ${durationText} • ${completedCount}/${steps.length} steps completed with warnings`
                : `Thought for ${durationText} • ${steps.length} step${steps.length > 1 ? "s" : ""} completed`}
            </span>
            {isStreaming && (
              <span className="flex h-1.5 w-1.5 rounded-full bg-indigo-600 animate-ping" />
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-slate-400 group-hover:text-slate-600 transition-colors shrink-0">
          <span className="text-[11px] font-medium text-slate-400">
            {isOpen ? "Hide" : "Show"}
          </span>
          <ChevronDown
            size={13}
            className={`transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
          />
        </div>
      </button>

      {/* Accordion Content with Antigravity / ChatGPT style left guide line */}
      {isOpen && (
        <div className="mt-2 pl-3 border-l-2 border-indigo-200/80 space-y-1.5">
          {steps.map((step, index) => {
            const agentCfg = getAgentConfig(step.agent);
            const isCurrent = step.status === "running";
            const isDone = step.status === "completed";
            const isFailed = step.status === "error";

            return (
              <div
                key={step.step_id || index}
                className={`flex items-center justify-between gap-2.5 py-1 px-2 rounded-lg text-xs transition-colors ${
                  isCurrent
                    ? "bg-indigo-50/70 border border-indigo-100 text-indigo-950 font-medium"
                    : isFailed
                    ? "bg-red-50/60 border border-red-100 text-red-900"
                    : "hover:bg-slate-50/80 text-slate-700"
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  {/* Status Indicator Icon */}
                  <div className="shrink-0 flex items-center justify-center">
                    {isCurrent ? (
                      <Loader2 size={13} className="animate-spin text-indigo-600" />
                    ) : isDone ? (
                      <CheckCircle2 size={13} className="text-emerald-500" />
                    ) : isFailed ? (
                      <AlertCircle size={13} className="text-red-500" />
                    ) : (
                      <Circle size={13} className="text-slate-300" />
                    )}
                  </div>

                  {/* Agent Pill Badge */}
                  <span
                    className={`inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded border leading-none tracking-wide shrink-0 ${agentCfg.badgeColor}`}
                  >
                    {agentCfg.icon}
                    <span>{agentCfg.name}</span>
                  </span>

                  {/* Action Name Only */}
                  <span className="text-[12px] truncate">
                    {step.action && step.action !== "general_chat"
                      ? step.action.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
                      : step.label || "Action"}
                  </span>
                </div>

                {/* Meet Link Button if present */}
                {step.data?.meet_link && (
                  <a
                    href={step.data.meet_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] font-semibold text-teal-700 bg-teal-50 border border-teal-200/80 px-2 py-0.5 rounded hover:bg-teal-100 transition-colors shrink-0"
                  >
                    <span>Join Meet</span>
                    <ExternalLink size={10} />
                  </a>
                )}

                {/* Failure summary note if step failed */}
                {isFailed && step.summary && (
                  <p className="text-[11px] text-red-600 pl-6 w-full">
                    {step.summary}
                  </p>
                )}
              </div>
            );
          })}

          {/* Next Up in Plan preview */}
          {isStreaming && nextStep && (
            <div className="flex items-center gap-2 py-1 px-2 text-[11px] text-slate-400">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
              <span>Next up:</span>
              <span className="font-semibold text-slate-600">
                {formatActionName(nextStep.action, nextStep.label)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ThoughtStream;
