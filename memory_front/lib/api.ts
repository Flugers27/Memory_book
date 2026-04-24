import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Интерцептор для добавления токена
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Интерцептор для обновления токена при 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const { access_token } = response.data;
        localStorage.setItem("access_token", access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Если refresh не удался, разлогиниваем
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data: { email: string; password: string; username?: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
  logout: () => api.post("/auth/logout"),
  refresh: (refreshToken: string) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),
  getProfile: () => api.get("/auth/me"),
};

export const memoryAPI = {
  getMemories: (params?: { page?: number; limit?: number; tag?: string }) =>
    api.get("/memories", { params }),
  getMemory: (id: string) => api.get(`/memories/${id}`),
  createMemory: (data: { title: string; content: string; tags?: string[] }) =>
    api.post("/memories", data),
  updateMemory: (id: string, data: Partial<{ title: string; content: string; tags: string[] }>) =>
    api.put(`/memories/${id}`, data),
  deleteMemory: (id: string) => api.delete(`/memories/${id}`),
};

export const accessAPI = {
  getSharedMemories: () => api.get("/access/shared"),
  shareMemory: (memoryId: string, userId: string, permission: "read" | "write") =>
    api.post("/access/share", { memory_id: memoryId, user_id: userId, permission }),
  revokeAccess: (accessId: string) => api.delete(`/access/${accessId}`),
};

export default api;