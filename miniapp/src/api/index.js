/**
 * Beijing News MiniApp — API Layer
 * Adapted from frontend/scripts/api.js
 * Uses uni.request() instead of fetch()
 */

const API_BASE = 'http://192.168.6.105:8000'

/**
 * Generic request wrapper
 * @param {string} url - full URL
 * @param {object} options - uni.request options
 * @returns {Promise<any>}
 */
function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method: 'GET',
      timeout: 15000,
      ...options,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(new Error(`API error: ${res.statusCode}`))
        }
      },
      fail(err) {
        reject(new Error(err.errMsg || 'Network error'))
      }
    })
  })
}

/**
 * Build query string from params object
 * @param {object} params
 * @returns {string}
 */
function buildQuery(params) {
  const parts = []
  for (const [key, val] of Object.entries(params)) {
    if (val !== null && val !== undefined && val !== '') {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(val)}`)
    }
  }
  return parts.length ? '?' + parts.join('&') : ''
}

/**
 * Get article list with optional filters
 * @param {object} params
 * @param {string} [params.source] - source id filter
 * @param {string} [params.category] - category filter (tech/finance/local)
 * @param {number} [params.limit=50]
 * @param {number} [params.offset=0]
 * @returns {Promise<Array>}
 */
export function getArticles(params = {}) {
  const query = buildQuery({
    source: params.source,
    category: params.category,
    limit: params.limit || 50,
    offset: params.offset || 0
  })
  return request(`${API_BASE}/articles${query}`)
}

/**
 * Search articles by keyword
 * @param {string} q - search query
 * @param {number} [limit=50]
 * @param {number} [offset=0]
 * @returns {Promise<Array>}
 */
export function searchArticles(q, limit = 50, offset = 0) {
  const query = buildQuery({ q, limit, offset })
  return request(`${API_BASE}/articles/search${query}`)
}

/**
 * Get single article detail
 * @param {number} id - article ID
 * @returns {Promise<Object>}
 */
export function getArticle(id) {
  return request(`${API_BASE}/articles/${id}`)
}

/**
 * Get stats grouped by source/category
 * @returns {Promise<Array<{source: string, category: string, cnt: number, last_fetched: string}>>}
 */
export function getStatsBySource() {
  return request(`${API_BASE}/stats/by-source`)
}
