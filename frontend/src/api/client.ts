import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 30000,
});

export interface Source {
  source: string;
  page_num: number;
  text: string;
  rerank_score: number | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  timestamp: Date;
}

export async function uploadPDF(file: File): Promise<{ chunks_created: number; filename: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function getIndexStatus() {
  const response = await apiClient.get("/documents/status");
  return response.data;
}
