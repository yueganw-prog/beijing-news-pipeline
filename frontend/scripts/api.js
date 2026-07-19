const API = location.protocol === "file:" ? "http://localhost:8000" : "/api";

async function fetchJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`API error: ${r.status}`);
  return r.json();
}

export function getArticles(params = {}) {
  const q = new URLSearchParams();
  if (params.source) q.set("source", params.source);
  if (params.category) q.set("category", params.category);
  if (params.limit) q.set("limit", params.limit);
  if (params.offset) q.set("offset", params.offset);
  if (params.search) q.set("q", params.search);
  const endpoint = params.search ? "/articles/search" : "/articles";
  return fetchJSON(`${API}${endpoint}?${q}`);
}

export function getArticle(id) {
  return fetchJSON(`${API}/articles/${id}`);
}

export function getStatsBySource() {
  return fetchJSON(`${API}/stats/by-source`);
}

export function getPipelineRuns(limit = 5) {
  return fetchJSON(`${API}/pipeline-runs?limit=${limit}`);
}

export function getDQResults(limit = 5) {
  return fetchJSON(`${API}/dq-results?limit=${limit}`);
}
