"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "@/components/message-bubble";
import { Loader2 } from "lucide-react";

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

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

export function MessageList({
  messages,
  isLoading,
  messagesEndRef,
}: MessageListProps) {
  return (
    <ScrollArea className="h-full">
      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {messages.map((message, index) => (
          <MessageBubble
            key={message.id}
            message={message}
            isLatest={index === messages.length - 1}
          />
        ))}

        {isLoading && (
          <div className="flex items-start gap-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="w-8 h-8 rounded-full bg-linear-to-br from-white/10 to-white/5 flex items-center justify-center border border-white/10">
              <Loader2 className="h-4 w-4 text-white/60 animate-spin" />
            </div>
            <div className="flex-1 space-y-3 mt-1">
              <div className="flex gap-2">
                <div className="h-2 w-2 rounded-full bg-white/20 animate-pulse" />
                <div
                  className="h-2 w-2 rounded-full bg-white/20 animate-pulse"
                  style={{ animationDelay: "0.2s" }}
                />
                <div
                  className="h-2 w-2 rounded-full bg-white/20 animate-pulse"
                  style={{ animationDelay: "0.4s" }}
                />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  );
}
