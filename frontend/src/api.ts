// api.ts — Railway backend client

const BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

async function req<T>(path: string, opts?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${path}`, opts);
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(err.detail || `HTTP ${r.status}`);
  }
  return r.json();
}

export const api = {
  // Health
  health: () => req<any>("/api/health"),

  // Media
  listMedia:   () => req<string[]>("/api/media"),
  deleteMedia: (f: string) => req<any>(`/api/media/${encodeURIComponent(f)}`, { method: "DELETE" }),
  uploadMedia: (files: File[]) => {
    const fd = new FormData();
    files.forEach(f => fd.append("files", f));
    return req<any>("/api/upload/media", { method: "POST", body: fd });
  },

  // Music
  listMusic:   () => req<string[]>("/api/music"),
  uploadMusic: (file: File) => {
    const fd = new FormData(); fd.append("file", file);
    return req<any>("/api/upload/music", { method: "POST", body: fd });
  },

  // Logo
  uploadLogo: (file: File) => {
    const fd = new FormData(); fd.append("file", file);
    return req<any>("/api/upload/logo", { method: "POST", body: fd });
  },

  // Vision analysis
  analyzeMedia: (filenames: string[], api_key: string) =>
    req<any[]>("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filenames, api_key }),
    }),

  // Generate
  startGeneration: (payload: Record<string, any>) =>
    req<{ job_id: string }>("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  // Jobs
  getJob:   (id: string) => req<any>(`/api/jobs/${id}`),
  listJobs: () => req<any[]>("/api/jobs"),

  // Output
  listOutput: () => req<string[]>("/api/output"),

  // URLs
  mediaUrl:  (f: string) => `${BASE}/media/${encodeURIComponent(f)}`,
  outputUrl: (f: string) => `${BASE}/output/${encodeURIComponent(f)}`,
  musicUrl:  (f: string) => `${BASE}/music/${encodeURIComponent(f)}`,
};
