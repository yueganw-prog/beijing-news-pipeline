import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useArticlesStore } from "@/stores/articles";
import type { Article } from "@/types";

const { mockArticles, mockArticleDetail } = vi.hoisted(() => ({
  mockArticles: [
    {
      id: 1, source: "36氪", category: "tech", title: "Test Title",
      url: "#", author: "Author", summary: "Summary",
      published_at: "2026-07-20T00:00:00Z", fetched_at: "2026-07-20T00:00:00Z",
    },
    {
      id: 2, source: "虎嗅", category: "tech", title: "Another",
      url: "#", author: "Author2", summary: "Summary2",
      published_at: "2026-07-19T00:00:00Z", fetched_at: "2026-07-19T00:00:00Z",
    },
  ] as Article[],
  mockArticleDetail: {
    id: 1, source: "36氪", category: "tech", title: "Test Title",
    url: "#", author: "Author", summary: "Summary",
    published_at: "2026-07-20T00:00:00Z", fetched_at: "2026-07-20T00:00:00Z",
    content_clean: "Full content",
  },
}));

vi.mock("@/api/endpoints", () => ({
  getArticles: vi.fn().mockResolvedValue(mockArticles),
  getArticle: vi.fn().mockResolvedValue(mockArticleDetail),
}));

describe("articles store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("has empty initial state", () => {
    const store = useArticlesStore();
    expect(store.items).toEqual([]);
    expect(store.loading).toBe(false);
  });

  it("fetchArticles populates items", async () => {
    const store = useArticlesStore();
    await store.fetchArticles();
    expect(store.items).toEqual(mockArticles);
  });

  it("sources getter returns unique sources", async () => {
    const store = useArticlesStore();
    await store.fetchArticles();
    expect(store.sources).toEqual(["36氪", "虎嗅"]);
  });

  it("setCategory resets other filters", () => {
    const store = useArticlesStore();
    store.setSource("36氪");
    store.setSearch("test");
    store.setCategory("tech");
    expect(store.category).toBe("tech");
    expect(store.source).toBeNull();
    expect(store.searchQuery).toBe("");
  });

  it("hasFilters is true when filters active", () => {
    const store = useArticlesStore();
    store.setCategory("tech");
    expect(store.hasFilters).toBe(true);
  });

  it("fetchArticleDetail sets currentDetail", async () => {
    const store = useArticlesStore();
    await store.fetchArticleDetail(1);
    expect(store.currentDetail).not.toBeNull();
    expect(store.currentDetail?.content_clean).toBe("Full content");
  });

  it("clearDetail nulls currentDetail", () => {
    const store = useArticlesStore();
    store.currentDetail = { id: 1 } as never;
    store.clearDetail();
    expect(store.currentDetail).toBeNull();
  });
});
