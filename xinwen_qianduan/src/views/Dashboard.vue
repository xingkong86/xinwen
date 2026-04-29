<template>
  <div class="dashboard" v-loading="loading">

    <!-- 顶部 Header -->
    <header class="dashboard-header">
      <div class="header-brand">
        <div class="brand-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M3 3h7v7H3V3zm0 11h7v7H3v-7zm11-11h7v7h-7V3zm0 11h7v7h-7v-7z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="6.5" cy="6.5" r="1.5" fill="currentColor"/>
            <circle cx="6.5" cy="17.5" r="1.5" fill="currentColor"/>
            <circle cx="17.5" cy="6.5" r="1.5" fill="currentColor"/>
            <circle cx="17.5" cy="17.5" r="1.5" fill="currentColor"/>
          </svg>
        </div>
        <div class="brand-text">
          <h1 class="brand-title">新闻数据可视化监测大屏</h1>
          <p class="brand-subtitle">NEWS DATA VISUALIZATION MONITOR</p>
        </div>
      </div>

      <div class="header-controls">
        <div class="live-badge">
          <span class="live-dot"></span>
          <span>LIVE</span>
        </div>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :shortcuts="shortcuts"
          @change="handleDateRangeChange"
        />
        <el-button type="success" :loading="spiderLoading" @click="handleRunSpider">运行爬虫</el-button>
        <el-button type="primary" :icon="Refresh" @click="refreshData">刷新数据</el-button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <section class="stats-section">
      <div class="stat-card stat-card--1" style="animation-delay: 0.05s">
        <div class="stat-card-glow"></div>
        <div class="stat-icon-wrap">
          <el-icon :size="28"><Document /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-label">新闻总数</div>
          <div class="stat-value">{{ totalNews }}</div>
          <div class="stat-trend">📰 全部数据</div>
        </div>
        <div class="stat-decoration"></div>
      </div>

      <div class="stat-card stat-card--2" style="animation-delay: 0.1s">
        <div class="stat-card-glow"></div>
        <div class="stat-icon-wrap">
          <el-icon :size="28"><Calendar /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-label">今日新增</div>
          <div class="stat-value">{{ todayNews }}</div>
          <div class="stat-trend">🕐 实时更新</div>
        </div>
        <div class="stat-decoration"></div>
      </div>

      <div class="stat-card stat-card--3" style="animation-delay: 0.15s">
        <div class="stat-card-glow"></div>
        <div class="stat-icon-wrap">
          <el-icon :size="28"><PriceTag /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-label">关键词数</div>
          <div class="stat-value">{{ keywordCount }}</div>
          <div class="stat-trend">🏷️ 热词追踪</div>
        </div>
        <div class="stat-decoration"></div>
      </div>
    </section>

    <!-- 图表区域 - 第一行 -->
    <section class="charts-row" style="animation-delay: 0.2s">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header-content">
            <span class="card-header-dot dot-cyan"></span>
            <span class="card-header-title">每日新闻统计</span>
          </div>
        </template>
        <DailyStatsChart :chartData="dailyStats" />
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="card-header-content">
            <span class="card-header-dot dot-blue"></span>
            <span class="card-header-title">热门关键词 Top 20</span>
          </div>
        </template>
        <KeywordBarChart :chartData="keywordStats" @keyword-click="handleKeywordClick" />
      </el-card>
    </section>

    <!-- 图表区域 - 第二行 -->
    <section class="charts-row" style="animation-delay: 0.25s">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header-content">
            <span class="card-header-dot dot-purple"></span>
            <span class="card-header-title">新闻关键词词云</span>
          </div>
        </template>
        <WordCloudChart :chartData="keywordStats" @keyword-click="handleKeywordClick" />
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="card-header-content">
            <span class="card-header-dot dot-green"></span>
            <span class="card-header-title">头部关键词占比</span>
          </div>
        </template>
        <KeywordPieChart :chartData="keywordStats" />
      </el-card>
    </section>

    <!-- 热点事件时间线 -->
    <section class="charts-full" style="animation-delay: 0.3s">
      <el-card>
        <template #header>
          <div class="card-header-content">
            <span class="card-header-dot dot-orange"></span>
            <span class="card-header-title">热点事件时间线</span>
          </div>
        </template>
        <HotEventTimeline :chartData="timelineData" @keyword-click="handleKeywordClick" />
      </el-card>
    </section>

    <!-- 关键词趋势对比 -->
    <section class="charts-full" style="animation-delay: 0.35s">
      <el-card>
        <template #header>
          <div class="card-header-content">
            <span class="card-header-dot dot-cyan"></span>
            <span class="card-header-title">关键词趋势对比分析</span>
          </div>
        </template>
        <KeywordTrendComparison :timelineData="timelineData" />
      </el-card>
    </section>

    <!-- 最新新闻表格 -->
    <section class="charts-full news-table-card" style="animation-delay: 0.4s">
      <el-card>
        <template #header>
          <div class="card-header-content">
            <span class="card-header-dot dot-blue"></span>
            <span class="card-header-title">
              {{ selectedKeyword ? `包含"${selectedKeyword}"的新闻` : '最新新闻' }}
            </span>
            <el-button v-if="selectedKeyword" link @click="clearKeywordFilter" class="clear-btn">
              × 清除筛选
            </el-button>
          </div>
        </template>
        <el-table :data="latestNews" stripe style="width: 100%">
          <el-table-column type="index" label="#" width="60" />
          <el-table-column prop="title" label="标题" min-width="300" show-overflow-tooltip />
          <el-table-column prop="intro" label="简介" width="250" show-overflow-tooltip />
          <el-table-column label="发布时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.publish_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="keywords" label="关键词" width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <el-tag
                v-for="(keyword, index) in getKeywordTags(row.keywords)"
                :key="index"
                size="small"
                style="margin-right: 5px; margin-bottom: 2px"
              >
                {{ keyword }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap" v-if="totalTableNews > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalTableNews"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            class="custom-pagination"
          />
        </div>
      </el-card>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Document, Calendar, PriceTag } from '@element-plus/icons-vue'
