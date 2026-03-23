import { useParams, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMemoryPage, getPrivateMemoryPage } from "../api/memory.api";

export default function MemoryPage() {
  const { id } = useParams();
  const location = useLocation();
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const isPublicRoute = location.pathname.startsWith('/public');

  useEffect(() => {
    console.log('MemoryPage id:', id, 'public?', isPublicRoute);
    if (!id) return;

    const fetchData = isPublicRoute ? getMemoryPage : getPrivateMemoryPage;
    fetchData(id)
      .then((res) => {
        console.log('Response:', res);
        setData(res);
      })
      .catch((err) => {
        console.error('Error fetching memory page:', err);
        setError(err.message);
      });
  }, [id, isPublicRoute]);

  if (error) return <p>Ошибка: {error}</p>;
  if (!data) return <p>Загрузка...</p>;

  // Структура ответа отличается между публичным и приватным
  // Публичный: { id_agent, full_name, ... page? }
  // Приватный: { agent, pages }
  let agent, pages;
  if (isPublicRoute) {
    // публичный ответ: данные агента на верхнем уровне
    agent = data;
    pages = data.page ? [data.page] : [];
  } else {
    agent = data.agent;
    pages = data.pages || [];
  }
  const page = pages?.[0];

  return (
    <div style={{ padding: "20px" }}>
      <h2>{agent.full_name}</h2>
      <p><strong>Пол:</strong> {agent.gender === 'M' ? 'Мужской' : 'Женский'}</p>
      <p><strong>Дата рождения:</strong> {agent.birth_date}</p>
      <p><strong>Дата смерти:</strong> {agent.death_date || 'Не указана'}</p>
      <p><strong>Место рождения:</strong> {agent.place_of_birth || 'Не указано'}</p>
      <p><strong>Место смерти:</strong> {agent.place_of_death || 'Не указано'}</p>
      <p><strong>Аватар:</strong> {agent.avatar_url ? <img src={agent.avatar_url} alt="Avatar" style={{ maxWidth: '200px' }} /> : 'Нет'}</p>
      <p><strong>Тип:</strong> {agent.is_human ? 'Человек' : 'Животное'}</p>
      <p><strong>ID агента:</strong> {agent.id_agent}</p>
      
      {page ? (
        <>
          <h3>Страница памяти</h3>
          <p><strong>Эпитафия:</strong> {page.epitaph}</p>
          <p><strong>Публичная:</strong> {page.is_public ? 'Да' : 'Нет'}</p>
          <p><strong>Черновик:</strong> {page.is_draft ? 'Да' : 'Нет'}</p>
          <p><strong>ID страницы:</strong> {page.id_page}</p>
          <p><strong>Создана:</strong> {new Date(page.created_at).toLocaleString()}</p>
          <p><strong>Обновлена:</strong> {new Date(page.updated_at).toLocaleString()}</p>
          
          <h3>Биография</h3>
          {page.biography && page.biography.length > 0 ? (
            page.biography.map((bio: any, index: number) => (
              <div key={index}>
                <h4>{bio.title}</h4>
                <p>{bio.info}</p>
                {bio.titles && bio.titles.length > 0 && (
                  <ul>
                    {bio.titles.map((sub: any, subIndex: number) => (
                      <li key={subIndex}>
                        <strong>{sub.title}:</strong> {sub.info}
                        {sub.titles && sub.titles.length > 0 && (
                          <ul>
                            {sub.titles.map((subsub: any, subsubIndex: number) => (
                              <li key={subsubIndex}>{subsub.title}: {subsub.info}</li>
                            ))}
                          </ul>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))
          ) : (
            <p>Биография отсутствует.</p>
          )}
        </>
      ) : (
        <p>Страница не найдена.</p>
      )}
      {/* Здесь позже можно добавить медиа */}
    </div>
  );
}
