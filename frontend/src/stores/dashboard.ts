import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { getStatsBySource, getPipelineRuns } from "@/api/endpoints";
import type { StatsBySource, PipelineRun } from "@/types";

export const useDashboardStore = defineStore("dashboard", () => {
  const stats = ref<StatsBySource[]>([]);
  const runs = ref<PipelineRun[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const totalArticles = computed(() => stats.value.reduce((s, x) => s + x.cnt, 0));
  const sourceCount = computed(() => stats.value.length);
  const lastRunStatus = computed(() => runs.value[0]?.status ?? "N/A");
  const lastRunColor = computed(() => {
    const s = runs.value[0]?.status;
    return s === "success" ? "green" : s === "failed" ? "" : "amber";
  });
  const dqAvgScore = computed(() => {
    const score = runs.value[0]?.dq_avg_score;
    return score != null ? score.toFixed(1) : "-";
  });

  async function fetchDashboardData() {
    loading.value = true;
    error.value = null;
    try {
      const [s, r] = await Promise.all([getStatsBySource(), getPipelineRuns(5)]);
      stats.value = s;
      runs.value = r;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "加载仪表盘数据失败";
    } finally {
      loading.value = false;
    }
  }

  return {
    stats, runs, loading, error,
    totalArticles, sourceCount, lastRunStatus, lastRunColor, dqAvgScore,
    fetchDashboardData,
  };
});
