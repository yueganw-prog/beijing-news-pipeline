import type { Category } from "@/types";

export const CATEGORIES: { key: Category; label: string; color: string; icon: string }[] = [
  { key: "tech", label: "科技", color: "var(--blue)", icon: "tech" },
  { key: "finance", label: "财经", color: "var(--amber)", icon: "finance" },
  { key: "local", label: "本地", color: "var(--green)", icon: "local" },
];

export const CATEGORY_LABELS: Record<string, string> = {
  tech: "科技",
  finance: "财经",
  local: "本地",
};

export const APP_NAME = "Beijing News Pipeline";
export const APP_SUBTITLE = "新闻聚合管道";