import { getDailyStats, getKeywordStats, getOverviewStats, getNewsList, getKeywordTimeline, runSpider } from '@/api/news'
import DailyStatsChart from '@/components/DailyStatsChart.vue'
import KeywordBarChart from '@/components/KeywordBarChart.vue'
import WordCloudChart from '@/components/WordCloudChart.vue'
import KeywordPieChart from '@/components/KeywordPieChart.vue'
import HotEventTimeline from '@/components/HotEventTimeline.vue'
import KeywordTrendComparison from '@/components/KeywordTrendComparison.vue'

const loading = ref(false)
const spiderLoading = ref(false)
const dailyStats = ref([])
const latestNews = ref([])
const keywordStats = ref([])
const timelineData = ref([])
const totalNews = ref(0)
const todayNews = ref(0)
const keywordCount = ref(0)

const selectedKeyword = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(50)
const totalTableNews = ref(0)

const shortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  }
]

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getKeywordTags = (keywords) => {
  if (!keywords) return []
  return keywords.split(',').slice(0, 3)
}

const formatDate = (date) => {
  if (!date) return null
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const fetchDailyStats = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = formatDate(dateRange.value[0])
      params.end_date = formatDate(dateRange.value[1])
    }
    const res = await getDailyStats(params)
    const data = res.data || res
    if (Array.isArray(data)) dailyStats.value = data
  } catch (error) {
    console.error('获取每日统计失败:', error)
  }
}

const fetchOverviewStats = async () => {
  try {
    const res = await getOverviewStats()
    const data = res.data || {}
    totalNews.value = data.total_news || 0
    todayNews.value = data.today_news || 0
    keywordCount.value = data.keyword_count || 0
  } catch (error) {
    console.error('获取概览统计失败:', error)
  }
}

const fetchLatestNews = async () => {
  try {
    const params = { 
      skip: (currentPage.value - 1) * pageSize.value, 
      limit: pageSize.value 
    }
    if (selectedKeyword.value) params.keyword = selectedKeyword.value
    
    const res = await getNewsList(params)
    const data = res.data || res
    
    if (Array.isArray(data)) {
      latestNews.value = data
      totalTableNews.value = data.length
    } else {
      latestNews.value = data.items || []
      totalTableNews.value = data.total || 0
    }
  } catch (error) {
    console.error('获取最新新闻失败:', error)
  }
}

