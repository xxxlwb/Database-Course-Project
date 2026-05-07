import axios from 'axios'

const client = axios.create({ baseURL: '/api', timeout: 30000 })

client.interceptors.request.use((cfg) => {
  const tok = localStorage.getItem('nkg_token')
  if (tok) cfg.headers.Authorization = `Bearer ${tok}`
  return cfg
})

client.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('nkg_token')
      localStorage.removeItem('nkg_user')
      if (location.pathname !== '/login') location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default client
