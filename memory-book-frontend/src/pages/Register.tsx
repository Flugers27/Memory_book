import { useState } from "react";
import { register } from "../api/auth.api";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async () => {
    try {
      await register(email, password);
      alert("Регистрация прошла успешно!");
      window.location.href = "/login";
    } catch {
      alert("Ошибка регистрации");
    }
  };

  return (
    <div>
      <h2>Регистрация</h2>
      <input placeholder="Email" onChange={e => setEmail(e.target.value)} />
      <input type="password" placeholder="Пароль" onChange={e => setPassword(e.target.value)} />
      <button onClick={handleRegister}>Зарегистрироваться</button>
    </div>
  );
}
