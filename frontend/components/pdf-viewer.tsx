"use client";

import {
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Loader2,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { Button } from "@/components/ui/button";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerProps {
  fileUrl: string;
  filename: string;
}

export function PDFViewer({ fileUrl }: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setIsLoading(false);
    setError(null);
  }

  function onDocumentLoadError(error: Error) {
    console.error("Error loading PDF:", error);
    setError(error.message || "Failed to load PDF");
    setIsLoading(false);
  }

  function changePage(offset: number) {
    setPageNumber((prevPageNumber) => {
      const newPage = prevPageNumber + offset;
      return Math.min(Math.max(1, newPage), numPages);
    });
  }

  function previousPage() {
    changePage(-1);
  }

  function nextPage() {
    changePage(1);
  }

  function zoomIn() {
    setScale((prevScale) => Math.min(prevScale + 0.2, 3.0));
  }

  function zoomOut() {
    setScale((prevScale) => Math.max(prevScale - 0.2, 0.5));
  }

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Controls */}
      <div className="flex items-center justify-between p-3 border-b border-white/5 bg-[#0A0A0A]">
        {/* Page Navigation */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={previousPage}
            disabled={pageNumber <= 1 || isLoading}
            className="h-7 w-7"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>

          <div className="text-xs text-white/60 font-mono min-w-20 text-center">
            {isLoading ? (
              <span>Loading...</span>
            ) : error ? (
              <span className="text-red-400">Error</span>
            ) : (
              <span>
                {pageNumber} / {numPages}
              </span>
            )}
          </div>

          <Button
            variant="ghost"
            size="icon-sm"
            onClick={nextPage}
            disabled={pageNumber >= numPages || isLoading}
            className="h-7 w-7"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={zoomOut}
            disabled={scale <= 0.5 || isLoading}
            className="h-7 w-7"
            title="Zoom out"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>

          <div className="text-xs text-white/60 font-mono min-w-12.5 text-center">
            {Math.round(scale * 100)}%
          </div>

          <Button
            variant="ghost"
            size="icon-sm"
            onClick={zoomIn}
            disabled={scale >= 3.0 || isLoading}
            className="h-7 w-7"
            title="Zoom in"
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* PDF Document */}
      <div className="flex-1 overflow-auto bg-[#1A1A1A] p-4 min-h-0">
        {error ? (
          <div className="flex flex-col items-center justify-center h-full space-y-3">
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
              <AlertCircle className="h-8 w-8 text-red-400" />
            </div>
            <div className="text-center space-y-1">
              <p className="text-sm font-medium text-white/90">
                Failed to load PDF
              </p>
              <p className="text-xs text-white/40">{error}</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <Document
              file={fileUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <div className="flex flex-col items-center justify-center py-12 space-y-3">
                  <Loader2 className="h-8 w-8 text-white/40 animate-spin" />
                  <p className="text-sm text-white/40">Loading PDF...</p>
                </div>
              }
              className="flex justify-center"
            >
              <Page
                pageNumber={pageNumber}
                // width={containerWith}
                scale={scale}
                loading={
                  <div className="bg-white/5 border border-white/10 rounded-lg w-75 h-100 flex items-center justify-center">
                    <Loader2 className="h-6 w-6 text-white/40 animate-spin" />
                  </div>
                }
                renderTextLayer={true}
                renderAnnotationLayer={true}
                className="shadow-lg"
              />
            </Document>
          </div>
        )}
      </div>
    </div>
  );
}
