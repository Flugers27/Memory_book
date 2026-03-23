import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getUserProfile, updateProfile } from "../api/auth.api";

export default function Profile() {
  const [user, setUser] = useState<{ email: string; username?: string; full_name?: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await getUserProfile();
      setUser(data);
      setFullName(data.full_name || "");
      setUsername(data.username || "");
    } catch (error) {
      console.error("Failed to fetch profile", error);
      alert("Ошибка загрузки профиля");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await updateProfile({ full_name: fullName, username });
      setUser({ ...user!, full_name: fullName, username });
      setEditMode(false);
      alert("Профиль обновлен");
    } catch (error) {
      console.error("Update failed", error);
      alert("Ошибка обновления профиля");
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (!user) return <div>Пользователь не найден</div>;

  return (
    <div style={{ maxWidth: 600, margin: "50px auto", padding: 20, border: "1px solid #ccc", borderRadius: 8 }}>
      <h2>Мой профиль</h2>
      <div>
        <p><strong>Email:</strong> {user.email}</p>
        {editMode ? (
          <>
            <div>
              <label>Полное имя:</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                style={{ width: "100%", marginBottom: 10 }}
              />
            </div>
            <div>
              <label>Имя пользователя:</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{ width: "100%", marginBottom: 10 }}
              />
            </div>
            <button onClick={handleSave} style={{ marginRight: 10 }}>Сохранить</button>
            <button onClick={() => setEditMode(false)}>Отмена</button>
          </>
        ) : (
          <>
            <p><strong>Полное имя:</strong> {user.full_name || "Не указано"}</p>
            <p><strong>Имя пользователя:</strong> {user.username || "Не указано"}</p>
            <button onClick={() => setEditMode(true)} style={{ marginRight: 10 }}>Редактировать</button>
            <button onClick={() => navigate("/")}>На главную</button>
          </>
        )}
      </div>
    </div>
  );
}