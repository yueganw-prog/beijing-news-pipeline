export function formatDate(isoStr: string | null | undefined): string {
  if (!isoStr) return "-";
  try {
    return new Date(isoStr).toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
  } catch {
    return "-";
  }
}

export function formatDateTime(isoStr: string | null | undefined): string {
  if (!isoStr) return "-";
  try {
    return new Date(isoStr).toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "-";
  }
}

export function timeAgo(isoStr: string | null | undefined): string {
  if (!isoStr) return "";
  try {
    const diff = Date.now() - new Date(isoStr).getTime();
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    if (mins < 1) return "刚刚";
    if (mins < 60) return `${mins} 分钟前`;
    if (hours < 24) return `${hours} 小时前`;
    if (days < 30) return `${days} 天前`;
    return formatDate(isoStr);
  } catch {
    return "";
  }
}
