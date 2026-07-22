import { createRouter, createWebHashHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "dashboard",
    component: () => import("@/views/DashboardPage.vue"),
    meta: { title: "仪表盘" },
  },
  {
    path: "/articles",
    name: "articles",
    component: () => import("@/views/ArticlesPage.vue"),
    meta: { title: "文章列表" },
  },
  {
    path: "/articles/:id",
    name: "article-detail",
    component: () => import("@/views/ArticleDetailPage.vue"),
    props: (route) => ({ id: Number(route.params.id) }),
    meta: { title: "文章详情" },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/",
  },
];

// Hash history works on any deployment (GitHub Pages, Netlify, etc.)
// without needing server-side SPA fallback or base-path configuration.
// Switch to createWebHistory('/') when using a custom domain.
const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// Set document title from route meta
router.beforeEach((to) => {
  const title = to.meta.title as string | undefined;
  document.title = title ? `${title} · Beijing News Pipeline` : "Beijing News Pipeline";
});

export default router;
