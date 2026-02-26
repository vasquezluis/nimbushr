"use client";

import { Download, FileSpreadsheet } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ExcelViewerProps {
  fileUrl: string;
  filename: string;
}

export function ExcelViewer({ fileUrl, filename }: ExcelViewerProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full space-y-4 p-8">
      <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
        <FileSpreadsheet className="h-12 w-12 text-green-400" />
      </div>
      <div className="text-center space-y-1">
        <p className="text-sm font-medium text-white/90">{filename}</p>
        <p className="text-xs text-white/40">
          Excel files can't be previewed in the browser.
          <br />
          Download it to view in your spreadsheet app.
        </p>
      </div>
      <Button
        asChild
        className="bg-green-500/20 hover:bg-green-500/30 border border-green-500/30 text-green-300"
      >
        <a href={fileUrl} download={filename}>
          <Download className="h-4 w-4 mr-2" />
          Download {filename}
        </a>
      </Button>
    </div>
  );
}
