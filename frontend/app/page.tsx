"use client";

import { useState } from "react";
import { ChatArea } from "@/components/chat-area";
import { DocumentPanel } from "@/components/document-panel";

export default function Home() {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  return (
    <div className="flex h-screen w-screen bg-[#0A0A0A] overflow-hidden">
      {/* Chat Area - Takes remaining space */}
      <div className="flex-1 flex flex-col min-h-0">
        <ChatArea />
      </div>

      {/* Document Panel - Fixed width on right */}
      <DocumentPanel
        selectedDocument={selectedDocument}
        onSelectDocument={setSelectedDocument}
      />
    </div>
  );
}
