import { createApp, ref, watch, onMounted } from "vue";
import { Sidebar, Dashboard, Articles } from "./components.js";
import { getStatsBySource } from "./api.js";

const app = createApp({
  components: { Sidebar, Dashboard, Articles },
  template: `
    <div class="app-layout">
      <Sidebar
        :activeView="currentView"
        :activeCategory="currentCategory"
        :badgeCounts="badgeCounts"
        @navigate="handleNavigate"
      />
      <main class="main-area">
        <Dashboard v-if="currentView === 'dashboard'" key="dashboard" />
        <Articles v-else-if="currentView === 'articles'" :category="currentCategory" key="articles" />
      </main>
    </div>
  `,
  setup() {
    const currentView = ref("dashboard");
    const currentCategory = ref(null);
    const badgeCounts = ref({});

    function handleNavigate(view, category) {
      currentView.value = view;
      currentCategory.value = category || null;
    }

    async function loadBadges() {
      try {
        const stats = await getStatsBySource();
        const counts = { tech: 0, finance: 0, local: 0 };
        stats.forEach((s) => { if (counts[s.category] !== undefined) counts[s.category] += s.cnt; });
        badgeCounts.value = counts;
      } catch {}
    }

    watch(currentView, (v) => { if (v === "dashboard") loadBadges(); });
    onMounted(loadBadges);

    return { currentView, currentCategory, badgeCounts, handleNavigate };
  },
});

app.mount("#app");
