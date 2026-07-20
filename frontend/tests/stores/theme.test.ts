import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useThemeStore } from "@/stores/theme";

describe("theme store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
  });

  it("defaults to system mode", () => {
    const store = useThemeStore();
    expect(store.mode).toBe("system");
  });

  it("setTheme changes mode and persists", () => {
    const store = useThemeStore();
    store.setTheme("dark");
    expect(store.mode).toBe("dark");
    expect(localStorage.setItem).toHaveBeenCalledWith("news-theme", "dark");
  });

  it("toggleTheme cycles dark → light → system → dark", () => {
    const store = useThemeStore();
    store.setTheme("dark");
    store.toggleTheme();
    expect(store.mode).toBe("light");
    store.toggleTheme();
    expect(store.mode).toBe("system");
    store.toggleTheme();
    expect(store.mode).toBe("dark");
  });

  it("apply sets data-theme attribute on html", () => {
    const store = useThemeStore();
    store.setTheme("dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });
});
