"use client";

import React, { useState } from "react";
import ChatSidebar from "@/components/chat/ChatSidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import { useChat } from "@/hooks/useChat";

export default function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  const {
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
  } = useChat();

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  return (
    <div className="h-screen w-full flex overflow-hidden bg-slate-50 font-sans antialiased text-slate-800">
      {/* Sidebar Navigation */}
      <ChatSidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={selectSession}
        onDeleteSession={deleteSession}
        onNewChat={startNewChat}
        isOpen={isSidebarOpen}
        onToggleSidebar={toggleSidebar}
        documents={documents}
        onUploadFile={uploadFile}
        isUploading={isUploading}
        uploadError={uploadError}
      />

      {/* Main Conversation Window */}
      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        error={error}
        selectedModel={selectedModel}
        onChangeModel={changeModel}
        onSendMessage={sendMessage}
        onToggleSidebar={toggleSidebar}
      />
    </div>
  );
}