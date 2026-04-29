import request from '@/utils/request'

// 获取新闻分页列表（支持关键词筛选）
export function getNewsList(params) {
  return request.get('/api/news/', { params })
}

// 获取每日新闻数量统计
export function getDailyStats(params) {
  return request.get('/api/news/stats/daily', { params })
}

// 获取最新爬取的 10 条新闻
export function getLatestNews() {
  return request.get('/api/news/latest')
}

// 获取关键词词频统计（词云数据）
export function getKeywordStats(params) {
  return request.get('/api/news/stats/keywords', { params })
}

// 获取概览统计数据（总数、今日数、关键词数）
export function getOverviewStats() {
  return request.get('/api/news/stats/overview')
}

// 获取关键词时间线数据
export function getKeywordTimeline(params) {
  return request.get('/api/news/stats/keyword-timeline', { params })
}

// 运行爬虫
export function runSpider() {
  return request.post('/api/news/spider/run')
}
