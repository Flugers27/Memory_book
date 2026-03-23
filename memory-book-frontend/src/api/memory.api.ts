import api from "./axios";

export const getPublicMemoryPages = async () => {
  const res = await api.get("/memory/public_memory_page_list");
  return res.data.memory_page_list;
};

export const getMemoryPage = async (agentId: string) => {
  const res = await api.get(`/memory/public_memory_page/${agentId}`);
  return res.data;
};

export const getPrivateMemoryPage = async (agentId: string) => {
  const res = await api.get(`/memory/memory_page/${agentId}`);
  return res.data;
};
export const createMemory = async (data: any) => {
  const res = await api.post("/memory/agent_create", data, {
    headers: { "Content-Type": "application/json" },
  });
  return res.data;
};
export const getMyMemoryPages = async () => {
  const res = await api.get("/memory/memory_page_list");
  return res.data.memory_page_list;
};
