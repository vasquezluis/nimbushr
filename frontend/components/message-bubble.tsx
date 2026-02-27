"use client";

import { format } from "date-fns";
import { AlertCircle, Bot, User } from "lucide-react";
import { GraphTraversal } from "@/components/graph-traversal";
import { MarkdownRenderer } from "@/components/markdown-renderer";
import type { MessageBubbleProps } from "@/types/chat";

import { Sources } from "./Sources";

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-4 ${isUser ? "flex-row-reverse" : "flex-row"} group animate-in fade-in slide-in-from-bottom-4 duration-500`}
    >
      {/* Avatar */}
      <div
        className={`
        w-8 h-8 rounded-full flex items-center justify-center -shrink-0
        ${
          isUser
            ? "bg-linear-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30"
            : "bg-linear-to-br from-white/10 to-white/5 border border-white/10"
        }
      `}
      >
        {isUser ? (
          <User className="h-4 w-4 text-blue-400" />
        ) : (
          <Bot className="h-4 w-4 text-white/60" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={`flex-1 space-y-2 ${isUser ? "items-end" : "items-start"} flex flex-col max-w-2xl`}
      >
        {/* Message Bubble */}
        <div
          className={`
          rounded-2xl px-5 py-3.5 relative
          ${
            isUser
              ? "bg-linear-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 ml-auto"
              : "bg-white/5 border border-white/10 backdrop-blur-sm"
          }
        `}
        >
          {isUser ? (
            <p className="text-white/90 text-[15px] leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          ) : (
            <div className="text-[15px] leading-relaxed">
              <MarkdownRenderer content={message.content} />
            </div>
          )}
          {/* Streaming Indicator */}
          {message.isStreaming && (
            <div className="mt-2 flex items-center gap-1">
              <div className="w-1.5 h-1.5 bg-white/40 rounded-full animate-pulse" />
              <div
                className="w-1.5 h-1.5 bg-white/40 rounded-full animate-pulse"
                style={{ animationDelay: "0.2s" }}
              />
              <div
                className="w-1.5 h-1.5 bg-white/40 rounded-full animate-pulse"
                style={{ animationDelay: "0.4s" }}
              />
            </div>
          )}
          {!message.isStreaming && message.isTruncated && (
            <div className="mt-2 flex items-center gap-1.5 text-xs text-amber-400/80">
              <AlertCircle className="h-3.5 w-3.5 shrink-0" />
              <span>
                Response was cut off — try asking a more specific question.
              </span>
            </div>
          )}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <Sources sources={message.sources} />
        )}

        {message.graphTraversal && message.graphTraversal.length > 0 && (
          <GraphTraversal nodes={message.graphTraversal} />
        )}

        {/* Timestamp */}
        <p className="text-xs text-white/30 px-1">
          {format(message.timestamp, "HH:mm")}
        </p>
      </div>
    </div>
  );
}
