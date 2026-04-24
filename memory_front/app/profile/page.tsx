"use client";

import { User, Mail, Calendar, Edit, Save, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState({
    name: "Иван Иванов",
    email: "ivan@example.com",
    bio: "Люблю путешествовать и записывать воспоминания. Собираю моменты с 2020 года.",
    joinDate: "2023-05-15",
  });

  const handleSave = () => {
    setIsEditing(false);
    toast.success("Профиль обновлён");
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Можно сбросить изменения
  };

  return (
    <div className="max-w-4xl mx-auto my-12">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Левая колонка */}
        <div className="md:w-1/3">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-indigo-100 mb-6">
                <User className="w-16 h-16 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">{profile.name}</h2>
              <p className="text-gray-600 mt-2">Пользователь Memory Book</p>
              <div className="mt-6 flex items-center justify-center gap-2 text-gray-500">
                <Calendar className="w-4 h-4" />
                <span>Участник с {profile.joinDate}</span>
              </div>
            </div>

            <div className="mt-8 space-y-4">
              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-gray-400" />
                <span className="text-gray-700">{profile.email}</span>
              </div>
              <div className="pt-4 border-t">
                <h3 className="font-semibold text-gray-900 mb-2">Статистика</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Воспоминаний</span>
                    <span className="font-bold">42</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Тегов</span>
                    <span className="font-bold">18</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Дней активности</span>
                    <span className="font-bold">127</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Правая колонка */}
        <div className="md:w-2/3 space-y-8">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">Обо мне</h3>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                {isEditing ? <X className="w-4 h-4" /> : <Edit className="w-4 h-4" />}
                {isEditing ? "Отмена" : "Редактировать"}
              </button>
            </div>

            {isEditing ? (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Имя</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Биография</label>
                  <textarea
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                    value={profile.bio}
                    onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                  />
                </div>
                <div className="flex gap-4">
                  <button
                    onClick={handleSave}
                    className="flex items-center gap-2 px-6 py-3 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
                  >
                    <Save className="w-4 h-4" />
                    Сохранить
                  </button>
                  <button
                    onClick={handleCancel}
                    className="px-6 py-3 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <p className="text-gray-700 whitespace-pre-line">{profile.bio}</p>
              </div>
            )}
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Настройки</h3>
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-medium text-gray-900">Уведомления по email</h4>
                  <p className="text-gray-600 text-sm">Получать уведомления о новых функциях</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-medium text-gray-900">Двухфакторная аутентификация</h4>
                  <p className="text-gray-600 text-sm">Повысьте безопасность аккаунта</p>
                </div>
                <button className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50">
                  Включить
                </button>
              </div>
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-medium text-gray-900">Экспорт данных</h4>
                  <p className="text-gray-600 text-sm">Скачайте все ваши воспоминания</p>
                </div>
                <button className="px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700">
                  Экспортировать
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}