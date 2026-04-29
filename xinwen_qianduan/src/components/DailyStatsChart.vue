<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  chartData: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null

// 纸墨·清风 主题颜色
const THEME = {
  indigo:  '#3b4f9e',
  coral:   '#e05c4b',
  gold:    '#c8913a',
  sage:    '#5a7a68',
  plum:    '#7c4d8a',
  text:    '#5c504a',
  muted:   '#a09590',
  grid:    'rgba(59, 79, 158, 0.07)',
  bg:      'transparent',
}

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value, null, { renderer: 'canvas' })
    updateChart()
  }
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) return

  // 处理空数据情况
  if (!props.chartData || props.chartData.length === 0) {
    chartInstance.clear()
    chartInstance.setOption({
      backgroundColor: THEME.bg,
      title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: THEME.muted, fontSize: 14 } }
    })
    return
  }

  const dates = props.chartData.map(item => item.date)
  const counts = props.chartData.map(item => item.count)

  const option = {
    backgroundColor: THEME.bg,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(250,247,242,0.97)',
      borderColor: 'rgba(180,165,150,0.4)',
      borderWidth: 1,
      textStyle: { color: '#1a1714', fontSize: 12 },
      axisPointer: { type: 'line', lineStyle: { color: 'rgba(59,79,158,0.25)', type: 'dashed' } },
      extraCssText: 'box-shadow: 0 4px 16px rgba(30,20,10,0.1);'
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: 'rgba(180,165,150,0.4)' } },
      axisLabel: { color: THEME.text, fontSize: 11 },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: THEME.text, fontSize: 11 },
      splitLine: { lineStyle: { color: THEME.grid, type: 'dashed' } }
    },
    series: [
      {
        name: '新闻数量',
        type: 'line',
        data: counts,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 79, 158, 0.18)' },
            { offset: 1, color: 'rgba(59, 79, 158, 0.01)' }
          ])
        },
        lineStyle: { color: THEME.indigo, width: 2.5 },
        itemStyle: { color: THEME.indigo, borderColor: '#faf7f2', borderWidth: 2 }
      }
    ]
  }

  chartInstance.setOption(option, true)
}

// 处理窗口大小变化
const handleResize = () => {
  chartInstance?.resize()
}

// 监听 chartData 变化
watch(() => props.chartData, () => {
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
.chart-container {
  width: 100%;
  height: 350px;
}
</style>
