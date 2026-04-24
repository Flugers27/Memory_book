'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { memoryAPI } from '@/lib/api'
import { toast } from 'sonner'
import { Save, Eye, EyeOff, FileEdit } from 'lucide-react'

export default function CreatePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    title: '',
    epitaph: '',
    biography: '',
    is_public: true,
    is_draft: false,
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setForm({ ...form, [name]: checked })
    } else {
      setForm({ ...form, [name]: value })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await memoryAPI.createPage(form)
      toast.success('Страница памяти успешно создана!')
      router.push('/pages')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка создания страницы.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <FileEdit className="w-8 h-8" />
          Создание страницы памяти
        </h1>
        <p className="text-gray-600 mt-2">
          Заполните информацию об умершем члене семьи или питомце.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold mb-6">Основная информация</h2>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Название страницы *
              </label>
              <input
                type="text"
                name="title"
                required
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Например: Память о дедушке Иване"
                value={form.title}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Эпиграф (краткая надпись) *
              </label>
              <textarea
                name="epitaph"
                required
                rows={2}
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Короткая фраза, отражающая суть памяти..."
                value={form.epitaph}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Биография *
              </label>
              <textarea
                name="biography"
                required
                rows={6}
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Расскажите историю жизни, важные моменты, характер..."
                value={form.biography}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold mb-6">Настройки видимости</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {form.is_public ? (
                  <Eye className="w-5 h-5 text-green-600" />
                ) : (
                  <EyeOff className="w-5 h-5 text-gray-600" />
                )}
                <div>
                  <p className="font-medium">Публичная страница</p>
                  <p className="text-sm text-gray-500">
                    Страница будет видна всем пользователям
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="is_public"
                  className="sr-only peer"
                  checked={form.is_public}
                  onChange={handleChange}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileEdit className="w-5 h-5 text-yellow-600" />
                <div>
                  <p className="font-medium">Черновик</p>
                  <p className="text-sm text-gray-500">
                    Страница будет сохранена как черновик и не будет опубликована
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="is_draft"
                  className="sr-only peer"
                  checked={form.is_draft}
                  onChange={handleChange}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-8 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Создание...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Создать страницу памяти
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}