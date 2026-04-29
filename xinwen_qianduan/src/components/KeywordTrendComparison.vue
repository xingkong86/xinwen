<template>
  <div class="keyword-trend-comparison">
    <!-- 关键词选择器 -->
    <div class="keyword-selector">
      <el-select
        v-model="selectedKeywords"
        multiple
        filterable
        placeholder="选择 2-3 个关键词进行对比"
        style="width: 100%"
        :max-collapse-tags="3"
        @change="handleKeywordChange"
      >
        <el-option
          v-for="item in availableKeywords"
          :key="item.name"
          :label="`${item.name} (${item.value}次)`"
          :value="item.name"
        />
      </el-select>
    </div>

    <!-- 图表区域 -->
    <div ref="chartRef" class="chart-container"></div>

    <!-- 统计分析面板 -->
    <div v-if="selectedKeywords.length >= 2" class="analysis-panel">
      <el-row :gutter="20">
        <el-col :span="8" v-for="keyword in selectedKeywords" :key="keyword">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-header">{{ keyword }}</div>
            <div class="stat-content">
              <div class="stat-item">
                <span class="stat-label">总出现次数</span>
                <span class="stat-value">{{ getKeywordStats(keyword).total }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均值</span>
                <span class="stat-value">{{ getKeywordStats(keyword).avg }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">峰值</span>
                <span class="stat-value">{{ getKeywordStats(keyword).max }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">标准差</span>
                <span class="stat-value">{{ getKeywordStats(keyword).std }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 相关性分析 -->
      <el-card v-if="selectedKeywords.length === 2" shadow="hover" class="correlation-card" style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <span>相关性分析</span>
          </div>
        </template>
        <div class="correlation-content">
          <div class="correlation-item">
            <span class="correlation-label">皮尔逊相关系数</span>
            <span class="correlation-value" :class="getCorrelationClass()">
              {{ correlationCoefficient }}
            </span>
          </div>
          <div class="correlation-desc">
            {{ getCorrelationDescription() }}
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  timelineData: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null

const selectedKeywords = ref([])
const availableKeywords = computed(() => {
  return props.timelineData.map(item => ({
    name: item.keyword,
    value: item.total
  }))
})

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  }
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) return

  // 如果没有选择关键词，显示提示
  if (selectedKeywords.value.length === 0) {
    chartInstance.clear()
    const emptyOption = {
      backgroundColor: 'transparent',
      title: {
        text: '请选择 2-3 个关键词进行趋势对比',
        left: 'center',
        top: 'center',
        textStyle: { color: '#4a6a8a', fontSize: 14 }
      }
    }
    chartInstance.setOption(emptyOption, true)
    return
  }

  // 过滤选中的关键词数据
  const selectedData = props.timelineData.filter(item => 
    selectedKeywords.value.includes(item.keyword)
  )

  if (selectedData.length === 0) return

  // 提取所有日期
  const allDates = new Set()
  selectedData.forEach(item => {
    item.timeline.forEach(point => {
      allDates.add(point.date)
    })
  })
  const dates = Array.from(allDates).sort()

  // 构建系列数据
  const series = selectedData.map((item, index) => {
    const dateMap = {}
    item.timeline.forEach(point => {
      dateMap[point.date] = point.count
    })

    const data = dates.map(date => dateMap[date] || 0)

    return {
      name: item.keyword,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      data: data,
      emphasis: {
        focus: 'series',
        lineStyle: {
          width: 4
        }
      },
      lineStyle: {
        width: 3
      },
      markPoint: {
        data: [
          { type: 'max', name: '峰值' }
        ],
        label: {
          formatter: '{c}'
        }
      },
      markLine: {
        data: [
          { type: 'average', name: '平均值' }
        ],
        label: {
          formatter: '平均: {c}'
        }
      }
    }
  })

  const option = {
    backgroundColor: 'transparent',
    title: {
      text: '关键词趋势对比',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#e8f4fd' }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(250,247,242,0.97)',
      borderColor: 'rgba(180,165,150,0.4)',
      borderWidth: 1,
      textStyle: { color: '#1a1714', fontSize: 12 },
      extraCssText: 'box-shadow: 0 4px 16px rgba(30,20,10,0.1);',
      axisPointer: { type: 'cross', label: { backgroundColor: 'rgba(59,79,158,0.1)', color: '#1a1714' } },
      formatter: (params) => {
        let result = `<div style="font-weight:bold;margin-bottom:5px;color:#3b4f9e">${params[0].axisValue}</div>`
        params.forEach(item => {
          result += `<div style="display:flex;align-items:center;margin:3px 0">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${item.color};margin-right:6px"></span>
            <span style="flex:1;color:#5c504a">${item.seriesName}</span>
            <span style="font-weight:bold;margin-left:10px;color:#1a1714">${item.value} 次</span>
          </div>`
        })
        return result
      }
    },
    legend: {
      top: 30,
      left: 'center',
      textStyle: { fontSize: 13, color: '#5c504a' }
    },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '20%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(180,165,150,0.4)' } },
      axisLabel: { rotate: 45, fontSize: 11, color: '#5c504a' },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '出现次数',
      nameTextStyle: { color: '#5c504a', fontSize: 11 },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { fontSize: 11, color: '#5c504a' },
      splitLine: { lineStyle: { color: 'rgba(59,79,158,0.07)', type: 'dashed' } }
    },
    series: series,
    color: ['#3b4f9e', '#e05c4b', '#c8913a'],
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 20,
        backgroundColor: 'rgba(245,240,234,0.8)',
        fillerColor: 'rgba(59,79,158,0.12)',
        borderColor: 'rgba(180,165,150,0.35)',
        handleStyle: { color: '#3b4f9e' },
        textStyle: { color: '#5c504a' }
      }
    ]
  }

  chartInstance.setOption(option, true)
}

