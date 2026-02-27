import type { GraphNode } from "@/types/query";

interface Source {
  file: string;
  chunk_index: number;
  has_tables: boolean;
  has_images: boolean;
  ai_summarized: boolean;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Source[];
  graphTraversal?: GraphNode[];
  isStreaming?: boolean;
  isTruncated?: boolean;
}

export interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  status?: string | null;
}

export interface MessageBubbleProps {
  message: Message;
  isLatest?: boolean;
}

export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  onCancel?: () => void;
  rateLimitedUntil?: number | null;
}

export interface MarkdownRendererProps {
  content: string;
  className?: string;
}
