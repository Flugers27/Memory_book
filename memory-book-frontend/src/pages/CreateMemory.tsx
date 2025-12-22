import { useState } from "react";
import { createMemory } from "../api/memory.api";

export default function CreateMemory() {
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [deathDate, setDeathDate] = useState("");
  const [epitaph, setEpitaph] = useState("");

  const handleCreate = async () => {
    try {
      await createMemory({ full_name: fullName, birth_date: birthDate, death_date: deathDate, epitaph });
      alert("Страница памяти создана!");
    } catch {
      alert("Ошибка при создании страницы");
    }
  };

  return (
    <div>
      <h2>Создать страницу памяти</h2>
      <input placeholder="ФИО" onChange={e => setFullName(e.target.value)} />
      <input type="date" placeholder="Дата рождения" onChange={e => setBirthDate(e.target.value)} />
      <input type="date" placeholder="Дата смерти" onChange={e => setDeathDate(e.target.value)} />
      <textarea placeholder="Эпитафия" onChange={e => setEpitaph(e.target.value)} />
      <button onClick={handleCreate}>Создать</button>
    </div>
  );
}
