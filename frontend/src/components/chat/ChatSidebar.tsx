import React, { useRef } from "react";
import { ChatSession, DocumentItem } from "@/types/chat";
import { MessageSquare, Plus, Trash2, Bot, Menu, X, Upload, FileText } from "lucide-react";

interface ChatSidebarProps {
  sessions: ChatSession[];
  currentSessionId: string;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string, event: React.MouseEvent) => void;
  onNewChat: () => void;
  isOpen: boolean;
  onToggleSidebar: () => void;
  documents: DocumentItem[];
  onUploadFile: (file: File) => Promise<void>;
  isUploading: boolean;
  uploadError: string | null;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat,
  isOpen,
  onToggleSidebar,
  documents,
  onUploadFile,
  isUploading,
  uploadError,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onUploadFile(files[0]);
    }
  };
  return (
    <>
      {/* Mobile Drawer Backdrop */}
      {isOpen && (
        <div
          onClick={onToggleSidebar}
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm md:hidden transition-opacity duration-300"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex w-72 flex-col border-r border-slate-200 bg-slate-950 text-slate-200 transition-transform duration-300 ease-in-out md:static md:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Sidebar Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-md">
              <Bot size={18} />
            </div>
            <span className="font-bold text-sm bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              Enterprise Suite
            </span>
          </div>
          {/* Close button on mobile */}
          <button
            onClick={onToggleSidebar}
            className="rounded-lg p-1.5 hover:bg-slate-800 md:hidden text-slate-400 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Action Button Container */}
        <div className="p-4">
          <button
            onClick={() => {
              onNewChat();
              // Auto close sidebar on mobile after starting new chat
              if (window.innerWidth < 768) {
                onToggleSidebar();
              }
            }}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-3 text-sm font-semibold text-white shadow-md hover:from-indigo-500 hover:to-violet-500 hover:shadow-indigo-500/20 active:scale-98 transition-all"
          >
            <Plus size={18} />
            New chat
          </button>
        </div>

        {/* History List */}
        <div className="flex-[3] overflow-y-auto px-3 py-2 space-y-1 scrollbar-thin border-b border-slate-800/80">
          <div className="px-3 py-1.5 text-xs font-semibold text-slate-500 tracking-wider uppercase">
            Recent Chats
          </div>
          
          {sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center px-4">
              <MessageSquare size={24} className="text-slate-700 mb-2" />
              <p className="text-xs text-slate-500">No recent chats</p>
            </div>
          ) : (
            sessions.map((session) => {
              const isActive = session.id === currentSessionId;
              return (
                <div
                  key={session.id}
                  onClick={() => {
                    onSelectSession(session.id);
                    if (window.innerWidth < 768) {
                      onToggleSidebar();
                    }
                  }}
                  className={`group relative flex items-center justify-between rounded-xl px-3 py-3 text-sm cursor-pointer transition-all ${
                    isActive
                      ? "bg-slate-800 text-white font-medium shadow-sm"
                      : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0 pr-6">
                    <MessageSquare size={16} className={`shrink-0 ${isActive ? "text-indigo-400" : "text-slate-500"}`} />
                    <span className="truncate text-xs">{session.title}</span>
                  </div>
                  
                  {/* Delete button (only shows on hover in desktop, or default in mobile/active) */}
                  <button
                    onClick={(e) => onDeleteSession(session.id, e)}
                    className="absolute right-2.5 opacity-0 group-hover:opacity-100 hover:text-red-400 p-1 rounded transition-all"
                    title="Delete Chat"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Knowledge Base Section */}
        <div className="flex-[2] flex flex-col min-h-0 bg-slate-950/40">
          <div className="flex items-center justify-between px-6 py-3 border-b border-slate-800/80 shrink-0">
            <span className="text-xs font-semibold text-slate-500 tracking-wider uppercase">
              Knowledge Base
            </span>
            <button
              onClick={handleUploadClick}
              disabled={isUploading}
              className="text-slate-400 hover:text-white disabled:text-slate-600 disabled:cursor-not-allowed transition-colors cursor-pointer"
              title="Upload PDF Document"
            >
              <Upload size={14} className={isUploading ? "animate-pulse" : ""} />
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf"
              className="hidden"
            />
          </div>

          <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 scrollbar-thin">
            {isUploading && (
              <div className="flex items-center gap-2.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800/60 text-xs text-indigo-400">
                <span className="shrink-0 w-3.5 h-3.5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></span>
                <span className="truncate text-[11px]">Indexing PDF...</span>
              </div>
            )}

            {uploadError && (
              <div className="px-3 py-2 rounded-xl bg-red-950/30 border border-red-900/40 text-[10px] text-red-400 leading-relaxed break-words">
                {uploadError}
              </div>
            )}

            {documents.length === 0 ? (
              !isUploading && (
                <div className="flex flex-col items-center justify-center py-6 text-center px-4">
                  <FileText size={18} className="text-slate-800 mb-1" />
                  <p className="text-[10px] text-slate-600">No documents uploaded</p>
                </div>
              )
            ) : (
              documents.map((doc) => (
                <a
                  key={doc.id}
                  href={doc.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 rounded-xl px-3 py-2 text-slate-400 hover:bg-slate-900 hover:text-slate-200 transition-all select-none group"
                >
                  <FileText size={15} className="shrink-0 text-emerald-500/80 group-hover:text-emerald-400 transition-colors" />
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-xs text-slate-300 group-hover:text-white transition-colors">
                      {doc.name}
                    </p>
                    <p className="text-[9px] text-slate-600">
                      {new Date(doc.uploaded_at).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </a>
              ))
            )}
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-semibold text-slate-300">
              EA
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-300 truncate">Enterprise User</p>
              <p className="text-[10px] text-slate-500 truncate">user@enterprise.ai</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default ChatSidebar;
