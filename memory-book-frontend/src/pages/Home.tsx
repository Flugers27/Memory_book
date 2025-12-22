import { Link } from "react-router-dom";

export default function Home() {
  const token = localStorage.getItem("access_token");

  return (
    <div>
      <h1>Memory Book</h1>
      <p>Добро пожаловать в Книгу памяти.</p>
      <Link to="/public">
        <button>Посмотреть публичные страницы памяти</button>
      </Link>

      {token && (
        <div>
          <Link to="/create">
            <button>Создать страницу памяти</button>
          </Link>
          <Link to="/my-pages">
            <button>Мои страницы памяти</button>
          </Link>
        </div>
      )}
    </div>
  );
}
