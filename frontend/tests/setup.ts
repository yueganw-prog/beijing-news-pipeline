import { config } from "@vue/test-utils";
import { createPinia } from "pinia";
import { createRouter, createMemoryHistory } from "vue-router";

// Mock fetch globally
globalThis.fetch = vi.fn() as unknown as typeof fetch;

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
});

// Helper: create a testing pinia instance
export function createTestPinia() {
  return createPinia();
}

// Helper: create a mock router
export function createTestRouter(routes = []) {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: { template: "<div>Home</div>" } },
      { path: "/articles", component: { template: "<div>Articles</div>" } },
      { path: "/articles/:id", component: { template: "<div>Detail</div>" } },
      ...routes,
    ],
  });
}

// Mock localStorage
const store: Record<string, string> = {};
globalThis.localStorage = {
  getItem: vi.fn((key: string) => store[key] ?? null),
  setItem: vi.fn((key: string, value: string) => {
    store[key] = value;
  }),
  removeItem: vi.fn((key: string) => {
    delete store[key];
  }),
  clear: vi.fn(() => {
    Object.keys(store).forEach((k) => delete store[k]);
  }),
  get length() {
    return Object.keys(store).length;
  },
  key: vi.fn((index: number) => Object.keys(store)[index] ?? null),
} as unknown as Storage;

// Mock matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Global vue test utils config
config.global.stubs = {
  transition: false,
  "transition-group": false,
};
