"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Filter, Calendar, User, Lock, Globe, Heart } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { memoryAPI } from "@/lib/api";

type MemoryPage = {
  id_page: string;
  epitaph?: string;
  place_of_birth?: string;
  place_of_death?: string;
  biography?: any;
  is_public: boolean;
  is_draft: boolean;
  memory_agent_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  agent?: {
    full_name: string;
    birth_date?: string;
    death_date?: string;
    avatar_url?: string;
  };
};

export default function PagesPage() {
  const [pages, setPages] = useState<MemoryPage[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "public" | "private" | "draft">("all");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Проверяем авторизацию (заглушка)
    const token = localStorage.getItem("access_token");
    setIsAuthenticated(!!token);
    fetchPages();
  }, []);

  const fetchPages = async () => {
    setLoading(true);
    try {
      // Заглушка: имитация данных
      setTimeout(() => {
        setPages([
          {
            id_page: "1",
            epitaph: "Вечная память",
            place_of_birth: "Москва",
            place_of_death: "Санкт-Петербург",
            biography: { text: "Любил жизнь и семью." },
            is_public: true,
            is_draft: false,
            memory_agent_id: "a1",
            user_id: "u1",
            created_at: "2024-01-15",
            updated_at: "2024-01-15",
            agent: {
              full_name: "Иванов Иван Иванович",
              birth_date: "1950-05-20",
              death_date: "2023-12-10",
              avatar_url: "",
            },
          },
          {
            id_page: "2",
            epitaph: "Наш любимый пёс",
            place_of_birth: "Дом",
            place_of_death: "Ветеринарная клиника",
            biography: { text: "Верный друг на протяжении 12 лет." },
            is_public: false,
            is_draft: false,
            memory_agent_id: "a2",
            user_id: "u1",
            created_at: "2024-02-20",
            updated_at: "2024-02-20",
            agent: {
              full_name: "Бобик",
              birth_date: "2012-03-10",
              death_date: "2024-01-05",
              avatar_url: "",
            },
          },
          {
            id_page: "3",
            epitaph: "Бабушка",
            place_of_birth: "Село Родное",
            place_of_death: "Городская больница",
            biography: { text: "Мудрая и добрая женщина." },
            is_public: true,
            is_draft: false,
            memory_agent_id: "a3",
            user_id: "u2",
            created_at: "2024-03-01",
            updated_at: "2024-03-01",
            agent: {
              full_name: "Мария Петровна",
              birth_date: "1940-11-30",
              death_date: "2024-02-28",
              avatar_url: "",
            },
          },
        ]);
        setLoading(false);
      }, 500);
    } catch (error) {
      toast.error("Ошибка загрузки страниц");
      setLoading(false);
    }
  };

  const filteredPages = pages.filter((page) => {
    const matchesSearch = page.agent?.full_name.toLowerCase().includes(search.toLowerCase()) ||
      page.epitaph?.toLowerCase().includes(search.toLowerCase());
    if (filter === "public") return page.is_public && !page.is_draft;
    if (filter === "private") return !page.is_public && !page.is_draft;
    if (filter === "draft") return page.is_draft;
    return matchesSearch;
  });

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Страницы памяти</h1>
          <p className="text-gray-600">
            {isAuthenticated
              ? "Ваши страницы памяти и публичные страницы других пользователей"
              : "Публичные страницы памяти. Войдите, чтобы создать свою."}
          </p>
        </div>
        {isAuthenticated ? (
          <Link
            href="/pages/create"
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white hover:bg-indigo-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Создать страницу
          </Link>
        ) : (
          <Link
            href="/login"
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Войти для создания
          </Link>
        )}
      </div>

      {/* Фильтры и поиск */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Поиск по имени или эпитафии..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            className={`px-4 py-2 rounded-lg border flex items-center gap-2 ${filter === "all" ? "bg-indigo-50 border-indigo-300 text-indigo-700" : "border-gray-300 text-gray-700"}`}
            onClick={() => setFilter("all")}
          >
            <Filter className="w-4 h-4" />
            Все
          </button>
          <button
            className={`px-4 py-2 rounded-lg border flex items-center gap-2 ${filter === "public" ? "bg-green-50 border-green-300 text-green-700" : "border-gray-300 text-gray-700"}`}
            onClick={() => setFilter("public")}
          >
            <Globe className="w-4 h-4" />
            Публичные
          </button>
          {isAuthenticated && (
            <>
              <button
                className={`px-4 py-2 rounded-lg border flex items-center gap-2 ${filter === "private" ? "bg-blue-50 border-blue-300 text-blue-700" : "border-gray-300 text-gray-700"}`}
                onClick={() => setFilter("private")}
              >
                <Lock className="w-4 h-4" />
                Приватные
              </button>
              <button
                className={`px-4 py-2 rounded-lg border flex items-center gap-2 ${filter === "draft" ? "bg-amber-50 border-amber-300 text-amber-700" : "border-gray-300 text-gray-700"}`}
                onClick={() => setFilter("draft")}
              >
                <Calendar className="w-4 h-4" />
                Черновики
              </button>
            </>
          )}
        </div>
      </div>

      {/* Список страниц */}
      {loading ? (
        <div className="text-center py-12">Загрузка...</div>
      ) : filteredPages.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-2xl">
          <Heart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <div className="text-gray-500">Страницы памяти не найдены</div>
          {isAuthenticated && (
            <Link href="/pages/create" className="mt-4 inline-block text-indigo-600 font-medium hover:underline">
              Создайте первую страницу
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPages.map((page) => (
            <Link
              key={page.id_page}
              href={`/pages/${page.id_page}`}
              className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow block"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{page.agent?.full_name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    {page.is_public ? (
                      <span className="flex items-center gap-1 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                        <Globe className="w-3 h-3" /> Публичная
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        <Lock className="w-3 h-3" /> Приватная
                      </span>
                    )}
                    {page.is_draft && (
                      <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded-full">
                        Черновик
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">
                    {new Date(page.created_at).toLocaleDateString("ru-RU")}
                  </div>
                </div>
              </div>
              <p className="text-gray-700 mb-4 line-clamp-2">{page.epitaph || "Эпитафия не указана"}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {page.agent?.birth_date && page.agent?.death_date
                    ? `${page.agent.birth_date} – ${page.agent.death_date}`
                    : "Даты неизвестны"}
                </div>
                <div className="flex items-center gap-1">
                  <User className="w-4 h-4" />
                  {page.agent?.full_name.split(" ")[0]}
                </div>
              </div>
              <div className="mt-4 pt-4 border-t text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Место рождения:</span>
                  <span className="font-medium">{page.place_of_birth || "—"}</span>
                </div>
                <div className="flex justify-between mt-1">
                  <span>Место смерти:</span>
                  <span className="font-medium">{page.place_of_death || "—"}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Информация о доступе */}
      {!isAuthenticated && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Хотите создать свою страницу памяти?</h3>
          <p className="text-blue-800 mb-4">
            Зарегистрируйтесь, чтобы сохранить память о близких, управлять доступом и приглашать родственников.
          </p>
          <div className="flex gap-4">
            <Link
              href="/register"
              className="px-6 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
            >
              Зарегистрироваться
            </Link>
            <Link
              href="/login"
              className="px-6 py-2 rounded-lg border border-blue-600 text-blue-600 hover:bg-blue-50"
            >
              Войти
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}