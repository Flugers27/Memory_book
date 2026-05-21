'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { memoryAPI } from '@/lib/api'
import { toast } from 'sonner'
import { Save, Eye, EyeOff, FileEdit, User, Calendar, MapPin, Image } from 'lucide-react'

export default function CreatePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [agentForm, setAgentForm] = useState({
    full_name: '',
    gender: '',
    birth_date: '',
    death_date: '',
    place_of_birth: '',
    place_of_death: '',
    avatar_url: '',
    is_human: true,
  })
  const [pageForm, setPageForm] = useState({
    epitaph: '',
    biography: '',
    is_public: true,
    is_draft: false,
  })

  const handleAgentChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setAgentForm({ ...agentForm, [name]: checked })
    } else if (type === 'radio') {
      // Для radio button обрабатываем is_human
      if (name === 'is_human') {
        setAgentForm({ ...agentForm, is_human: value === 'true' })
      }
    } else {
      setAgentForm({ ...agentForm, [name]: value })
    }
  }

  const handlePageChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setPageForm({ ...pageForm, [name]: checked })
    } else {
      setPageForm({ ...pageForm, [name]: value })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Клиентская валидация
    if (!agentForm.full_name.trim()) {
      toast.error('Пожалуйста, введите полное имя агента')
      return
    }
    
    if (!pageForm.epitaph.trim()) {
      toast.error('Пожалуйста, введите эпитафию')
      return
    }
    
    if (!pageForm.biography.trim()) {
      toast.error('Пожалуйста, введите биографию')
      return
    }
    
    setLoading(true)
    try {
      // Маппинг пола в один символ для базы данных
      const genderMap: Record<string, string | null> = {
        'male': 'M',
        'female': 'F',
        'other': 'O',
        '': null
      }
      
      // Обработка дат: пустые строки должны быть null
      const parseDate = (dateStr: string): string | null => {
        if (!dateStr || dateStr.trim() === '') return null
        // Проверяем, что дата в правильном формате YYYY-MM-DD
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/
        if (!dateRegex.test(dateStr)) {
          console.warn(`Date format might be incorrect: ${dateStr}`)
        }
        return dateStr
      }
      
      // Подготовка данных агента
      const agentData = {
        full_name: agentForm.full_name.trim(),
        gender: genderMap[agentForm.gender] || null,
        birth_date: parseDate(agentForm.birth_date),
        death_date: parseDate(agentForm.death_date),
        place_of_birth: agentForm.place_of_birth?.trim() || null,
        place_of_death: agentForm.place_of_death?.trim() || null,
        avatar_url: agentForm.avatar_url?.trim() || null,
        is_human: agentForm.is_human,
      }

      console.log('Sending agent data:', JSON.stringify(agentData, null, 2))

      // 1. Создаем агента
      const agentResponse = await memoryAPI.createAgent(agentData)
      console.log('Agent created:', agentResponse)
      const agentId = agentResponse.id_agent
      
      // 2. Создаем страницу с agent_id
      const pageData = {
        epitaph: pageForm.epitaph.trim(),
        // biography должен быть массивом BiographyItem
        biography: pageForm.biography.trim() ? [
          {
            title: 'Биография',
            info: pageForm.biography.trim(),
            titles: []
          }
        ] : [],
        is_public: pageForm.is_public,
        is_draft: pageForm.is_draft,
        agent_id: agentId,
      }

      console.log('Sending page data:', JSON.stringify(pageData, null, 2))
      
      const pageResponse = await memoryAPI.createPage(pageData)
      console.log('Page created:', pageResponse)
      
      toast.success('Страница памяти успешно создана!')
      // Даем пользователю время увидеть сообщение об успехе
      setTimeout(() => {
        router.push('/memory_page/list/my')
      }, 1500)
    } catch (error: any) {
      console.error('Error creating memory page:', error)
      console.error('Error response:', error.response?.data)
      console.error('Error status:', error.response?.status)
      console.error('Error headers:', error.response?.headers)
      
      // Улучшенная обработка ошибок валидации
      if (error.response?.status === 422) {
        const errors = error.response.data?.detail
        console.error('Validation errors:', errors)
        if (Array.isArray(errors)) {
          const errorMessages = errors.map((err: any) => {
            const field = err.loc?.join('.') || 'unknown'
            return `${field}: ${err.msg}`
          }).join('\n')
          toast.error(`Ошибка валидации:\n${errorMessages}`)
        } else if (typeof errors === 'string') {
          toast.error(`Ошибка валидации: ${errors}`)
        } else if (errors && typeof errors === 'object') {
          // Если errors - объект с полями
          const errorMessages = Object.entries(errors).map(([key, value]) =>
            `${key}: ${value}`
          ).join('\n')
          toast.error(`Ошибка валидации:\n${errorMessages}`)
        } else {
          toast.error('Ошибка валидации данных. Проверьте заполнение полей.')
        }
      } else if (error.response?.status === 500) {
        toast.error('Внутренняя ошибка сервера. Попробуйте позже.')
      } else if (error.response?.status === 401) {
        toast.error('Сессия истекла. Пожалуйста, войдите снова.')
        router.push('/user/login')
      } else {
        toast.error(error.response?.data?.detail || error.message || 'Ошибка создания страницы.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
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
        {/* Блок информации об агенте */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center gap-2 mb-6">
            <User className="w-6 h-6 text-indigo-600" />
            <h2 className="text-xl font-semibold">Информация об умершем</h2>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Полное имя *
              </label>
              <input
                type="text"
                name="full_name"
                required
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Иванов Иван Иванович"
                value={agentForm.full_name}
                onChange={handleAgentChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Тип агента *
              </label>
              <div className="flex gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="is_human"
                    value="true"
                    checked={agentForm.is_human === true}
                    onChange={() => setAgentForm({...agentForm, is_human: true})}
                    className="w-4 h-4 text-indigo-600"
                  />
                  <span className="text-gray-700">Человек</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="is_human"
                    value="false"
                    checked={agentForm.is_human === false}
                    onChange={() => setAgentForm({...agentForm, is_human: false})}
                    className="w-4 h-4 text-indigo-600"
                  />
                  <span className="text-gray-700">Питомец</span>
                </label>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Пол
                </label>
                <select
                  name="gender"
                  className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  value={agentForm.gender}
                  onChange={handleAgentChange}
                >
                  <option value="">Не указано</option>
                  <option value="male">Мужской</option>
                  <option value="female">Женский</option>
                  <option value="other">Другой</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL аватара
                </label>
                <div className="flex items-center gap-2">
                  <Image className="w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="avatar_url"
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="https://example.com/avatar.jpg"
                    value={agentForm.avatar_url}
                    onChange={handleAgentChange}
                  />
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Дата рождения
                </label>
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-gray-400" />
                  <input
                    type="date"
                    name="birth_date"
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={agentForm.birth_date}
                    onChange={handleAgentChange}
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Дата смерти
                </label>
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-gray-400" />
                  <input
                    type="date"
                    name="death_date"
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={agentForm.death_date}
                    onChange={handleAgentChange}
                  />
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Место рождения
                </label>
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="place_of_birth"
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Город, страна"
                    value={agentForm.place_of_birth}
                    onChange={handleAgentChange}
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Место смерти
                </label>
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="place_of_death"
                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Город, страна"
                    value={agentForm.place_of_death}
                    onChange={handleAgentChange}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Блок информации о странице памяти */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center gap-2 mb-6">
            <FileEdit className="w-6 h-6 text-indigo-600" />
            <h2 className="text-xl font-semibold">Страница памяти</h2>
          </div>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Эпитафия (краткая надпись) *
              </label>
              <textarea
                name="epitaph"
                required
                rows={2}
                className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Короткая фраза, отражающая суть памяти..."
                value={pageForm.epitaph}
                onChange={handlePageChange}
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
                value={pageForm.biography}
                onChange={handlePageChange}
              />
            </div>
          </div>
        </div>

        {/* Блок настроек видимости */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-xl font-semibold mb-6">Настройки видимости</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {pageForm.is_public ? (
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
                  checked={pageForm.is_public}
                  onChange={handlePageChange}
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
                  checked={pageForm.is_draft}
                  onChange={handlePageChange}
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