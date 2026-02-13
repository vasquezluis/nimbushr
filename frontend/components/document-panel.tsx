"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { FileText, X, ChevronRight, ChevronLeft, FileIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface Document {
  id: string;
  name: string;
  path: string;
  size: string;
  chunks: number;
  lastModified: Date;
}

interface DocumentPanelProps {
  selectedDocument: string | null;
  onSelectDocument: (docId: string | null) => void;
}

export function DocumentPanel({
  selectedDocument,
  onSelectDocument,
}: DocumentPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Mock documents - TODO: Fetch from your RAG system
  const documents: Document[] = [
    {
      id: "1",
      name: "employee_handbook.pdf",
      path: "/docs/employee_handbook.pdf",
      size: "2.4 MB",
      chunks: 45,
      lastModified: new Date(2024, 0, 15),
    },
    {
      id: "2",
      name: "benefits_guide.pdf",
      path: "/docs/benefits_guide.pdf",
      size: "1.8 MB",
      chunks: 32,
      lastModified: new Date(2024, 0, 20),
    },
    {
      id: "3",
      name: "remote_work_policy.pdf",
      path: "/docs/remote_work_policy.pdf",
      size: "890 KB",
      chunks: 18,
      lastModified: new Date(2024, 1, 1),
    },
    {
      id: "4",
      name: "performance_review.pdf",
      path: "/docs/performance_review.pdf",
      size: "1.2 MB",
      chunks: 24,
      lastModified: new Date(2024, 1, 10),
    },
  ];

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
    <div className="w-96 border-l border-white/5 bg-[#0F0F0F] flex flex-col">
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
                {documents.length} files loaded
              </p>
            </div>
          </div>
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

      {/* Document List */}
      {!selectedDocument ? (
        <ScrollArea className="flex-1 p-3">
          <div className="space-y-2">
            {documents.map((doc) => (
              <button
                key={doc.id}
                onClick={() => onSelectDocument(doc.id)}
                className="w-full text-left p-3 rounded-xl cursor-pointer bg-white/5 border border-white/10 hover:bg-white/8 hover:border-white/15 transition-all duration-200 group"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-white/10 group-hover:bg-white/15 transition-colors">
                    <FileIcon className="h-4 w-4 text-white/60" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-white/90 truncate mb-1">
                      {doc.name}
                    </h3>
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge
                        variant="outline"
                        className="text-xs bg-white/5 border-white/10 text-white/50"
                      >
                        {doc.size}
                      </Badge>
                      <Badge
                        variant="outline"
                        className="text-xs bg-blue-500/10 border-blue-500/30 text-blue-300"
                      >
                        {doc.chunks} chunks
                      </Badge>
                    </div>
                    <p className="text-xs text-white/30 mt-1">
                      Modified {doc.lastModified.toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </ScrollArea>
      ) : (
        /* PDF Viewer */
        <div className="flex-1 flex flex-col">
          {/* Viewer Header */}
          <div className="border-b border-white/5 p-3 flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-white/90 truncate">
                {documents.find((d) => d.id === selectedDocument)?.name}
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
          <div className="flex-1 bg-white/5 p-4 overflow-auto">
            <div className="bg-white rounded-lg shadow-2xl min-h-full flex items-center justify-center">
              {/* TODO: Integrate actual PDF viewer */}
              <div className="text-center p-8">
                <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 text-sm mb-2">PDF Viewer</p>
                <p className="text-gray-400 text-xs">
                  Integrate react-pdf or pdf.js here
                </p>
                <p className="text-gray-400 text-xs mt-4">
                  File: {documents.find((d) => d.id === selectedDocument)?.name}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer Stats */}
      <div className="border-t border-white/5 p-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-white/40">Total chunks</span>
          <span className="text-white/60 font-medium">
            {documents.reduce((acc, doc) => acc + doc.chunks, 0)}
          </span>
        </div>
      </div>
    </div>
  );
}
