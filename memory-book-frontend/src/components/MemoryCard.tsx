import { Link } from "react-router-dom";

export default function MemoryCard({ memory }: { memory: any }) {
  return (
    <div style={{ border: "1px solid black", margin: "10px", padding: "10px" }}>
      <h3>{memory.full_name}</h3>
      <p>{memory.birth_date} — {memory.death_date}</p>
      <Link to={`/memory/${memory.page.id_page}`}>
        <button>Открыть страницу памяти</button>
      </Link>
    </div>
  );
}
