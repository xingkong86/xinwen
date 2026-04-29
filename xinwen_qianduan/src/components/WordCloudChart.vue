<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 动态导入词云插件
let wordCloudLoaded = false

const loadWordCloud = async () => {
  if (!wordCloudLoaded) {
    try {
      await import('echarts-wordcloud')
      wordCloudLoaded = true
    } catch (error) {
      console.error('词云插件加载失败:', error)
    }
  }
}

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
const initChart = async () => {
  if (chartRef.value) {
    // 先加载词云插件
    await loadWordCloud()
    chartInstance = echarts.init(chartRef.value)
    
    // 添加点击事件
    chartInstance.on('click', (params) => {
      if (params.componentType === 'series') {
        emit('keyword-click', params.name)
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

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      show: true,
      backgroundColor: 'rgba(250,247,242,0.97)',
      borderColor: 'rgba(180,165,150,0.4)',
      borderWidth: 1,
      textStyle: { color: '#1a1714', fontSize: 12 },
      extraCssText: 'box-shadow: 0 4px 16px rgba(30,20,10,0.1);',
      formatter: (params) => `${params.name}: ${params.value} 次`
    },
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      left: 'center',
      top: 'center',
      width: '90%',
      height: '90%',
      right: null,
      bottom: null,
      sizeRange: [14, 60],
      rotationRange: [-60, 60],
      rotationStep: 30,
      gridSize: 8,
      drawOutOfBound: false,
      layoutAnimation: true,
      textStyle: {
        fontFamily: 'Noto Sans SC, sans-serif',
        fontWeight: 'bold',
        color: function () {
          const colors = [
            '#3b4f9e', '#e05c4b', '#c8913a', '#5a7a68', '#7c4d8a',
            '#4a63b5', '#c97060', '#b07828', '#6a9078', '#9060a0',
            '#2e3f80', '#d04838', '#a87520', '#4a6858', '#6a3d78'
          ]
          return colors[Math.floor(Math.random() * colors.length)]
        }
      },
      emphasis: {
        focus: 'self',
        textStyle: {
          textShadowBlur: 10,
          textShadowColor: 'rgba(59, 79, 158, 0.4)'
        }
      },
      data: props.chartData
    }]
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

onMounted(async () => {
  await initChart()
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
  height: 400px;
}
</style>
