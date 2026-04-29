import axios from 'axios'

// 创建 axios 实例
// 改造后
const request = axios.create({
  baseURL: import.meta.env.PROD ? '' : 'http://localhost:8000', // 本地开发用 8000，线上直接请求当前域名
  timeout: 10000
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
  (error) => {
    console.error('响应错误:', error)
    return Promise.reject(error)
  }
)

export default request
