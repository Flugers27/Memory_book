"use client";

import { useState } from "react";
import { Plus, Search, Filter, Calendar, Tag, Edit, Trash2 } from "lucide-react";
import { toast } from "sonner";

type Memory = {
  id: string;
  title: string;
  content: string;
  date: string;
  tags: string[];
  mood: string;
};

export default function MemoriesPage() {
  const [memories, setMemories] = useState<Memory[]>([
    {
      id: "1",
      title: "Поездка на море",
      content: "Замечательный день на пляже с семьей. Солнце, море и смех.",
      date: "2024-08-15",
      tags: ["отпуск", "семья", "море"],
      mood: "happy",
    },
    {
      id: "2",
      title: "Успешный проект",
      content: "Завершили важный проект вовремя. Команда была великолепна.",
      date: "2024-09-20",
      tags: ["работа", "успех"],
      mood: "proud",
    },
    {
      id: "3",
      title: "Встреча с друзьями",
      content: "Долгожданная встреча после многих лет. Столько воспоминаний!",
      date: "2024-10-05",
      tags: ["друзья", "встреча"],
      mood: "joyful",
    },
  ]);

  const [search, setSearch] = useState("");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const allTags = Array.from(new Set(memories.flatMap((m) => m.tags)));

  const filteredMemories = memories.filter((memory) => {
    const matchesSearch =
      memory.title.toLowerCase().includes(search.toLowerCase()) ||
      memory.content.toLowerCase().includes(search.toLowerCase());
    const matchesTag = selectedTag ? memory.tags.includes(selectedTag) : true;
    return matchesSearch && matchesTag;
  });

  const handleDelete = (id: string) => {
    setMemories(memories.filter((m) => m.id !== id));
    toast.success("Воспоминание удалено");
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Мои воспоминания</h1>
          <p className="text-gray-600">Здесь хранятся все ваши записи и моменты</p>
        </div>
        <button
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white hover:bg-indigo-700 transition-colors"
          onClick={() => toast.info("Функция добавления в разработке")}
        >
          <Plus className="w-5 h-5" />
          Добавить воспоминание
        </button>
      </div>

      {/* Фильтры и поиск */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Поиск по воспоминаниям..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            className={`px-4 py-2 rounded-lg border flex items-center gap-2 ${selectedTag === null ? "bg-indigo-50 border-indigo-300 text-indigo-700" : "border-gray-300 text-gray-700"}`}
            onClick={() => setSelectedTag(null)}
          >
            <Filter className="w-4 h-4" />
            Все
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              className={`px-4 py-2 rounded-lg border ${selectedTag === tag ? "bg-indigo-50 border-indigo-300 text-indigo-700" : "border-gray-300 text-gray-700"}`}
              onClick={() => setSelectedTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Список воспоминаний */}
      {filteredMemories.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-2xl">
          <div className="text-gray-400 mb-4">Нет воспоминаний, соответствующих фильтрам</div>
          <button
            className="text-indigo-600 font-medium hover:underline"
            onClick={() => {
              setSearch("");
              setSelectedTag(null);
            }}
          >
            Сбросить фильтры
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMemories.map((memory) => (
            <div
              key={memory.id}
              className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-900">{memory.title}</h3>
                <div className="flex gap-2">
                  <button
                    className="p-2 text-gray-500 hover:text-indigo-600"
                    onClick={() => toast.info("Редактирование в разработке")}
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    className="p-2 text-gray-500 hover:text-red-600"
                    onClick={() => handleDelete(memory.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-gray-700 mb-4">{memory.content}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {memory.date}
                </div>
                <div className="flex items-center gap-1">
                  <Tag className="w-4 h-4" />
                  {memory.tags.join(", ")}
                </div>
              </div>
              <div className="mt-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${memory.mood === "happy" ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"}`}>
                  {memory.mood === "happy" ? "Радость" : "Гордость"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Статистика */}
      <div className="bg-gray-50 rounded-2xl p-6">
        <h3 className="text-lg font-semibold mb-4">Статистика</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-white rounded-lg">
            <div className="text-2xl font-bold text-indigo-600">{memories.length}</div>
            <div className="text-gray-600">Всего записей</div>
          </div>
          <div className="text-center p-4 bg-white rounded-lg">
            <div className="text-2xl font-bold text-green-600">{allTags.length}</div>
            <div className="text-gray-600">Уникальных тегов</div>
          </div>
          <div className="text-center p-4 bg-white rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {new Set(memories.map((m) => m.date.split("-")[0])).size}
            </div>
            <div className="text-gray-600">Активных лет</div>
          </div>
          <div className="text-center p-4 bg-white rounded-lg">
            <div className="text-2xl font-bold text-amber-600">24</div>
            <div className="text-gray-600">Записей в этом месяце</div>
          </div>
        </div>
      </div>
    </div>
  );
}