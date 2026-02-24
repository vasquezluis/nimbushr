import { type UseQueryResult, useQuery } from "@tanstack/react-query";
import { filesApi } from "@/api/files";
import type { FileChunksResponse, FilesListResponse } from "@/types/files";

/**
 * Query keys for files
 */
export const filesKeys = {
  all: ["files"] as const,
  lists: () => [...filesKeys.all, "list"] as const,
  list: () => [...filesKeys.lists()] as const,
  file: (filename: string) => [...filesKeys.all, "file", filename] as const,
  chunks: (filename: string) => [...filesKeys.all, "chunks", filename] as const,
};

/**
 * Hook to fetch all loaded files
 */
export function useFiles(): UseQueryResult<FilesListResponse, Error> {
  return useQuery({
    queryKey: filesKeys.list(),
    queryFn: filesApi.getFiles,
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep unused data in cache for 10 minutes
    retry: 2,
  });
}

/**
 * Hook to fetch chunks for a specific file
 */
export function useFileChunks(
  filename: string | null,
): UseQueryResult<FileChunksResponse, Error> {
  return useQuery({
    queryKey: filesKeys.chunks(filename || ""),
    queryFn: () => filesApi.getFileChunks(filename as string),
    enabled: !!filename,
    staleTime: 10 * 60 * 1000, // Consider data fresh for 10 minutes
    retry: 2,
  });
}

/**
 * Hook to get file URL
 */
export function useFileUrl(filename: string | null): string | null {
  if (!filename) return null;
  return filesApi.getFileUrl(filename);
}
