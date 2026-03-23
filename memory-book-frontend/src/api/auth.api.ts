import api from "./axios";

export const login = async (email: string, password: string) => {
  const data = new URLSearchParams();
  data.append("username", email);
  data.append("password", password);

  const res = await api.post("/auth/login", data, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  localStorage.setItem("access_token", res.data.access_token);
  localStorage.setItem("refresh_token", res.data.refresh_token);

  return res.data;
};

export const register = async (email: string, password: string) => {
  const data = { email, password };
  const res = await api.post("/auth/register", data, {
    headers: { "Content-Type": "application/json" },
  });
  return res.data;
};

export const getUserProfile = async () => {
  const res = await api.get("/auth/users/me");
  return res.data;
};

export const updateProfile = async (profileData: { full_name?: string; username?: string }) => {
  const res = await api.put("/auth/users/me", profileData);
  return res.data;
};

export const refreshToken = async () => {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) throw new Error("No refresh token");
  const res = await api.post("/auth/refresh", { refresh_token: refresh });
  localStorage.setItem("access_token", res.data.access_token);
  localStorage.setItem("refresh_token", res.data.refresh_token);
  return res.data;
};

export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
};
