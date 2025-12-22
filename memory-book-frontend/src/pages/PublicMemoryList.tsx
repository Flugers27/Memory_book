import { useEffect, useState } from "react";
import { getPublicMemoryPages } from "../api/memory.api";
import MemoryCard from "../components/MemoryCard";

export default function PublicMemoryList() {
  const [pages, setPages] = useState<any[]>([]);

  useEffect(() => {
    getPublicMemoryPages().then(setPages);
  }, []);

  return (
    <div>
      <h2>Публичные страницы памяти</h2>
      {pages.map((page) => (
        <MemoryCard key={page.id_agent} memory={page} />
      ))}
    </div>
  );
}