// 处理关键词选择变化
const handleKeywordChange = (value) => {
  // 限制最多选择3个
  if (value.length > 3) {
    selectedKeywords.value = value.slice(0, 3)
  }
  updateChart()
}

// 获取关键词统计数据
const getKeywordStats = (keyword) => {
  const data = props.timelineData.find(item => item.keyword === keyword)
  if (!data) return { total: 0, avg: 0, max: 0, std: 0 }

  const counts = data.timeline.map(point => point.count)
  const total = counts.reduce((sum, val) => sum + val, 0)
  const avg = counts.length > 0 ? (total / counts.length).toFixed(2) : 0
  const max = Math.max(...counts)
  
  // 计算标准差
  const mean = total / counts.length
  const variance = counts.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / counts.length
  const std = Math.sqrt(variance).toFixed(2)

  return { total, avg, max, std }
}

// 计算皮尔逊相关系数
const correlationCoefficient = computed(() => {
  if (selectedKeywords.value.length !== 2) return '-'

  const data1 = props.timelineData.find(item => item.keyword === selectedKeywords.value[0])
  const data2 = props.timelineData.find(item => item.keyword === selectedKeywords.value[1])

  if (!data1 || !data2) return '-'

  // 构建日期对齐的数据
  const allDates = new Set()
  data1.timeline.forEach(point => allDates.add(point.date))
  data2.timeline.forEach(point => allDates.add(point.date))
  const dates = Array.from(allDates).sort()

  const dateMap1 = {}
  const dateMap2 = {}
  data1.timeline.forEach(point => { dateMap1[point.date] = point.count })
  data2.timeline.forEach(point => { dateMap2[point.date] = point.count })

  const x = dates.map(date => dateMap1[date] || 0)
  const y = dates.map(date => dateMap2[date] || 0)

  // 计算皮尔逊相关系数
  const n = x.length
  const sumX = x.reduce((a, b) => a + b, 0)
  const sumY = y.reduce((a, b) => a + b, 0)
  const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0)
  const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0)
  const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0)

  const numerator = n * sumXY - sumX * sumY
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY))

  if (denominator === 0) return '0.00'

  const r = numerator / denominator
  return r.toFixed(3)
})

// 获取相关性等级样式
const getCorrelationClass = () => {
  const r = parseFloat(correlationCoefficient.value)
  if (isNaN(r)) return ''
  
  const absR = Math.abs(r)
  if (absR >= 0.8) return 'strong-correlation'
  if (absR >= 0.5) return 'moderate-correlation'
  return 'weak-correlation'
}

// 获取相关性描述
const getCorrelationDescription = () => {
  const r = parseFloat(correlationCoefficient.value)
  if (isNaN(r)) return ''

  const absR = Math.abs(r)
  let strength = ''
  if (absR >= 0.8) strength = '强'
  else if (absR >= 0.5) strength = '中等'
  else strength = '弱'

  const direction = r > 0 ? '正' : '负'

  return `两个关键词呈现${strength}${direction}相关关系。${r > 0 ? '当一个关键词热度上升时，另一个也倾向于上升。' : '当一个关键词热度上升时，另一个倾向于下降。'}`
}

// 处理窗口大小变化
const handleResize = () => {
  chartInstance?.resize()
}

// 监听数据变化
watch(() => props.timelineData, () => {
  updateChart()
}, { deep: true })

watch(() => selectedKeywords.value, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.keyword-trend-comparison { width: 100%; }

.keyword-selector { margin-bottom: 20px; }

.chart-container { width: 100%; height: 400px; }

.analysis-panel { margin-top: 20px; }

.stat-card {
  background: rgba(255, 252, 248, 0.9) !important;
  border: 1px solid var(--border-card) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-card) !important;
}

.stat-header {
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 700;
  color: var(--accent-indigo);
  margin-bottom: 14px;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-subtle);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-subtle);
}
.stat-item:last-child { border-bottom: none; }

.stat-label { font-size: 12px; color: var(--text-muted); }

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-indigo);
  font-family: 'DM Sans', sans-serif;
  letter-spacing: -0.5px;
}

.correlation-card {
  background: rgba(255, 252, 248, 0.9) !important;
  border: 1px solid var(--border-card) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-card) !important;
}

.card-header { font-weight: 600; color: var(--text-primary); font-family: 'Noto Serif SC', serif; }

.correlation-content { padding: 10px 0; }

.correlation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.correlation-label { font-size: 13px; color: var(--text-muted); }

.correlation-value {
  font-size: 28px;
  font-weight: 700;
  font-family: 'DM Sans', sans-serif;
  letter-spacing: -1px;
}

.strong-correlation   { color: var(--accent-sage); }
.moderate-correlation { color: var(--accent-coral); }
.weak-correlation     { color: var(--text-muted); }

.correlation-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.7;
  padding: 12px 14px;
  background: rgba(59, 79, 158, 0.04);
  border: 1px solid rgba(59, 79, 158, 0.1);
  border-radius: 8px;
}
</style>
