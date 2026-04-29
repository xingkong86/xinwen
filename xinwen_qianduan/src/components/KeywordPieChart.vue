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

const THEME = {
  text: '#5c504a', muted: '#a09590', bg: 'transparent',
  pieColors: [
    '#3b4f9e', '#e05c4b', '#5a7a68', '#c8913a', '#7c4d8a',
    '#b06040', '#4a7890', '#9a5468', '#6a7838', '#8a6050'
  ]
}

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

  // 处理空数据情况
  if (!props.chartData || props.chartData.length === 0) {
    chartInstance.clear()
    chartInstance.setOption({ backgroundColor: THEME.bg, title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: THEME.muted, fontSize: 14 } } })
    return
  }

  // 取前8个关键词，剩余的聚合为"其他"
  const topData = props.chartData.slice(0, 8).map(item => ({
    name: item.name,
    value: item.value
  }))
  
  // 计算"其他"的总和
  if (props.chartData.length > 8) {
    const othersSum = props.chartData
      .slice(8)
      .reduce((sum, item) => sum + item.value, 0)
    
    if (othersSum > 0) {
      topData.push({
        name: '其他',
        value: othersSum
      })
    }
  }

  const option = {
    backgroundColor: THEME.bg,
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} 次 ({d}%)',
      backgroundColor: 'rgba(250,247,242,0.97)',
      borderColor: 'rgba(180,165,150,0.4)',
      borderWidth: 1,
      textStyle: { color: '#1a1714', fontSize: 12 },
      extraCssText: 'box-shadow: 0 4px 16px rgba(30,20,10,0.1);'
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: '2%',
      top: 'middle',
      textStyle: { fontSize: 12, color: THEME.text, overflow: 'truncate', width: 80 },
      pageTextStyle: { color: THEME.text },
      pageIconColor: '#3b4f9e',
      itemGap: 10, itemWidth: 10, itemHeight: 10,
      formatter: (name) => name.length > 8 ? name.substring(0, 8) + '...' : name
    },
    series: [
      {
        name: '关键词占比',
        type: 'pie',
        radius: ['50%', '78%'],
        center: ['40%', '50%'],
        roseType: 'area',
        itemStyle: {
          borderRadius: 6,
          borderColor: 'rgba(245, 240, 234, 0.9)',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            formatter: '{b}\n{d}%',
            color: '#1a1714',
            fontFamily: 'DM Sans'
          },
          itemStyle: {
            shadowBlur: 16,
            shadowOffsetX: 0,
            shadowColor: 'rgba(30, 20, 10, 0.2)'
          }
        },
        labelLine: { show: false },
        data: topData,
        color: THEME.pieColors
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
  height: 450px; /* 增加高度 */
}
</style>
