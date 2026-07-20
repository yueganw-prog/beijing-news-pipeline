import { defineStore } from "pinia";
import { ref, computed } from "vue";

export type ThemeMode = "dark" | "light" | "system";
const STORAGE_KEY = "news-theme";

function getSystemPreference(): "dark" | "light" {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function resolveTheme(mode: ThemeMode): "dark" | "light" {
  return mode === "system" ? getSystemPreference() : mode;
}

export const useThemeStore = defineStore("theme", () => {
  const mode = ref<ThemeMode>((localStorage.getItem(STORAGE_KEY) as ThemeMode) || "system");
  const resolved = ref<"dark" | "light">(resolveTheme(mode.value));

  const isDark = computed(() => resolved.value === "dark");

  function apply() {
    resolved.value = resolveTheme(mode.value);
    document.documentElement.setAttribute("data-theme", resolved.value);
  }

  function setTheme(newMode: ThemeMode) {
    mode.value = newMode;
    localStorage.setItem(STORAGE_KEY, newMode);
    apply();
  }

  function toggleTheme() {
    const order: ThemeMode[] = ["dark", "light", "system"];
    const idx = order.indexOf(mode.value);
    setTheme(order[(idx + 1) % order.length]);
  }

  function init() {
    apply();
    // Listen for system theme changes when in "system" mode
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
      if (mode.value === "system") {
        resolved.value = getSystemPreference();
        document.documentElement.setAttribute("data-theme", resolved.value);
      }
    });
  }

  return { mode, resolved, isDark, setTheme, toggleTheme, init };
});
