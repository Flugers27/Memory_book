import { Link } from "react-router-dom";

export default function Navbar() {
  const token = localStorage.getItem("access_token");

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/";
  };

  return (
    <nav>
      <Link to="/">Главная</Link> | <Link to="/public">Публичные страницы</Link>
      {!token && (
        <>
          {" | "}
          <Link to="/login">Вход</Link> | <Link to="/register">Регистрация</Link>
        </>
      )}
      {token && (
        <>
          {" | "}
          <Link to="/create">Создать страницу</Link> | <Link to="/my-pages">Мои страницы</Link> |{" "}
          <button onClick={handleLogout}>Выйти</button>
        </>
      )}
    </nav>
  );
}
