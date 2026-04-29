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

const emit = defineEmits(['keyword-click'])

const chartRef = ref(null)
let chartInstance = null

const THEME = {
  indigo: '#3b4f9e', coral: '#e05c4b', gold: '#c8913a', sage: '#5a7a68',
  text: '#5c504a', muted: '#a09590',
  grid: 'rgba(59, 79, 158, 0.07)', bg: 'transparent'
}

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value, null, { renderer: 'canvas' })
    chartInstance.on('click', (params) => {
      if (params.componentType === 'series') emit('keyword-click', params.name)
    })
    updateChart()
  }
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) return

  if (!props.chartData || props.chartData.length === 0) {
    chartInstance.clear()
    chartInstance.setOption({ backgroundColor: THEME.bg, title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: THEME.muted, fontSize: 14 } } })
    return
  }

  // 取前20个关键词
  const topData = props.chartData.slice(0, 20)
  const keywords = topData.map(item => item.name)
  const values = topData.map(item => item.value)

  const option = {
    backgroundColor: THEME.bg,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(250,247,242,0.97)',
      borderColor: 'rgba(180,165,150,0.4)',
      borderWidth: 1,
      textStyle: { color: '#1a1714', fontSize: 12 },
      extraCssText: 'box-shadow: 0 4px 16px rgba(30,20,10,0.1);'
    },
    grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: THEME.text, fontSize: 11 },
      splitLine: { lineStyle: { color: THEME.grid, type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: keywords,
      axisLine: { lineStyle: { color: 'rgba(180,165,150,0.4)' } },
      axisTick: { show: false },
      axisLabel: { color: THEME.text, interval: 0, fontSize: 12 }
    },
    series: [
      {
        name: '出现次数',
        type: 'bar',
        data: values,
        cursor: 'pointer',
        barMaxWidth: 18,
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: 'rgba(59, 79, 158, 0.35)' },
            { offset: 1, color: '#3b4f9e' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: 'rgba(224, 92, 75, 0.4)' },
              { offset: 1, color: '#e05c4b' }
            ])
          }
        },
        label: {
          show: true,
          position: 'right',
          valueAnimation: true,
          color: THEME.muted,
          fontSize: 11
        }
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
  height: 500px;
}
</style>
