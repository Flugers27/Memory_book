import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

console.log('[API Config] API_URL:', API_URL)

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Функция проверки публичного URL
const isPublicUrl = (url: string): boolean => {
  const publicPatterns = [
    '/auth/login',
    '/auth/register',
    '/auth/refresh',
    '/auth/validate',
    '/memory/public_memory_page_list',
    '/memory/public_memory_page/',
    '/docs',
    '/redoc',
    '/openapi.json',
    '/health'
  ]
  return publicPatterns.some(pattern => url.startsWith(pattern))
}

// Интерцептор для добавления токена и логирования
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    console.log(`[API Request Debug] URL: ${config.url}, Token: "${token ? token.substring(0, 10) + '...' : 'null'}", isPublic: ${config.url ? isPublicUrl(config.url) : 'unknown'}`)
    // Не добавляем токен для публичных эндпоинтов
    if (token && config.url && !isPublicUrl(config.url)) {
      config.headers.Authorization = `Bearer ${token}`
      console.log(`[API Request Debug] Added Authorization header for ${config.url}`)
    } else if (!token && config.url && !isPublicUrl(config.url)) {
      console.warn(`[API Request Debug] No token found for private endpoint: ${config.url}`)
      // Если пользователь есть в store, но токена нет, возможно нужно выйти
      const userStr = localStorage.getItem('auth-storage')
      if (userStr) {
        console.warn(`[API Request Debug] User exists in store but no token. Store: ${userStr}`)
      }
    }
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, config.params ? { params: config.params } : '')
  }
  return config
})

// Интерцептор для обновления токена при истечении и логирования
api.interceptors.response.use(
  (response) => {
    if (typeof window !== 'undefined') {
      console.log(`[API Response] ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    }
    return response
  },
  async (error) => {
    if (typeof window !== 'undefined') {
      console.error('[API Error]', error.message, error.response?.status, error.config?.url, error.response?.data)
    }
    const originalRequest = error.config
    // Пропускаем обработку 401 для публичных URL
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url && !isPublicUrl(originalRequest.url)) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) throw new Error('No refresh token')
        const response = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken })
        const { access_token } = response.data
        localStorage.setItem('access_token', access_token)
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/user/login'
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data: { email: string; password: string; name?: string }) =>
    api.post('/auth/register', data).then((res) => res.data),
  login: (data: { email: string; password: string }) => {
    const formData = new URLSearchParams()
    formData.append('username', data.email)
    formData.append('password', data.password)
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }).then((res) => res.data)
  },
  logout: () => api.post('/auth/logout').then((res) => res.data),
  validateToken: (token: string) =>
    api.post('/auth/validate', { token }).then((res) => res.data),
}

export const memoryAPI = {
  // Публичные страницы (без авторизации)
  getPublicPages: (params?: { skip?: number; limit?: number }) =>
    api.get('/memory/public_memory_page_list', { params }).then((res) => res.data),
  // Получить публичную страницу по agent_id
  getPublicPage: (agent_id: string) =>
    api.get(`/memory/public_memory_page/${agent_id}`).then((res) => res.data),
  // Страницы пользователя (требуют авторизации)
  getUserPages: (params?: { skip?: number; limit?: number; is_draft?: boolean }) =>
    api.get('/memory/memory_page_list', { params }).then((res) => res.data),
  // Получить конкретную страницу пользователя по agent_id
  getUserPage: (agent_id: string) =>
    api.get(`/memory/memory_page/${agent_id}`).then((res) => res.data),
  // Алиас для обратной совместимости
  getPage: (agent_id: string) =>
    api.get(`/memory/memory_page/${agent_id}`).then((res) => res.data),
  // Получить агента по ID
  getAgent: (agent_id: string) =>
    api.get(`/memory/agent/${agent_id}`).then((res) => res.data),
  // Обновить агента
  updateAgent: (agent_id: string, data: any) =>
    api.put(`/memory/agent/update/${agent_id}`, data).then((res) => res.data),
  // Получить список страниц агента
  getPageList: (agent_id: string, params?: { skip?: number; limit?: number }) =>
    api.get(`/memory/page_list/${agent_id}`, { params }).then((res) => res.data),
  // Создать агента (требует авторизации)
  createAgent: (data: any) =>
    api.post('/memory/agent/add', data).then((res) => res.data),
  // Создать страницу (требует авторизации)
  createPage: (data: any) =>
    api.post('/memory/page/add', data).then((res) => res.data),
  // Обновить страницу
  updatePage: (page_id: string, data: any) =>
    api.put(`/memory/page/update/${page_id}`, data).then((res) => res.data),
  // Удалить страницу
  deletePage: (page_id: string) =>
    api.delete(`/memory/page/del/${page_id}`).then((res) => res.data),
}

export const accessAPI = {
  grantAccess: (data: { page_id: string; user_id: string; permission: string }) =>
    api.post('/access/grant', data).then((res) => res.data),
  revokeAccess: (data: { page_id: string; user_id: string }) =>
    api.post('/access/revoke', data).then((res) => res.data),
  getAccessList: (page_id: string) =>
    api.get(`/access/list/${page_id}`).then((res) => res.data),
}

export default api