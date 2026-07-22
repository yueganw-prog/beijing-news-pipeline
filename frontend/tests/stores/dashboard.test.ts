import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useDashboardStore } from "@/stores/dashboard";
import type { StatsBySource, PipelineRun } from "@/types";

const { mockStats, mockRuns } = vi.hoisted(() => ({
  mockStats: [
    { source: "36氪", category: "tech", cnt: 100, last_fetched: "2026-07-20T00:00:00Z" },
    { source: "新浪财经", category: "finance", cnt: 200, last_fetched: "2026-07-20T00:00:00Z" },
  ] as StatsBySource[],
  mockRuns: [
    {
      id: 1, dag_id: "test", dag_run_id: "r1", run_date: "2026-07-20",
      status: "success", total_articles: 50, dq_avg_score: 95.5,
      started_at: "2026-07-20T00:00:00Z", finished_at: "2026-07-20T00:05:00Z",
    },
  ] as PipelineRun[],
}));

vi.mock("@/api/endpoints", () => ({
  getStatsBySource: vi.fn().mockResolvedValue(mockStats),
  getPipelineRuns: vi.fn().mockResolvedValue(mockRuns),
}));

describe("dashboard store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("has empty initial state", () => {
    const store = useDashboardStore();
    expect(store.stats).toEqual([]);
    expect(store.runs).toEqual([]);
    expect(store.loading).toBe(false);
  });

  it("fetchDashboardData populates stats and runs", async () => {
    const store = useDashboardStore();
    await store.fetchDashboardData();
    expect(store.stats).toEqual(mockStats);
    expect(store.runs).toEqual(mockRuns);
    expect(store.loading).toBe(false);
  });

  it("totalArticles sums all source counts", async () => {
    const store = useDashboardStore();
    await store.fetchDashboardData();
    expect(store.totalArticles).toBe(300);
  });

  it("sourceCount returns number of unique sources", async () => {
    const store = useDashboardStore();
    await store.fetchDashboardData();
    expect(store.sourceCount).toBe(2);
  });

  it("lastRunStatus returns first run status", async () => {
    const store = useDashboardStore();
    await store.fetchDashboardData();
    expect(store.lastRunStatus).toBe("success");
  });

  it("dqAvgScore formats to 1 decimal", async () => {
    const store = useDashboardStore();
    await store.fetchDashboardData();
    expect(store.dqAvgScore).toBe("95.5");
  });
});
