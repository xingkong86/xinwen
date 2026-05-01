import axios from 'axios'

const RETRYABLE_STATUS = new Set([429, 500, 502, 503, 504])

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

// 创建 axios 实例
const request = axios.create({
  // 这里把原本的 '' 替换成了你后端的真实地址
  baseURL: import.meta.env.PROD ? 'https://xinwen-production.up.railway.app' : 'http://localhost:8000', 
  timeout: 60000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const config = error.config || {}
    const status = error.response?.status
    const shouldRetry = !config.__retry && (!status || RETRYABLE_STATUS.has(status))

    if (shouldRetry) {
      config.__retry = true
      // 首次失败后做一次短退避重试，降低跨地域网络抖动造成的瞬时失败
      await sleep(800)
      return request(config)
    }

    console.error('响应错误:', error)
    return Promise.reject(error)
  }
)

export default request
