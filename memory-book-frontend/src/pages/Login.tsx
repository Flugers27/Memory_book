import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/auth.api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const data = await login(email, password);
      console.log("Login response:", data);

      if (data.access_token) {
        // Сохраняем токены
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);

        alert("Успешный вход");
        navigate("/public_memory_page_list"); // перенаправление на публичный список
      } else {
        alert("Ошибка: токен не получен");
      }
    } catch (err: any) {
      console.error("Login error:", err.response || err);
      alert("Ошибка входа: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "50px auto", textAlign: "center" }}>
      <h2>Вход в Memory Book</h2>
      <input
        style={{ width: "100%", marginBottom: 10 }}
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        style={{ width: "100%", marginBottom: 10 }}
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin} style={{ width: "100%", padding: 8 }}>
        Войти
      </button>
    </div>
  );
}
