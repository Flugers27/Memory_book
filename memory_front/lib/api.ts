import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

console.log('[API Config] API_URL:', API_URL)

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерцептор для добавления токена и логирования
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, config.params ? { params: config.params } : '')
  }
  return config
})

// Интерцептор для обновления токена при истечении и логирования
api.interceptors.response.use(
  (response) => {
    if (typeof window !== 'undefined') {
      console.log(`[API Response] ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`)
    }
    return response
  },
  async (error) => {
    if (typeof window !== 'undefined') {
      console.error('[API Error]', error.message, error.response?.status, error.config?.url)
    }
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
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
        window.location.href = '/login'
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
  // Создать страницу (требует авторизации)
  createPage: (data: any) =>
    api.post('/memory/memory_page', data).then((res) => res.data),
  // Обновить страницу
  updatePage: (agent_id: string, data: any) =>
    api.put(`/memory/memory_page/${agent_id}`, data).then((res) => res.data),
  // Удалить страницу
  deletePage: (agent_id: string) =>
    api.delete(`/memory/memory_page/${agent_id}`).then((res) => res.data),
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