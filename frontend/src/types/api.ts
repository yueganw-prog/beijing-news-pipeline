export interface Article {
  id: number;
  source: string;
  category: "tech" | "finance" | "local" | string;
  title: string;
  url: string;
  author: string;
  summary: string;
  published_at: string | null;
  fetched_at: string;
}

export interface ArticleDetail extends Article {
  content_clean: string | null;
  content_raw?: string | null;
}

export interface StatsBySource {
  source: string;
  category: string;
  cnt: number;
  last_fetched: string;
}

export interface PipelineRun {
  id: number;
  dag_id: string;
  dag_run_id: string;
  run_date: string;
  status: string;
  total_articles: number;
  dq_avg_score: number | null;
  started_at: string;
  finished_at: string | null;
}

export interface DQResult {
  id: number;
  dag_run_id: string;
  source: string;
  category: string;
  total_rows: number;
  score: number | null;
  checked_at: string;
}

export interface ArticleQueryParams {
  source?: string;
  category?: string;
  limit?: number;
  offset?: number;
  search?: string;
}

export interface ApiError {
  status: number;
  message: string;
}
