"use client";

import { useState } from "react";
import { Save, ArrowLeft, Upload, Calendar, MapPin, User } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export default function CreatePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    agentName: "",
    birthDate: "",
    deathDate: "",
    epitaph: "",
    placeOfBirth: "",
    placeOfDeath: "",
    biography: "",
    isPublic: true,
    isDraft: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      setForm({ ...form, [name]: checked });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Заглушка
    setTimeout(() => {
      toast.success("Страница памяти создана");
      router.push("/pages");
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="max-w-4xl mx-auto my-12">
      <div className="mb-8">
        <Link
          href="/pages"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4" />
          Назад к списку страниц
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-4">Создание страницы памяти</h1>
        <p className="text-gray-600">Заполните информацию об ушедшем близком человеке или питомце.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Основная информация об агенте */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <User className="w-5 h-5" />
            Основные данные
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Полное имя *
              </label>
              <input
                type="text"
                name="agentName"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Иванов Иван Иванович"
                value={form.agentName}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Эпитафия (необязательно)
              </label>
              <input
                type="text"
                name="epitaph"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                placeholder="Короткая памятная фраза"
                value={form.epitaph}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Дата рождения
              </label>
              <input
                type="date"
                name="birthDate"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                value={form.birthDate}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Дата смерти
              </label>
              <input
                type="date"
                name="deathDate"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                value={form.deathDate}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Место рождения
              </label>
              <input
                type="text"
                name="placeOfBirth"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                placeholder="Город, страна"
                value={form.placeOfBirth}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Место смерти
              </label>
              <input
                type="text"
                name="placeOfDeath"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                placeholder="Город, страна"
                value={form.placeOfDeath}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Биография */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Биография</h2>
          <textarea
            name="biography"
            rows={6}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            placeholder="Расскажите историю жизни, важные моменты, характер..."
            value={form.biography}
            onChange={handleChange}
          />
          <p className="text-sm text-gray-500 mt-2">Поддерживается Markdown. Вы можете добавить ссылки, списки, выделения.</p>
        </div>

        {/* Настройки доступа */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Настройки доступа</h2>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">Публичная страница</h3>
                <p className="text-gray-600 text-sm">Страница будет видна всем пользователям без авторизации</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="isPublic"
                  checked={form.isPublic}
                  onChange={handleChange}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">Сохранить как черновик</h3>
                <p className="text-gray-600 text-sm">Страница не будет опубликована, даже если публичная</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="isDraft"
                  checked={form.isDraft}
                  onChange={handleChange}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Загрузка фото (заглушка) */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Фотографии
          </h2>
          <div className="border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">Перетащите сюда фотографии или нажмите для загрузки</p>
            <p className="text-sm text-gray-500">Поддерживаются JPG, PNG до 10 МБ</p>
            <button
              type="button"
              className="mt-4 px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Выбрать файлы
            </button>
          </div>
        </div>

        {/* Кнопки */}
        <div className="flex justify-between items-center">
          <Link
            href="/pages"
            className="px-8 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            Отмена
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-8 py-3 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            <Save className="w-5 h-5" />
            {loading ? "Создание..." : "Создать страницу памяти"}
          </button>
        </div>
      </form>
    </div>
  );
}