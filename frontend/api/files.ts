import { api } from "@/lib/api";
import { FilesListResponse, FileChunksResponse } from "@/types/files";

/**
 * Files API Service
 * Handles all file-related API calls
 */
export const filesApi = {
  /**
   * Get list of all loaded files
   */
  getFiles: async (): Promise<FilesListResponse> => {
    const response = await api.get<FilesListResponse>("/files");
    return response.data;
  },

  /**
   * Get a specific PDF file
   */
  getFile: async (filename: string): Promise<Blob> => {
    const response = await api.get(`/files/${filename}`, {
      responseType: "blob",
    });
    return response.data;
  },

  /**
   * Get all chunks for a specific file
   */
  getFileChunks: async (filename: string): Promise<FileChunksResponse> => {
    const response = await api.get<FileChunksResponse>(
      `/files/${filename}/chunks`,
    );
    return response.data;
  },

  /**
   * Get file URL for viewing
   */
  getFileUrl: (filename: string): string => {
    const baseURL =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    return `${baseURL}/files/${filename}`;
  },
};
