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

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    
    // 添加点击事件
    chartInstance.on('click', (params) => {
      if (params.componentType === 'series' && params.seriesName !== '全部') {
        emit('keyword-click', params.seriesName)
      }
    })
    
    updateChart()
  }
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) return

  if (!props.chartData || props.chartData.length === 0) {
    chartInstance.clear()
    chartInstance.setOption({
      backgroundColor: 'transparent',
      title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#4a6a8a', fontSize: 14 } }
    })
    return
  }

  // 提取所有日期（合并所有关键词的日期）
  const allDates = new Set()
  props.chartData.forEach(item => {
    item.timeline.forEach(point => {
      allDates.add(point.date)
    })
  })
  const dates = Array.from(allDates).sort()

  // 构建系列数据
  const series = props.chartData.map((item, index) => {
    // 创建日期到数量的映射
    const dateMap = {}
    item.timeline.forEach(point => {
      dateMap[point.date] = point.count
    })

    // 填充完整的日期序列（缺失的日期填0）
    const data = dates.map(date => dateMap[date] || 0)

    return {
      name: item.keyword,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: data,
      emphasis: {
        focus: 'series',
        lineStyle: {
          width: 3
        }
      },
      lineStyle: {
        width: 2
      },
      areaStyle: {
        opacity: 0.1
      }
    }
  })

  const option = {
    backgroundColor: 'transparent',
    title: {
      text: '热点事件时间线',
      subtext: '关键词热度随时间的变化趋势',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#1a1714', fontFamily: 'Noto Serif SC, serif' },
      subtextStyle: { fontSize: 11, color: '#a09590' }
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
        const sorted = params.sort((a, b) => b.value - a.value)
        sorted.forEach(item => {
          if (item.value > 0) {
            result += `<div style="display:flex;align-items:center;margin:3px 0">
              <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${item.color};margin-right:6px"></span>
              <span style="flex:1;color:#5c504a">${item.seriesName}</span>
              <span style="font-weight:bold;margin-left:10px;color:#1a1714">${item.value} 次</span>
            </div>`
          }
        })
        return result
      }
    },
    legend: {
      type: 'scroll',
      orient: 'horizontal',
      bottom: 10,
      left: 'center',
      textStyle: { fontSize: 12, color: '#5c504a' },
      pageIconColor: '#3b4f9e',
      pageTextStyle: { color: '#5c504a' }
    },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '18%', containLabel: true },
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
      splitLine: { lineStyle: { color: 'rgba(59, 79, 158, 0.07)', type: 'dashed' } }
    },
    series: series,
    color: ['#3b4f9e', '#e05c4b', '#5a7a68', '#c8913a', '#7c4d8a', '#b06040', '#4a7890', '#9a5468', '#6a7838', '#8a6050'],
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 20,
        bottom: 50,
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
