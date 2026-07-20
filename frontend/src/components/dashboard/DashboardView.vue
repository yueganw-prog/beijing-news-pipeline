<template>
  <div class="view-wrapper">
    <!-- Demo banner -->
    <div v-if="isDemo" class="demo-banner">
      <BaseIcon name="database" :size="12" />
      演示模式 — 显示模拟数据 · 后端 API 不可用时自动启用
    </div>

    <!-- Error state -->
    <ErrorState
      v-if="error"
      :message="error"
      @retry="dashboard.fetchDashboardData()"
    />

    <!-- Content -->
    <div class="content" v-else>
      <div class="content-inner">
        <!-- Stats row -->
        <SkeletonGrid v-if="loading" :count="4" item-height="100px" />
        <div v-else class="stats-row">
          <StatsCard label="文章总数" :value="dashboard.totalArticles.toLocaleString()" color="blue" />
          <StatsCard label="新闻源" :value="dashboard.sourceCount" />
          <StatsCard
            label="最近运行"
            :value="dashboard.lastRunStatus"
            :color="dashboard.lastRunColor"
          />
          <StatsCard label="DQ 均分" :value="dashboard.dqAvgScore" color="green" />
        </div>

        <!-- Source breakdown -->
        <div class="section-title">按来源统计</div>
        <SkeletonGrid v-if="loading" :count="6" :columns="3" item-height="110px" />
        <SourceCardGrid v-else-if="dashboard.stats.length" :stats="dashboard.stats" />
        <EmptyState v-else message="暂无来源数据" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useDashboardStore } from "@/stores/dashboard";
import StatsCard from "@/components/common/StatsCard.vue";
import SkeletonGrid from "@/components/common/SkeletonGrid.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import ErrorState from "@/components/common/ErrorState.vue";
import BaseIcon from "@/components/common/BaseIcon.vue";
import SourceCardGrid from "./SourceCardGrid.vue";

const dashboard = useDashboardStore();
const loading = computed(() => dashboard.loading);
const error = computed(() => dashboard.error);

const isDemo = computed(
  () => import.meta.env.VITE_MOCK_MODE === "true" || !window.location.hostname.includes("localhost"),
);

onMounted(() => {
  if (!dashboard.stats.length) {
    dashboard.fetchDashboardData();
  }
});
</script>
