<template>
  <div class="page">
    <AppTopbar
      title="仪表盘"
      :refreshing="dashboard.loading"
      @refresh="dashboard.fetchDashboardData()"
      @toggle-mobile="$emit('toggleMobile')"
    />
    <DashboardView />
  </div>
</template>

<script setup lang="ts">
import { useDashboardStore } from "@/stores/dashboard";
import AppTopbar from "@/components/layout/AppTopbar.vue";
import DashboardView from "@/components/dashboard/DashboardView.vue";

defineEmits<{ toggleMobile: [] }>();
const dashboard = useDashboardStore();
</script>
