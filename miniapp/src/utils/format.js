/**
 * 文章分类标签映射
 */
export const CAT_LABELS = {
  tech: '科技',
  finance: '财经',
  local: '本地'
}

/**
 * 格式化 ISO 日期为中文显示
 * @param {string} isoStr - ISO 8601 日期字符串
 * @returns {string} 如 "2026年7月18日"
 */
export function formatDate(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  if (isNaN(d.getTime())) return isoStr
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

/**
 * 格式化 ISO 日期为相对时间
 * @param {string} isoStr - ISO 8601 日期字符串
 * @returns {string} 如 "3小时前" / "2天前"
 */
export function formatRelative(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  if (isNaN(d.getTime())) return isoStr
  const now = new Date()
  const diff = now - d
  const min = Math.floor(diff / 60000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min}分钟前`
  const hour = Math.floor(min / 60)
  if (hour < 24) return `${hour}小时前`
  const day = Math.floor(hour / 24)
  if (day < 7) return `${day}天前`
  return formatDate(isoStr)
}

/**
 * 截断文本
 * @param {string} text
 * @param {number} maxLen
 * @returns {string}
 */
export function truncate(text, maxLen = 100) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

/**
 * 去除 HTML 标签
 * @param {string} html
 * @returns {string}
 */
export function stripHtml(html) {
  if (!html) return ''
  return html.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()
}
