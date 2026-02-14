/**
 * File metadata from the RAG system
 */
export interface FileInfo {
  filename: string;
  source_type: string;
  chunk_count: number;
  has_tables: boolean;
  has_images: boolean;
  ai_summarized_chunks: number;
}

/**
 * Response from the /files endpoint
 */
export interface FilesListResponse {
  files: FileInfo[];
  total_files: number;
  total_chunks: number;
}

/**
 * Individual chunk information
 */
export interface ChunkInfo {
  chunk_index: number;
  content_preview: string;
  content_length: number;
  has_tables: boolean;
  has_images: boolean;
  num_tables: number;
  num_images: number;
  ai_summarized: boolean;
  content_types: string;
  text_preview: string;
}

/**
 * Response from the /files/{filename}/chunks endpoint
 */
export interface FileChunksResponse {
  filename: string;
  total_chunks: number;
  chunks: ChunkInfo[];
}
