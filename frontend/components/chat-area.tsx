"use client";

import { useState, useRef, useEffect } from "react";
import { MessageList } from "@/components/message-list";
import { ChatInput } from "@/components/chat-input";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Array<{
    file: string;
    chunk_index: number;
    has_tables: boolean;
    has_images: boolean;
    ai_summarized: boolean;
  }>;
  isStreaming?: boolean;
}

export function ChatArea() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your RAG Assistant. I can help you find information from your documents. Ask me anything about employee benefits, policies, or procedures.",
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(
    null,
  ) as React.RefObject<HTMLDivElement>;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Simulate streaming response
    // TODO: Replace with actual streaming API call
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "This is a placeholder response. Connect your streaming API endpoint to see real-time token streaming. The response will appear word by word as it's generated.",
        timestamp: new Date(),
        sources: [
          {
            file: "employee_handbook.pdf",
            chunk_index: 5,
            has_tables: true,
            has_images: false,
            ai_summarized: true,
          },
          {
            file: "benefits_guide.pdf",
            chunk_index: 12,
            has_tables: false,
            has_images: true,
            ai_summarized: false,
          },
        ],
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-[#0A0A0A]">
      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <MessageList
          messages={messages}
          isLoading={isLoading}
          messagesEndRef={messagesEndRef}
        />
      </div>

      {/* Input Area */}
      <div className="border-t border-white/5 bg-[#0A0A0A]">
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
