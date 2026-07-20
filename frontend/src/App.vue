<template>
  <div class="app-layout">
    <!-- Mobile backdrop -->
    <Transition name="fade">
      <div v-if="mobileOpen" class="mobile-backdrop" @click="mobileOpen = false" />
    </Transition>

    <!-- Sidebar -->
    <AppSidebar :mobile-open="mobileOpen" @close-mobile="mobileOpen = false" />

    <!-- Main content area -->
    <main class="main-area">
      <RouterView @toggle-mobile="mobileOpen = !mobileOpen" />
    </main>

    <!-- Toast notifications -->
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useThemeStore } from "@/stores/theme";
import AppSidebar from "@/components/layout/AppSidebar.vue";
import ToastContainer from "@/components/common/ToastContainer.vue";

const mobileOpen = ref(false);
const theme = useThemeStore();

onMounted(() => {
  theme.init();
});
</script>
