import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMemoryPage } from "../api/memory.api";

export default function MemoryPage() {
  const { id } = useParams();
  const [page, setPage] = useState<any>(null);

  useEffect(() => {
    if (id) getMemoryPage(id).then(setPage);
  }, [id]);

  if (!page) return <p>Загрузка...</p>;

  return (
    <div>
      <h2>{page.full_name}</h2>
      <p>{page.page.epitaph}</p>
      {/* Здесь позже можно добавить медиа */}
    </div>
  );
}
