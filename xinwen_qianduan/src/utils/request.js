import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  // 这里把原本的 '' 替换成了你后端的真实地址
  baseURL: import.meta.env.PROD ? 'https://xinwen-production.up.railway.app' : 'http://localhost:8000', 
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