const fetchKeywordStats = async () => {
  try {
    const params = { limit: 100 }
    if (dateRange.value && dateRange.value.length === 2) {
      const start = new Date(dateRange.value[0])
      const end = new Date(dateRange.value[1])
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
      params.days = days
    } else {
      params.days = 7
    }
    const res = await getKeywordStats(params)
    const data = res.data || res
    if (Array.isArray(data)) keywordStats.value = data
  } catch (error) {
    console.error('获取关键词统计失败:', error)
  }
}

const fetchTimelineData = async () => {
  try {
    const params = { top_keywords: 10 }
    if (dateRange.value && dateRange.value.length === 2) {
      const start = new Date(dateRange.value[0])
      const end = new Date(dateRange.value[1])
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
      params.days = days
    } else {
      params.days = 30
    }
    const res = await getKeywordTimeline(params)
    const data = res.data || res
    if (Array.isArray(data)) timelineData.value = data
  } catch (error) {
    console.error('获取时间线数据失败:', error)
  }
}

const handleKeywordClick = (keyword) => {
  selectedKeyword.value = keyword
  currentPage.value = 1
  setTimeout(() => {
    const newsTable = document.querySelector('.news-table-card')
    if (newsTable) newsTable.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 100)
  fetchLatestNews()
}

const clearKeywordFilter = () => {
  selectedKeyword.value = ''
  currentPage.value = 1
  fetchLatestNews()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchLatestNews()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchLatestNews()
}

const handleDateRangeChange = () => {
  refreshData()
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchDailyStats(),
      fetchOverviewStats(),
      fetchLatestNews(),
      fetchKeywordStats(),
      fetchTimelineData()
    ])
  } finally {
    loading.value = false
  }
}

const handleRunSpider = async () => {
  spiderLoading.value = true
  try {
    const res = await runSpider()
    const data = res.data || res
    if (data.success) {
      ElMessage.success(data.message || `爬虫运行成功，新增数据记录`)
      refreshData()
    } else {
      ElMessage.error(data.message || '爬虫运行失败')
    }
  } catch (error) {
    console.error('运行爬虫失败:', error)
    ElMessage.error('网络或服务器错误，爬虫运行失败')
  } finally {
    spiderLoading.value = false
  }
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
/* ==========================================
   Dashboard 布局
   ========================================== */
.dashboard {
  padding: 24px 28px 40px;
  min-height: 100vh;
  background: transparent;
  max-width: 1600px;
  margin: 0 auto;
}

/* ==========================================
   顶部 Header
   ========================================== */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding: 22px 32px;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  animation: fadeInUp 0.4s ease both;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.dashboard-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 32px;
  right: 32px;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-indigo), var(--accent-coral), var(--accent-gold));
  border-radius: 2px;
  transform-origin: left;
  animation: lineGrow 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 18px;
}

.brand-icon {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--accent-indigo), #5a6dc0);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 14px rgba(59,79,158,0.35);
  flex-shrink: 0;
}

.brand-title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 21px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 1px;
  margin: 0;
  line-height: 1.2;
  white-space: nowrap;
}

.brand-subtitle {
  font-size: 10px;
  font-weight: 400;
  color: var(--text-muted);
  letter-spacing: 2.5px;
  margin-top: 4px;
  font-family: 'DM Sans', sans-serif;
  text-transform: uppercase;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.live-badge {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  background: rgba(90, 122, 104, 0.1);
  border: 1px solid rgba(90, 122, 104, 0.3);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-sage);
  letter-spacing: 1.5px;
  font-family: 'DM Sans', sans-serif;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent-sage);
  animation: glowPulse 2s ease-in-out infinite;
}

/* ==========================================
   统计卡片区
   ========================================== */
.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  padding: 26px 28px;
  border-radius: var(--radius-card);
  border: 1px solid var(--border-card);
  background: var(--bg-card);
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: default;
  overflow: hidden;
  animation: fadeInUp 0.5s ease both;
  transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
  box-shadow: var(--shadow-card);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}

