import api from "./axios";

export const getPublicMemoryPages = async () => {
  const res = await api.get("/memory/public_memory_page_list");
  return res.data.memory_page_list;
};

export const getMemoryPage = async (id: string) => {
  const res = await api.get(`/memory/page/${id}`);
  return res.data;
};
export const createMemory = async (data: any) => {
  const res = await api.post("/memory/agent_create", data, {
    headers: { "Content-Type": "application/json" },
  });
  return res.data;
};
export const getMyMemoryPages = async () => {
  const res = await api.get("/memory/my_memory_pages");
  return res.data.memory_page_list;
};
