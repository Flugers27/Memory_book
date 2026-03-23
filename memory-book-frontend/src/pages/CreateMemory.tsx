import { useState } from "react";
import api from "../api/axios";

export default function CreateMemory() {
  const [step, setStep] = useState(1); // 1 - создание агента, 2 - создание страницы
  const [agentId, setAgentId] = useState<string | null>(null);
  const [agentData, setAgentData] = useState({
    full_name: "",
    gender: "",
    birth_date: "",
    death_date: "",
    place_of_birth: "",
    place_of_death: "",
    avatar_url: "",
    is_human: true,
  });
  const [pageData, setPageData] = useState({
    epitaph: "",
    biography: [{ title: "", info: "", titles: [] }],
    is_public: false,
    is_draft: false,
    agent_id: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleAgentChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setAgentData(prev => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handlePageChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setPageData(prev => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleBiographyChange = (index: number, field: string, value: string) => {
    const newBiography = [...pageData.biography];
    newBiography[index] = { ...newBiography[index], [field]: value };
    setPageData({ ...pageData, biography: newBiography });
  };

  const createAgent = async () => {
    setLoading(true);
    try {
      const res = await api.post("/agent/add", agentData);
      const { id_agent } = res.data;
      setAgentId(id_agent);
      setPageData(prev => ({ ...prev, agent_id: id_agent }));
      setStep(2);
      setMessage("Агент успешно создан! Теперь создайте страницу.");
    } catch (err: any) {
      setMessage(`Ошибка создания агента: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const createPage = async () => {
    if (!agentId) {
      setMessage("Сначала создайте агента.");
      return;
    }
    setLoading(true);
    try {
      await api.post("/page/add", { ...pageData, agent_id: agentId });
      setMessage("Страница успешно создана!");
      // Сброс формы или переход куда-то
    } catch (err: any) {
      setMessage(`Ошибка создания страницы: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      <h2>Создание страницы памяти</h2>
      {message && <div style={{ padding: "10px", background: message.includes("успешно") ? "#d4edda" : "#f8d7da", border: "1px solid #c3e6cb", borderRadius: "5px" }}>{message}</div>}
      
      {step === 1 ? (
        <div>
          <h3>Шаг 1: Создание агента (памятной личности)</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
            <div>
              <label>Полное имя *</label>
              <input name="full_name" value={agentData.full_name} onChange={handleAgentChange} required />
            </div>
            <div>
              <label>Пол</label>
              <select name="gender" value={agentData.gender} onChange={handleAgentChange}>
                <option value="">Не указан</option>
                <option value="M">Мужской</option>
                <option value="F">Женский</option>
              </select>
            </div>
            <div>
              <label>Дата рождения</label>
              <input type="date" name="birth_date" value={agentData.birth_date} onChange={handleAgentChange} />
            </div>
            <div>
              <label>Дата смерти</label>
              <input type="date" name="death_date" value={agentData.death_date} onChange={handleAgentChange} />
            </div>
            <div>
              <label>Место рождения</label>
              <input name="place_of_birth" value={agentData.place_of_birth} onChange={handleAgentChange} />
            </div>
            <div>
              <label>Место смерти</label>
              <input name="place_of_death" value={agentData.place_of_death} onChange={handleAgentChange} />
            </div>
            <div>
              <label>URL аватара</label>
              <input name="avatar_url" value={agentData.avatar_url} onChange={handleAgentChange} />
            </div>
            <div>
              <label>
                <input type="checkbox" name="is_human" checked={agentData.is_human} onChange={(e) => setAgentData({...agentData, is_human: e.target.checked})} />
                Человек
              </label>
            </div>
          </div>
          <button onClick={createAgent} disabled={loading} style={{ marginTop: "20px" }}>
            {loading ? "Создание..." : "Создать агента"}
          </button>
        </div>
      ) : (
        <div>
          <h3>Шаг 2: Создание страницы памяти</h3>
          <p>Агент создан (ID: {agentId})</p>
          <div>
            <div>
              <label>Эпитафия</label>
              <textarea name="epitaph" value={pageData.epitaph} onChange={handlePageChange} rows={3} />
            </div>
            <div>
              <label>Публичная страница</label>
              <input type="checkbox" name="is_public" checked={pageData.is_public} onChange={handlePageChange} />
            </div>
            <div>
              <label>Черновик</label>
              <input type="checkbox" name="is_draft" checked={pageData.is_draft} onChange={handlePageChange} />
            </div>
            <div>
              <h4>Биография</h4>
              {pageData.biography.map((bio, index) => (
                <div key={index} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "10px" }}>
                  <label>Заголовок</label>
                  <input value={bio.title} onChange={(e) => handleBiographyChange(index, "title", e.target.value)} />
                  <label>Информация</label>
                  <textarea value={bio.info} onChange={(e) => handleBiographyChange(index, "info", e.target.value)} />
                  {/* Вложенные titles не реализованы для простоты */}
                </div>
              ))}
              <button onClick={() => setPageData({...pageData, biography: [...pageData.biography, { title: "", info: "", titles: [] }]})}>
                Добавить раздел биографии
              </button>
            </div>
          </div>
          <div style={{ marginTop: "20px" }}>
            <button onClick={() => setStep(1)}>Назад к агенту</button>
            <button onClick={createPage} disabled={loading} style={{ marginLeft: "10px" }}>
              {loading ? "Создание..." : "Создать страницу"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
