"use client";

import { AlertCircle, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { MarkdownRenderer } from "./markdown-renderer";

interface TextViewerProps {
  fileUrl: string;
  filename: string;
}

export function TextViewer({ fileUrl, filename }: TextViewerProps) {
  const [content, setContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isMarkdown = filename.toLowerCase().endsWith(".md");

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    setContent(null);

    fetch(fileUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.text();
      })
      .then((text) => setContent(text))
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [fileUrl]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-3">
        <Loader2 className="h-8 w-8 text-white/40 animate-spin" />
        <p className="text-sm text-white/40">Loading file...</p>
      </div>
    );
  }

  if (content == null) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-3">
        <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
          <AlertCircle className="h-8 w-8 text-yellow-400" />
        </div>
        <p className="text-sm font-medium text-white/90">File is empty</p>
        <p className="text-xs text-white/40">{error}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-3">
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
          <AlertCircle className="h-8 w-8 text-red-400" />
        </div>
        <p className="text-sm font-medium text-white/90">Failed to load file</p>
        <p className="text-xs text-white/40">{error}</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-[#0F0F0F] p-4">
      <pre
        className={`
          whitespace-pre-wrap wrap-break-words text-sm leading-relaxed
          font-mono text-white/80
          ${isMarkdown ? "font-sans" : ""}
        `}
      >
        <MarkdownRenderer content={content} />
      </pre>
    </div>
  );
}
