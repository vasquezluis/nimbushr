"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import {
  FileText,
  X,
  ChevronRight,
  ChevronLeft,
  FileIcon,
  Loader2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useFiles, useFileUrl } from "@/hooks/use-files";
import { FileInfo } from "@/types/files";
import { PDFViewer } from "@/components/pdf-viewer";

interface DocumentPanelProps {
  selectedDocument: string | null;
  onSelectDocument: (docId: string | null) => void;
}

export function DocumentPanel({
  selectedDocument,
  onSelectDocument,
}: DocumentPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Fetch files using React Query
  const { data, isLoading, isError, error, refetch } = useFiles();

  // Get PDF URL for selected document
  const pdfUrl = useFileUrl(selectedDocument);

  // Format file size (backend doesn't return size, so we'll calculate from chunks)
  const formatFileStats = (file: FileInfo) => {
    return {
      chunkInfo: `${file.chunk_count} chunks`,
      aiSummary:
        file.ai_summarized_chunks > 0
          ? `${file.ai_summarized_chunks} AI-summarized`
          : null,
    };
  };

  if (isCollapsed) {
    return (
      <div className="w-12 border-l border-white/5 bg-[#0F0F0F] flex flex-col items-center py-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(false)}
          className="h-10 w-10 rounded-lg hover:bg-white/10"
        >
          <ChevronLeft className="h-5 w-5 text-white/60" />
        </Button>
        <div className="mt-4 writing-mode-vertical text-xs text-white/40 font-medium rotate-180">
          Documents
        </div>
      </div>
    );
  }

  return (
    <div className="w-130 border-l border-white/5 bg-[#0F0F0F] flex flex-col">
      {/* Header */}
      <div className="border-b border-white/5 p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-white/5 border border-white/10">
              <FileText className="h-4 w-4 text-white/60" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white/90">Documents</h2>
              <p className="text-xs text-white/40">
                {isLoading
                  ? "Loading..."
                  : data
                    ? `${data.total_files} files loaded`
                    : "No files"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => refetch()}
              disabled={isLoading}
              className="h-8 w-8 rounded-lg hover:bg-white/10"
              title="Refresh files"
            >
              <RefreshCw
                className={`h-4 w-4 text-white/60 ${isLoading ? "animate-spin" : ""}`}
              />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsCollapsed(true)}
              className="h-8 w-8 rounded-lg hover:bg-white/10"
            >
              <ChevronRight className="h-4 w-4 text-white/60" />
            </Button>
          </div>
        </div>
      </div>

      {/* Document List or PDF Viewer */}
      {!selectedDocument ? (
        <ScrollArea className="flex-1 p-3">
          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-12 space-y-3">
              <Loader2 className="h-8 w-8 text-white/40 animate-spin" />
              <p className="text-sm text-white/40">Loading documents...</p>
            </div>
          )}

          {/* Error State */}
          {isError && (
            <div className="flex flex-col items-center justify-center py-12 space-y-3">
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
                <AlertCircle className="h-8 w-8 text-red-400" />
              </div>
              <div className="text-center space-y-1">
                <p className="text-sm font-medium text-white/90">
                  Failed to load documents
                </p>
                <p className="text-xs text-white/40">
                  {error?.message || "Unknown error"}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                className="mt-2"
              >
                <RefreshCw className="h-3 w-3 mr-2" />
                Try Again
              </Button>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !isError && data?.files.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 space-y-3">
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <FileText className="h-8 w-8 text-white/40" />
              </div>
              <div className="text-center space-y-1">
                <p className="text-sm font-medium text-white/90">
                  No documents found
                </p>
                <p className="text-xs text-white/40">
                  Upload documents to get started
                </p>
              </div>
            </div>
          )}

          {/* Documents List */}
          {!isLoading && !isError && data && data.files.length > 0 && (
            <div className="space-y-2">
              {data.files.map((file) => {
                const stats = formatFileStats(file);
                return (
                  <button
                    key={file.filename}
                    onClick={() => onSelectDocument(file.filename)}
                    className="w-full text-left p-3 rounded-xl cursor-pointer bg-white/5 border border-white/10 hover:bg-white/8 hover:border-white/15 transition-all duration-200 group"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-white/10 group-hover:bg-white/15 transition-colors">
                        <FileIcon className="h-4 w-4 text-white/60" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-white/90 truncate mb-1">
                          {file.filename}
                        </h3>
                        <div className="flex items-center gap-2 flex-wrap mb-2">
                          <Badge
                            variant="outline"
                            className="text-xs bg-blue-500/10 border-blue-500/30 text-blue-300"
                          >
                            {stats.chunkInfo}
                          </Badge>
                          {file.has_tables && (
                            <Badge
                              variant="outline"
                              className="text-xs bg-green-500/10 border-green-500/30 text-green-300"
                            >
                              Tables
                            </Badge>
                          )}
                          {file.has_images && (
                            <Badge
                              variant="outline"
                              className="text-xs bg-purple-500/10 border-purple-500/30 text-purple-300"
                            >
                              Images
                            </Badge>
                          )}
                        </div>
                        {stats.aiSummary && (
                          <p className="text-xs text-white/40">
                            {stats.aiSummary}
                          </p>
                        )}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </ScrollArea>
      ) : (
        /* PDF Viewer */
        <div className="flex-1 flex flex-col min-h-0">
          {/* Viewer Header */}
          <div className="border-b border-white/5 p-3 flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-white/90 truncate">
                {selectedDocument}
              </h3>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onSelectDocument(null)}
              className="h-8 w-8 rounded-lg hover:bg-white/10 shrink-0"
            >
              <X className="h-4 w-4 text-white/60" />
            </Button>
          </div>

          {/* PDF Content */}
          <div className="flex-1 overflow-hidden min-h-0">
            {pdfUrl ? (
              <PDFViewer fileUrl={pdfUrl} filename={selectedDocument} />
            ) : (
              <div className="flex items-center justify-center h-full bg-white/5">
                <div className="text-center p-8">
                  <FileText className="h-16 w-16 mx-auto text-white/40 mb-4" />
                  <p className="text-white/60 text-sm mb-2">PDF Viewer</p>
                  <p className="text-white/40 text-xs">Loading document...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer Stats */}
      {!selectedDocument && data && (
        <div className="border-t border-white/5 p-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-white/40">Total chunks</span>
            <span className="text-white/60 font-medium">
              {data.total_chunks}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
