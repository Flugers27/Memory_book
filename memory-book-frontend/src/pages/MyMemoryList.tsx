import { useEffect, useState } from "react";
import { getMyMemoryPages } from "../api/memory.api";
import MemoryCard from "../components/MemoryCard";

export default function MyMemoryList() {
  const [pages, setPages] = useState<any[]>([]);

  useEffect(() => {
    getMyMemoryPages().then(setPages);
  }, []);

  return (
    <div>
      <h2>Мои страницы памяти</h2>
      {pages.length === 0 && <p>У вас пока нет страниц памяти.</p>}
      {pages.map((page) => (
        <MemoryCard key={page.id_agent} memory={page} />
      ))}
    </div>
  );
}
