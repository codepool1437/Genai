// Central API client — all pages import from here instead of calling Supabase directly.
// In Review 1: points to our local FastAPI backend (http://localhost:8000)
// In Review 2: same URL, just the backend gains real ChromaDB + embeddings

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// ── Helpers ───────────────────────────────────────────────────────────────────

export function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

/** GET, returns parsed JSON response */
export async function apiGet<T = unknown>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path));
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail ?? err.error ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

/** POST JSON, returns parsed JSON response */
export async function apiPost<T = unknown>(path: string, body: unknown): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail ?? err.error ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

/** POST multipart form data, returns parsed JSON response */
export async function apiPostForm<T = unknown>(path: string, form: FormData): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail ?? err.error ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

/** POST JSON, returns a ReadableStream for SSE streaming responses */
export async function apiStream(path: string, body: unknown): Promise<ReadableStream<Uint8Array>> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail ?? err.error ?? "Request failed");
  }
  if (!res.body) throw new Error("No response body");
  return res.body;
}
