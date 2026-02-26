"use client";

import { AlertCircle, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

interface CsvViewerProps {
  fileUrl: string;
  filename: string;
}

function parseCsv(text: string): string[][] {
  return text
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => {
      // Simple CSV parse — handles quoted fields
      const row: string[] = [];
      let current = "";
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (ch === '"') {
          inQuotes = !inQuotes;
        } else if (ch === "," && !inQuotes) {
          row.push(current);
          current = "";
        } else {
          current += ch;
        }
      }
      row.push(current);
      return row;
    });
}

export function CsvViewer({ fileUrl }: CsvViewerProps) {
  const [rows, setRows] = useState<string[][] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    setRows(null);

    fetch(fileUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.text();
      })
      .then((text) => setRows(parseCsv(text)))
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [fileUrl]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-3">
        <Loader2 className="h-8 w-8 text-white/40 animate-spin" />
        <p className="text-sm text-white/40">Loading CSV...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-3">
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
          <AlertCircle className="h-8 w-8 text-red-400" />
        </div>
        <p className="text-sm font-medium text-white/90">Failed to load CSV</p>
        <p className="text-xs text-white/40">{error}</p>
      </div>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-sm text-white/40">No data found</p>
      </div>
    );
  }

  const [header, ...dataRows] = rows;

  return (
    <div className="h-full overflow-auto bg-[#0F0F0F] p-2">
      <table className="min-w-full text-xs border-collapse">
        <thead className="sticky top-0 bg-[#1A1A1A] z-10">
          <tr>
            {header.map((col, i) => (
              <th
                // biome-ignore lint/suspicious/noArrayIndexKey: Change for something else, instead of array index
                key={i}
                className="px-3 py-2 text-left font-semibold text-white/70 border border-white/10 whitespace-nowrap"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, ri) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: Change for something else, instead of array index
            <tr key={ri} className="hover:bg-white/5 transition-colors">
              {header.map((_, ci) => (
                <td
                  // biome-ignore lint/suspicious/noArrayIndexKey: Change for something else, instead of array index
                  key={ci}
                  className="px-3 py-1.5 text-white/60 border border-white/5 max-w-48 truncate"
                  title={row[ci] ?? ""}
                >
                  {row[ci] ?? ""}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-white/30 mt-2 px-2">
        {dataRows.length} rows · {header.length} columns
      </p>
    </div>
  );
}
