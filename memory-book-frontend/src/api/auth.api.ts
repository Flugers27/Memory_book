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
