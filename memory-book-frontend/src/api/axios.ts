import axios from "axios";

// Функция для чтения куки
function getCookie(name: string) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()!.split(';').shift();
  return null;
}

const api = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true, // важно для отправки куки.
});

// Берём CSRF-токен из куки и добавляем в заголовки
const csrfToken = getCookie("csrf_token");
if (csrfToken) {
  api.defaults.headers.common["X-CSRF-Token"] = csrfToken;
}

// Добавляем Authorization из localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Добавляем interceptor для обработки 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Если ошибка 401 и это не запрос на обновление токена
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Если это сам запрос /auth/refresh, не пытаемся обновлять
      if (originalRequest.url?.includes('/auth/refresh')) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(error);
      }
      originalRequest._retry = true;
      try {
        // Пытаемся обновить токен
        const { refreshToken } = await import('./auth.api');
        await refreshToken();
        // Повторяем запрос с новым токеном
        const newToken = localStorage.getItem("access_token");
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Если refresh не удался, перенаправляем на логин
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
