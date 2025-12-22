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
  withCredentials: true, // важно для отправки куки
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

export default api;
