import { useEffect, useState } from "react";
import { getMyMemoryPages } from "../api/memory.api";
import { Link } from "react-router-dom";

export default function MyMemoryList() {
  const [pages, setPages] = useState<any[]>([]);

  useEffect(() => {
    getMyMemoryPages().then(setPages);
  }, []);

  return (
    <div>
      <h2>Мои страницы памяти</h2>
      {pages.length === 0 ? (
        <p>У вас пока нет страниц памяти.</p>
      ) : (
        <table border={1} style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>ID агента</th>
              <th>Имя</th>
              <th>Пол</th>
              <th>Дата рождения</th>
              <th>Дата смерти</th>
              <th>Публичная</th>
              <th>Черновик</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {pages.map((item) => {
              const agent = item.agent;
              const page = item.pages[0]; // берем первую страницу (может быть несколько)
              return (
                <tr key={agent.id_agent}>
                  <td>{agent.id_agent}</td>
                  <td>{agent.full_name}</td>
                  <td>{agent.gender === 'M' ? 'Мужской' : 'Женский'}</td>
                  <td>{agent.birth_date}</td>
                  <td>{agent.death_date || '—'}</td>
                  <td>{page?.is_public ? 'Да' : 'Нет'}</td>
                  <td>{page?.is_draft ? 'Да' : 'Нет'}</td>
                  <td>
                    <Link to={`/memory/${agent.id_agent}`}>
                      <button>Открыть страницу памяти</button>
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
