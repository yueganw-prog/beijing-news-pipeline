import type { Article, ArticleDetail, StatsBySource, PipelineRun, DQResult, ArticleQueryParams } from "@/types";
import { fetchWithFallback } from "./client";
import {
  mockArticles,
  mockArticleDetail,
  mockStats,
  mockPipelineRuns,
} from "./mockData";

const BASE = "/api";

function buildQuery(params: Record<string, string | number | undefined>): string {
  const q = new URLSearchParams();
  for (const [key, val] of Object.entries(params)) {
    if (val !== undefined && val !== null && val !== "") {
      q.set(key, String(val));
    }
  }
  const qs = q.toString();
  return qs ? `?${qs}` : "";
}

export function getArticles(params: ArticleQueryParams = {}): Promise<Article[]> {
  const { search, ...rest } = params;
  if (search) {
    const q = buildQuery({ q: search, limit: rest.limit, offset: rest.offset });
    return fetchWithFallback<Article[]>(
      `${BASE}/articles/search${q}`,
      () => filterMockArticles(params),
    );
  }
  const q = buildQuery(rest);
  return fetchWithFallback<Article[]>(
    `${BASE}/articles${q}`,
    () => filterMockArticles(params),
  );
}

export function getArticle(id: number): Promise<ArticleDetail> {
  return fetchWithFallback<ArticleDetail>(
    `${BASE}/articles/${id}`,
    () => structuredClone(mockArticleDetail),
  );
}

export function getStatsBySource(): Promise<StatsBySource[]> {
  return fetchWithFallback<StatsBySource[]>(
    `${BASE}/stats/by-source`,
    () => structuredClone(mockStats),
  );
}

export function getPipelineRuns(limit = 5): Promise<PipelineRun[]> {
  return fetchWithFallback<PipelineRun[]>(
    `${BASE}/pipeline-runs?limit=${limit}`,
    () => structuredClone(mockPipelineRuns).slice(0, limit),
  );
}

export function getDQResults(limit = 5): Promise<DQResult[]> {
  return fetchWithFallback<DQResult[]>(
    `${BASE}/dq-results?limit=${limit}`,
    () => [],
  );
}

// ---- client-side filtering for mock mode ----
function filterMockArticles(params: ArticleQueryParams): Article[] {
  let items = structuredClone(mockArticles);
  if (params.category) {
    items = items.filter((a) => a.category === params.category);
  }
  if (params.source) {
    items = items.filter((a) => a.source === params.source);
  }
  if (params.search) {
    const q = params.search.toLowerCase();
    items = items.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        (a.summary || "").toLowerCase().includes(q),
    );
  }
  const offset = params.offset || 0;
  const limit = params.limit || 50;
  return items.slice(offset, offset + limit);
}
