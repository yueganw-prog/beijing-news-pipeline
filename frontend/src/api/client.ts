import type { ApiError } from "@/types";

const TIMEOUT_MS = 5000;

export class ApiClientError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
  }
}

async function tryFetch<T>(url: string, signal?: AbortSignal): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  // If an external signal is provided, forward its abort
  if (signal) {
    signal.addEventListener("abort", () => controller.abort());
  }

  try {
    const r = await fetch(url, { signal: controller.signal });
    if (!r.ok) {
      const text = await r.text().catch(() => "");
      throw new ApiClientError(r.status, text || `HTTP ${r.status}`);
    }
    return (await r.json()) as T;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Fetch with automatic mock fallback.
 * - If VITE_MOCK_MODE is "true" or the API is unreachable, falls back to mock data.
 * - The mockFallback function is only called when needed.
 */
export async function fetchWithFallback<T>(
  url: string,
  mockFallback: () => T,
  signal?: AbortSignal,
): Promise<T> {
  // If explicitly in mock mode, skip the fetch entirely
  if (import.meta.env.VITE_MOCK_MODE === "true") {
    return mockFallback();
  }

  try {
    return await tryFetch<T>(url, signal);
  } catch (err) {
    // Network errors (offline, timeout, CORS) → fall back
    if (err instanceof TypeError || err instanceof DOMException) {
      console.info("[API] Network unreachable, using mock data for:", url);
      return mockFallback();
    }
    // Pass through ApiClientErrors (the API IS reachable but returned an error)
    throw err;
  }
}
