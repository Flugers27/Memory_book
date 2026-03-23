import { Link } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const token = localStorage.getItem("access_token");

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/";
  };

  return (
    <nav className="navbar">
      <div className="nav-links">
        <Link to="/">Главная</Link>
        <Link to="/public">Публичные страницы</Link>
        {!token ? (
          <>
            <Link to="/login">Вход</Link>
            <Link to="/register">Регистрация</Link>
          </>
        ) : (
          <>
            <Link to="/create">Создать страницу</Link>
            <Link to="/my-pages">Мои страницы</Link>
            <Link to="/profile">Профиль</Link>
            <button className="logout-btn" onClick={handleLogout}>Выйти</button>
          </>
        )}
      </div>
    </nav>
  );
}