.stat-card-glow {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}
.stat-card:hover .stat-card-glow { opacity: 1; }

/* 各卡片颜色 */
.stat-card--1 {
  border-left: 4px solid var(--accent-indigo);
}
.stat-card--1 .stat-card-glow {
  background: radial-gradient(ellipse at 0% 50%, rgba(59,79,158,0.06) 0%, transparent 65%);
}
.stat-card--1 .stat-icon-wrap { color: var(--accent-indigo); border-color: rgba(59,79,158,0.2); background: rgba(59,79,158,0.08); }
.stat-card--1 .stat-value { color: var(--accent-indigo); }

.stat-card--2 {
  border-left: 4px solid var(--accent-sage);
}
.stat-card--2 .stat-card-glow {
  background: radial-gradient(ellipse at 0% 50%, rgba(90,122,104,0.06) 0%, transparent 65%);
}
.stat-card--2 .stat-icon-wrap { color: var(--accent-sage); border-color: rgba(90,122,104,0.2); background: rgba(90,122,104,0.08); }
.stat-card--2 .stat-value { color: var(--accent-sage); }

.stat-card--3 {
  border-left: 4px solid var(--accent-gold);
}
.stat-card--3 .stat-card-glow {
  background: radial-gradient(ellipse at 0% 50%, rgba(200,145,58,0.06) 0%, transparent 65%);
}
.stat-card--3 .stat-icon-wrap { color: var(--accent-gold); border-color: rgba(200,145,58,0.2); background: rgba(200,145,58,0.08); }
.stat-card--3 .stat-value { color: var(--accent-gold); }

.stat-icon-wrap {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: 14px;
  border: 1px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.28s ease;
}
.stat-card:hover .stat-icon-wrap {
  transform: scale(1.06) rotate(3deg);
}

.stat-body { flex: 1; min-width: 0; }

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 1.2px;
  text-transform: uppercase;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-family: 'DM Sans', sans-serif;
  font-size: 38px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
  letter-spacing: -1.5px;
  animation: numberCount 0.5s ease both;
}

.stat-trend {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.3px;
}

.stat-decoration {
  position: absolute;
  top: -30px;
  right: -30px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: transparent;
  border: 1.5px solid rgba(180, 165, 150, 0.12);
  pointer-events: none;
}

/* ==========================================
   图表区域布局
   ========================================== */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
  animation: fadeInUp 0.5s ease both;
}

.charts-full {
  margin-bottom: 20px;
  animation: fadeInUp 0.5s ease both;
}

.chart-card {
  min-height: 320px;
}

/* ==========================================
   卡片标题
   ========================================== */
.card-header-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-cyan   { background: var(--accent-indigo); }
.dot-blue   { background: var(--accent-indigo); }
.dot-purple { background: var(--accent-plum); }
.dot-green  { background: var(--accent-sage); }
.dot-orange { background: var(--accent-coral); }

.card-header-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.4px;
  flex: 1;
}

.clear-btn {
  margin-left: auto;
  font-size: 12px;
  color: var(--accent-coral) !important;
  opacity: 0.8;
  transition: opacity 0.2s ease;
}
.clear-btn:hover { opacity: 1; }

/* ==========================================
   新闻表格与分页
   ========================================== */
.news-table-card {
  scroll-margin-top: 24px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-subtle);
}

:deep(.custom-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: var(--text-secondary);
  --el-pagination-button-color: var(--text-secondary);
  --el-pagination-button-disabled-bg-color: transparent;
  --el-pagination-hover-color: var(--accent-indigo);
}

:deep(.custom-pagination .el-pager li) {
  background-color: rgba(255, 252, 248, 0.8);
  border: 1px solid var(--border-card);
  color: var(--text-secondary);
  border-radius: 6px;
}

:deep(.custom-pagination .el-pager li.is-active) {
  background-color: var(--accent-indigo);
  color: #fff;
  border-color: var(--accent-indigo);
  font-weight: bold;
}

:deep(.custom-pagination button) {
  background-color: rgba(255, 252, 248, 0.8) !important;
  border: 1px solid var(--border-card) !important;
  border-radius: 6px !important;
  color: var(--text-secondary) !important;
}
</style>
