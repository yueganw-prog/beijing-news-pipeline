<template>
  <nav class="sidebar" :class="{ open: mobileOpen }" role="navigation" aria-label="主导航">
    <div class="sidebar-logo">
      <h1>Beijing News Pipeline</h1>
      <span>新闻聚合管道</span>
    </div>

    <!-- Overview -->
    <div class="nav-group">
      <div class="nav-group-label">概览</div>
      <RouterLink
        class="nav-item"
        :class="{ active: route.name === 'dashboard' }"
        to="/"
        @click="$emit('closeMobile')"
      >
        <BaseIcon name="dashboard" /> 仪表盘
      </RouterLink>
      <RouterLink
        class="nav-item"
        :class="{ active: route.name === 'articles' && !articlesStore.category }"
        to="/articles"
        @click="$emit('closeMobile')"
      >
        <BaseIcon name="newspaper" /> 文章列表
      </RouterLink>
    </div>

    <!-- Categories -->
    <div class="nav-group">
      <div class="nav-group-label">分类</div>
      <RouterLink
        v-for="cat in categories"
        :key="cat.key"
        class="nav-item"
        :class="{ active: route.name === 'articles' && route.query.category === cat.key }"
        :to="{ name: 'articles', query: { category: cat.key } }"
        @click="articlesStore.setCategory(cat.key); $emit('closeMobile')"
      >
        <BaseIcon :name="cat.icon" :style="{ color: cat.color }" />
        {{ cat.label }}
        <span class="nav-badge">{{ badgeCounts[cat.key] ?? "-" }}</span>
      </RouterLink>
    </div>

    <!-- Footer -->
    <div class="sidebar-footer">
      <div style="display:flex;align-items:center;gap:6px">
        <BaseIcon name="database" :size="12" />
        <span v-if="isDemo">演示模式</span>
        <span v-else>API: localhost:8000</span>
      </div>
      <div style="margin-top:8px">
        <ThemeToggle />
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { useDashboardStore } from "@/stores/dashboard";
import { useArticlesStore } from "@/stores/articles";
import { CATEGORIES } from "@/utils/constants";
import BaseIcon from "@/components/common/BaseIcon.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";

defineProps<{ mobileOpen?: boolean }>();
defineEmits<{ closeMobile: [] }>();

const route = useRoute();
const dashboard = useDashboardStore();
const articlesStore = useArticlesStore();
const categories = CATEGORIES;

const isDemo = computed(() => import.meta.env.VITE_MOCK_MODE === "true" || !window.location.hostname.includes("localhost"));

const badgeCounts = computed(() => {
  const counts: Record<string, number> = { tech: 0, finance: 0, local: 0 };
  dashboard.stats.forEach((s) => {
    if (s.category in counts) counts[s.category] += s.cnt;
  });
  return counts;
});
</script>
