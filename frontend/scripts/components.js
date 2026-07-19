 const { ref, computed, watch, onMounted, defineComponent, h } = Vue;
 
 // ─── Icons (inline SVGs) ───
 const Icons = {
   dashboard: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>',
   newspaper: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>',
   tech: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/></svg>',
   finance: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></svg>',
   local: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
   refresh: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>',
   search: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
   globe: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
   user: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
   calendar: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 2v4"/><path d="M16 2v4"/><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M3 10h18"/></svg>',
   close: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
   clock: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
   link: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>',
   copy: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="8" width="14" height="14" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>',
   check: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
 };
 
 const catLabels = { tech: '科技', finance: '财经', local: '本地' };
 const categories = [
   { key: 'tech', label: '科技', color: '#5eb8ff', icon: 'tech' },
   { key: 'finance', label: '财经', color: '#f0b848', icon: 'finance' },
   { key: 'local', label: '本地', color: '#4ec98b', icon: 'local' }
 ];
 
 // ─── Sidebar ───
 const Sidebar = {
   props: ['activeView', 'activeCategory', 'badgeCounts'],
   emits: ['navigate'],
   template: `
     <nav class="sidebar">
       <div class="sidebar-logo">
         <h1>Beijing News Pipeline</h1>
         <span>新闻聚合管道</span>
       </div>
       <div class="nav-group">
         <div class="nav-group-label">概览</div>
         <div class="nav-item" :class="{ active: activeView === 'dashboard' }" @click="$emit('navigate', 'dashboard', null)">
           ${Icons.dashboard} 仪表盘
         </div>
         <div class="nav-item" :class="{ active: activeView === 'articles' && !activeCategory }" @click="$emit('navigate', 'articles', null)">
           ${Icons.newspaper} 文章列表
         </div>
       </div>
       <div class="nav-group">
         <div class="nav-group-label">分类</div>
         <div v-for="cat in categories" :key="cat.key"
           class="nav-item"
           :class="{ active: activeView === 'articles' && activeCategory === cat.key }"
           @click="$emit('navigate', 'articles', cat.key)"
         >
           <span v-html="catSvg(cat.icon)" :style="{ color: cat.color, display:'inline-flex' }"></span>
           {{ cat.label }}
           <span class="nav-badge">{{ (badgeCounts || {})[cat.key] ?? '-' }}</span>
         </div>
       </div>
       <div class="sidebar-footer">API: localhost:8000</div>
     </nav>
   `,
   setup() {
     const catSvg = (key) => Icons[key] || '';
     return { categories, catSvg };
   }
 };
 
 // ─── StatsCard ───
 const StatsCard = {
   props: ['label', 'value', 'sub', 'color'],
   template: `
     <div class="stat-card" :class="color || ''">
       <div class="stat-label">{{ label }}</div>
       <div class="stat-value">{{ value }}</div>
       <div v-if="sub" class="stat-sub">{{ sub }}</div>
     </div>
   `
 };
 
 // ─── ArticleDetail ───
 const ArticleDetail = {
   props: ['article'],
   emits: ['close'],
   template: `
     <div class="overlay" @click.self="$emit('close')">
       <div class="panel">
         <div class="panel-header">
           <h2>{{ article.title }}</h2>
           <button class="close-btn" @click="$emit('close')">${Icons.close}</button>
         </div>
         <div class="panel-body">
           <div class="meta">
             <span class="badge" :class="'badge-' + article.category">{{ catLabels[article.category] || article.category }}</span>
             <span>${Icons.globe}{{ article.source }}</span>
             <span v-if="article.author">${Icons.user}{{ article.author }}</span>
             <span>${Icons.calendar}{{ article.published_at ? new Date(article.published_at).toLocaleDateString('zh-CN') : '-' }}</span>
           </div>
           <div v-if="article.summary" class="summary">{{ article.summary }}</div>
           <div class="content" v-text="article.content_clean || article.content_raw || '(无内容)'"></div>
           <div class="actions">
             <button class="action-btn" @click="searchOriginal">${Icons.link} 搜索原文</button>
             <button class="action-btn" @click="copyContent">${Icons.copy} {{ copied ? '已复制' : '复制内容' }}</button>
           </div>
         </div>
       </div>
     </div>
   `,
   setup(props) {
     const copied = ref(false);
     function searchOriginal() {
       window.open('https://www.google.com/search?q=' + encodeURIComponent(props.article.title), '_blank');
     }
     async function copyContent() {
       const text = props.article.content_clean || props.article.content_raw || '';
       try { await navigator.clipboard.writeText(text); copied.value = true; setTimeout(() => copied.value = false, 2000); } catch {}
     }
     return { catLabels, copied, searchOriginal, copyContent };
   }
 };
 
 // ─── Dashboard View ───
 const Dashboard = {
   components: { StatsCard },
   template: `
     <div class="topbar">
       <h2>仪表盘</h2>
       <button class="btn-icon" :class="{ refreshing }" @click="loadData">${Icons.refresh}</button>
     </div>
     <div class="content">
       <div class="content-inner">
         <div v-if="loading" class="skeleton-grid">
           <div v-for="i in 4" :key="i" class="skeleton" style="height:100px"></div>
         </div>
         <div v-else class="stats-row">
           <StatsCard label="文章总数" :value="total" color="blue" />
           <StatsCard label="新闻源" :value="sources" />
           <StatsCard label="最近运行" :value="lastRun" :color="lastRunColor" />
           <StatsCard label="DQ 均分" :value="dqAvg" color="green" />
         </div>
         <div class="section-title">按来源统计</div>
         <div v-if="loading" class="skeleton-grid source-grid">
           <div v-for="i in 6" :key="i" class="skeleton" style="height:110px"></div>
         </div>
         <div v-else-if="stats.length" class="source-grid">
           <div v-for="s in stats" :key="s.source" class="source-card" :class="s.category">
             <div class="src-name">{{ s.source }}</div>
             <div class="src-count">{{ s.cnt }}</div>
             <div class="src-last">${Icons.clock} 最近: {{ s.last_fetched ? new Date(s.last_fetched).toLocaleString('zh-CN') : '-' }}</div>
           </div>
         </div>
         <div v-else class="empty-state">暂无来源数据</div>
       </div>
     </div>
   `,
   setup() {
     const loading = ref(true); const refreshing = ref(false);
     const stats = ref([]); const runs = ref([]);
     const total = computed(() => stats.value.reduce((s, x) => s + x.cnt, 0));
     const sources = computed(() => stats.value.length);
     const lastRun = computed(() => runs.value.length ? runs.value[0].status : 'N/A');
     const lastRunColor = computed(() => { const s = runs.value[0]?.status; return s === 'success' ? 'green' : s === 'failed' ? '' : 'amber'; });
     const dqAvg = computed(() => runs.value.length && runs.value[0].dq_avg_score ? runs.value[0].dq_avg_score.toFixed(1) : '-');
 
     async function loadData() {
       refreshing.value = true;
       try { const [s, r] = await Promise.all([getStatsBySource(), getPipelineRuns(5)]); stats.value = s; runs.value = r; } catch (e) { console.error(e); }
       finally { loading.value = false; refreshing.value = false; }
     }
     onMounted(loadData);
     return { loading, refreshing, stats, total, sources, lastRun, lastRunColor, dqAvg, loadData };
   }
 };
 
 // ─── Articles View ───
 const Articles = {
   components: { ArticleDetail },
   props: ['category'],
   template: `
     <div class="topbar">
       <h2>文章列表 · {{ categoryLabel }}</h2>
       <button class="btn-icon" :class="{ refreshing }" @click="loadArticles">${Icons.refresh}</button>
     </div>
     <div class="content">
       <div class="content-inner">
         <div class="filter-bar">
           <span class="filter-chip" :class="{ active: !activeSource }" @click="activeSource = null; loadArticles()">全部</span>
           <span v-for="s in sources" :key="s" class="filter-chip" :class="[ sourceCategory(s), { active: activeSource === s } ]"
             @click="activeSource = s; loadArticles()">{{ s }}</span>
         </div>
         <div class="search-bar">
           <input v-model="searchQuery" type="text" placeholder="搜索标题、摘要或正文..." @keydown.enter="loadArticles" />
           <button class="btn-icon" @click="loadArticles">${Icons.search}</button>
         </div>
         <div v-if="loading" class="loading-overlay"><span class="spinner"></span> 加载中...</div>
         <table v-else-if="articles.length" class="article-table">
           <thead><tr><th>标题</th><th>来源</th><th>分类</th><th>日期</th></tr></thead>
           <tbody>
             <tr v-for="(a, idx) in articles" :key="a.id" :style="{ animation: 'slideUp .3s ease ' + (idx * 0.02) + 's both' }"
               @click="openDetail(a.id)">
               <td class="cell-title" :title="a.title">{{ a.title || '(无标题)' }}</td>
               <td class="cell-source">{{ a.source }}</td>
               <td class="cell-category"><span class="badge" :class="'badge-' + a.category">{{ catLabels[a.category] || a.category }}</span></td>
               <td class="cell-date">{{ a.published_at ? new Date(a.published_at).toLocaleDateString('zh-CN') : '-' }}</td>
             </tr>
           </tbody>
         </table>
         <div v-else class="empty-state">暂无文章</div>
       </div>
     </div>
     <ArticleDetail v-if="detailArticle" :article="detailArticle" @close="detailArticle = null" />
   `,
   setup(props) {
     const articles = ref([]); const sources = ref([]); const loading = ref(true);
     const refreshing = ref(false); const activeSource = ref(null);
     const searchQuery = ref(''); const detailArticle = ref(null);
 
     const categoryLabel = computed(() => props.category ? catLabels[props.category] || '全部' : '全部');
 
     function sourceCategory(source) { const a = articles.value.find(x => x.source === source); return a ? a.category : ''; }
 
     watch(() => props.category, () => { activeSource.value = null; searchQuery.value = ''; loadArticles(); });
 
     async function loadArticles() {
       loading.value = articles.value.length === 0; refreshing.value = true;
       try {
         const params = { limit: 200 };
         if (props.category) params.category = props.category;
         if (activeSource.value) params.source = activeSource.value;
         if (searchQuery.value.trim()) params.search = searchQuery.value.trim();
         const data = await getArticles(params);
         articles.value = data;
         sources.value = [...new Set(data.map(a => a.source))];
       } catch (e) { console.error(e); }
       finally { loading.value = false; refreshing.value = false; }
     }
 
     async function openDetail(id) {
       try { detailArticle.value = await getArticle(id); }
       catch { detailArticle.value = articles.value.find(a => a.id === id) || null; }
     }
 
     onMounted(loadArticles);
     return { articles, sources, loading, refreshing, activeSource, searchQuery, detailArticle, categoryLabel, sourceCategory, loadArticles, openDetail, catLabels };
   }
 };


// Expose components to other scripts
window.Sidebar = Sidebar;
window.StatsCard = StatsCard;
window.ArticleDetail = ArticleDetail;
window.Dashboard = Dashboard;
window.Articles = Articles;
window.Icons = Icons;
window.catLabels = catLabels;
window.categories = categories;
