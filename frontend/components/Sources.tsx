"use client";

import {
  Check,
  ChevronDown,
  ChevronRight,
  FileText,
  Image,
  Sparkles,
  Table,
} from "lucide-react";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";

interface Source {
  file: string;
  chunk_index: number;
  has_tables: boolean;
  has_images: boolean;
  ai_summarized: boolean;
}

interface SourcesProps {
  sources: Source[];
}

export function Sources({ sources }: SourcesProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="w-full space-y-1.5">
      {/* Collapsible header — matches GraphTraversal exactly */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center cursor-pointer gap-2 px-1 text-xs text-white/70 hover:text-white/90 transition-colors duration-150"
      >
        <FileText className="h-3.5 w-3.5" />
        <span className="font-medium">Sources</span>
        <span className="text-white/50">
          {sources.length} document{sources.length !== 1 ? "s" : ""}
        </span>
        {isOpen ? (
          <ChevronDown className="h-3 w-3 ml-auto" />
        ) : (
          <ChevronRight className="h-3 w-3 ml-auto" />
        )}
      </button>

      {/* Expanded content */}
      {isOpen && (
        <div className="space-y-1 animate-in fade-in duration-200">
          {sources.map((source, idx) => (
            <div
              // biome-ignore lint/suspicious/noArrayIndexKey: change to other index method
              key={idx}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/8 transition-colors duration-150"
            >
              <FileText className="h-3.5 w-3.5 text-white/40 shrink-0" />
              <span className="text-xs text-white/60 font-mono flex-1 truncate">
                {source.file}
              </span>
              <span>
                {idx === 0 && (
                  <Badge
                    variant="outline"
                    className="h-5 px-1.5 text-[10px] bg-green-500/10 border-green-500/30 text-green-300"
                  >
                    <Check className="h-2.5 w-2.5 mr-0.5" />
                    Best match
                  </Badge>
                )}
              </span>

              <span className="text-xs text-white/30 shrink-0">
                #{source.chunk_index}
              </span>
              <div className="flex gap-1">
                {source.ai_summarized && (
                  <Badge
                    variant="outline"
                    className="h-5 px-1.5 text-[10px] bg-purple-500/10 border-purple-500/30 text-purple-300"
                  >
                    <Sparkles className="h-2.5 w-2.5 mr-0.5" />
                    AI
                  </Badge>
                )}
                {source.has_tables && (
                  <Badge
                    variant="outline"
                    className="h-5 px-1.5 text-[10px] bg-green-500/10 border-green-500/30 text-green-300"
                  >
                    <Table className="h-2.5 w-2.5 mr-0.5" />
                  </Badge>
                )}
                {source.has_images && (
                  <Badge
                    variant="outline"
                    className="h-5 px-1.5 text-[10px] bg-blue-500/10 border-blue-500/30 text-blue-300"
                  >
                    <Image className="h-2.5 w-2.5 mr-0.5" />
                  </Badge>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
