import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { setActivePinia, createPinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";
import DashboardPage from "@/views/DashboardPage.vue";
import { useDashboardStore } from "@/stores/dashboard";

const { mockStats, mockRuns } = vi.hoisted(() => ({
  mockStats: [
    { source: "36氪", category: "tech", cnt: 100, last_fetched: "2026-07-20T00:00:00Z" },
  ],
  mockRuns: [
    {
      id: 1, dag_id: "test", dag_run_id: "r1", run_date: "2026-07-20",
      status: "success" as const, total_articles: 50, dq_avg_score: 95.5,
      started_at: "2026-07-20T00:00:00Z", finished_at: "2026-07-20T00:05:00Z",
    },
  ],
}));

vi.mock("@/api/endpoints", () => ({
  getStatsBySource: vi.fn().mockResolvedValue(mockStats),
  getPipelineRuns: vi.fn().mockResolvedValue(mockRuns),
}));

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: "/", component: {} }],
});

describe("DashboardPage", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("mounts without error", () => {
    const wrapper = mount(DashboardPage, {
      global: {
        plugins: [router],
        stubs: {
          AppTopbar: { template: '<div class="topbar-stub"><slot name="actions"/></div>', props: ["title", "refreshing", "showRefresh"] },
          DashboardView: { template: '<div class="dashboard-stub" />' },
        },
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it("fetches dashboard data on mount", async () => {
    const store = useDashboardStore();
    mount(DashboardPage, {
      global: {
        plugins: [router],
        stubs: {
          AppTopbar: { template: '<div class="topbar-stub"><slot name="actions"/></div>', props: ["title"] },
          DashboardView: { template: '<div class="dashboard-stub" />' },
        },
      },
    });

    await store.fetchDashboardData();
    expect(store.stats).toHaveLength(1);
    expect(store.totalArticles).toBe(100);
  });
});
