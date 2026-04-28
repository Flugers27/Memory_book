'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { memoryAPI } from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { ArrowLeft, Eye, EyeOff, Calendar, User, MapPin, Edit } from 'lucide-react'
import Link from 'next/link'

type PageDetail = {
  id: string
  title: string
  epitaph: string
  biography: string
  is_public: boolean
  is_draft: boolean
  created_at: string
  updated_at: string
  agent_id: string
  full_name: string
  gender: string
  birth_date: string | null
  death_date: string | null
  place_of_birth: string | null
  place_of_death: string | null
  is_human: boolean
  avatar_url: string | null
}

export default function PageDetail() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuthStore()
  const [page, setPage] = useState<PageDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const pageId = params.id as string
  const [agent, setAgent] = useState<any>(null)
  const [pages, setPages] = useState<any[]>([])
  const [selectedPage, setSelectedPage] = useState<any>(null)
  const [editing, setEditing] = useState(false)
  const [editAgent, setEditAgent] = useState<any>(null)
  const [editPage, setEditPage] = useState<any>(null)
  const [updating, setUpdating] = useState(false)

  const handleEditClick = () => {
    const newEditing = !editing
    setEditing(newEditing)
    if (newEditing) {
      // Инициализируем формы редактирования текущими данными
      setEditAgent(agent ? { ...agent } : null)
      setEditPage(selectedPage ? { ...selectedPage } : null)
    } else {
      // Отмена редактирования
      setEditAgent(null)
      setEditPage(null)
    }
  }

  const handleUpdateAgent = async () => {
    if (!editAgent || !agent?.id_agent) return
    try {
      setUpdating(true)
      const updated = await memoryAPI.updateAgent(agent.id_agent, editAgent)
      setAgent(updated)
      setEditAgent(updated)
      alert('Агент успешно обновлён')
    } catch (err) {
      console.error('Ошибка обновления агента:', err)
      alert('Не удалось обновить агента')
    } finally {
      setUpdating(false)
    }
  }

  const handleUpdatePage = async () => {
    if (!editPage || !selectedPage?.id_page) return
    try {
      setUpdating(true)
      const updated = await memoryAPI.updatePage(selectedPage.id_page, editPage)
      // Обновляем selectedPage и pages
      setSelectedPage(updated)
      setPages(prev => prev.map(p => p.id_page === updated.id_page ? updated : p))
      alert('Страница успешно обновлена')
    } catch (err) {
      console.error('Ошибка обновления страницы:', err)
      alert('Не удалось обновить страницу')
    } finally {
      setUpdating(false)
    }
  }

  const handleUpdateBoth = async () => {
    if (!editAgent || !agent?.id_agent) return
    try {
      setUpdating(true)
      // Сначала обновляем агента
      await memoryAPI.updateAgent(agent.id_agent, editAgent)
      // Затем страницу, если есть
      if (editPage && selectedPage?.id_page) {
        await memoryAPI.updatePage(selectedPage.id_page, editPage)
      }
      // Перезагружаем данные
      const agentData = await memoryAPI.getAgent(pageId)
      const pagesData = await memoryAPI.getPageList(pageId)
      setAgent(agentData)
      setPages(pagesData.pages || [])
      const priorityPage = selectPriorityPage(pagesData.pages || [])
      setSelectedPage(priorityPage || null)
      alert('Страница памяти полностью обновлена')
    } catch (err) {
      console.error('Ошибка обновления страницы памяти:', err)
      alert('Не удалось обновить страницу памяти')
    } finally {
      setUpdating(false)
    }
  }

  useEffect(() => {
    if (!pageId) return

    const fetchData = async () => {
      try {
        setLoading(true)
        // ПЕРВЫЙ ПРИОРИТЕТ: попытка получить публичную страницу
        try {
          const data = await memoryAPI.getPublicPage(pageId)
          // Преобразуем данные публичной страницы
          const item = data.memory_page || data
          const pageData = item.page || item
          let biography = pageData.biography || item.biography || ''
          if (Array.isArray(biography)) {
            const first = biography[0]
            if (first?.info) biography = first.info
            else if (first?.title) biography = first.title
            else biography = JSON.stringify(biography)
          }
          const detail: PageDetail = {
            id: pageData.id_page || item.id_agent || pageId,
            title: item.full_name || 'Без названия',
            epitaph: pageData.epitaph || item.epitaph || '',
            biography,
            is_public: pageData.is_public ?? item.is_public ?? true,
            is_draft: pageData.is_draft ?? item.is_draft ?? false,
            created_at: pageData.created_at || item.created_at || '',
            updated_at: pageData.updated_at || item.updated_at || '',
            agent_id: item.id_agent || item.agent_id,
            full_name: item.full_name || '',
            gender: item.gender || '',
            birth_date: item.birth_date,
            death_date: item.death_date,
            place_of_birth: item.place_of_birth,
            place_of_death: item.place_of_death,
            is_human: item.is_human ?? true,
            avatar_url: item.avatar_url,
          }
          setPage(detail)
          setAgent(item)
          setPages([pageData])
          setSelectedPage(pageData)
          setError(null)
          return // Успешно, выходим
        } catch (publicErr: any) {
          // Если публичная страница не найдена (404) или другая ошибка, продолжаем
          console.log('Public page not found, trying authenticated endpoints if user exists')
        }

        // Если пользователь авторизован, пробуем получить через защищенные эндпоинты
        if (user) {
          try {
            const agentData = await memoryAPI.getAgent(pageId)
            setAgent(agentData)
            let pagesList = []
            try {
              const pagesData = await memoryAPI.getPageList(pageId)
              pagesList = pagesData.pages || []
            } catch (err: any) {
              if (err.response?.status !== 404) {
                console.error('Error fetching pages:', err)
              }
            }
            setPages(pagesList)
            const priorityPage = selectPriorityPage(pagesList)
            setSelectedPage(priorityPage || null)
            setError(null)
          } catch (err: any) {
            console.error('Error fetching agent or pages:', err)
            // Если и это не удалось, пробуем получить через getUserPage (старый метод)
            try {
              const data = await memoryAPI.getUserPage(pageId)
              const item = data.memory_page || data
              const pageData = item.page || item
              let biography = normalizeBiography(pageData.biography || item.biography || '')
              const detail: PageDetail = {
                id: pageData.id_page || item.id_agent || pageId,
                title: item.full_name || 'Без названия',
                epitaph: pageData.epitaph || item.epitaph || '',
                biography,
                is_public: pageData.is_public ?? item.is_public ?? true,
                is_draft: pageData.is_draft ?? item.is_draft ?? false,
                created_at: pageData.created_at || item.created_at || '',
                updated_at: pageData.updated_at || item.updated_at || '',
                agent_id: item.id_agent || item.agent_id,
                full_name: item.full_name || '',
                gender: item.gender || '',
                birth_date: item.birth_date,
                death_date: item.death_date,
                place_of_birth: item.place_of_birth,
                place_of_death: item.place_of_death,
                is_human: item.is_human ?? true,
                avatar_url: item.avatar_url,
              }
              setPage(detail)
              setAgent(item)
              setPages([pageData])
              setSelectedPage(pageData)
              setError(null)
            } catch (fallbackErr) {
              console.error('Fallback also failed:', fallbackErr)
              setError('Не удалось загрузить страницу памяти. Возможно, она не существует или у вас нет доступа.')
            }
          }
        } else {
          // Пользователь не авторизован и публичная страница не найдена
          setError('Страница памяти не найдена или недоступна. Возможно, требуется авторизация.')
        }
      } catch (err: any) {
        console.error('Unexpected error:', err)
        setError('Произошла непредвиденная ошибка при загрузке страницы.')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [pageId, user])

  const selectPriorityPage = (pages: any[]) => {
    if (pages.length === 0) return null
    // Приоритет 1: публичная и не черновик
    const publicNonDraft = pages.find(p => p.is_public === true && p.is_draft === false)
    if (publicNonDraft) return publicNonDraft
    // Приоритет 2: не публичная, но не черновик
    const nonPublicNonDraft = pages.find(p => p.is_public === false && p.is_draft === false)
    if (nonPublicNonDraft) return nonPublicNonDraft
    // Приоритет 3: черновик
    const draft = pages.find(p => p.is_draft === true)
    if (draft) return draft
    // Если ничего не найдено, возвращаем первую страницу
    return pages[0]
  }

  // Функция для нормализации biography в строку
  const normalizeBiography = (bio: any): string => {
    if (!bio) return ''
    if (typeof bio === 'string') return bio
    if (Array.isArray(bio)) {
      // Обрабатываем массив объектов с полями title, info, titles
      const parts: string[] = []
      bio.forEach((item, index) => {
        if (item && typeof item === 'object') {
          // Добавляем основной info
          if (item.info) parts.push(item.info)
          // Обрабатываем подзаголовки titles
          if (Array.isArray(item.titles)) {
            item.titles.forEach((sub: any) => {
              if (sub?.info) parts.push(sub.info)
            })
          }
        }
      })
      if (parts.length > 0) {
        return parts.join('\n\n')
      }
      // Если ничего не извлекли, возвращаем JSON
      return JSON.stringify(bio)
    }
    if (typeof bio === 'object') {
      // Пытаемся извлечь info, title, или text
      if (bio.info) return bio.info
      if (bio.title) return bio.title
      if (bio.text) return bio.text
      // Если есть поле titles (массив), обрабатываем
      if (Array.isArray(bio.titles)) {
        const parts: string[] = []
        bio.titles.forEach((sub: any) => {
          if (sub?.info) parts.push(sub.info)
        })
        if (parts.length > 0) return parts.join('\n\n')
      }
      return JSON.stringify(bio)
    }
    return String(bio)
  }

  // Функция для рендеринга структурированной биографии
  const renderBiography = (bio: any): React.ReactNode => {
    if (!bio) return null
    if (typeof bio === 'string') return <p className="text-gray-700 whitespace-pre-line">{bio}</p>
    if (Array.isArray(bio)) {
      return (
        <div className="space-y-6">
          {bio.map((item, idx) => (
            <div key={idx} className="space-y-4">
              {item.title && <h3 className="text-xl font-semibold text-gray-900">{item.title}</h3>}
              {item.info && <p className="text-gray-700">{item.info}</p>}
              {Array.isArray(item.titles) && item.titles.length > 0 && (
                <div className="ml-6 space-y-3">
                  {item.titles.map((sub: any, subIdx: number) => (
                    <div key={subIdx}>
                      {sub.title && <h4 className="text-lg font-medium text-gray-800">{sub.title}</h4>}
                      {sub.info && <p className="text-gray-700">{sub.info}</p>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )
    }
    if (typeof bio === 'object') {
      // Одиночный объект
      return (
        <div className="space-y-4">
          {bio.title && <h3 className="text-xl font-semibold text-gray-900">{bio.title}</h3>}
          {bio.info && <p className="text-gray-700">{bio.info}</p>}
          {Array.isArray(bio.titles) && bio.titles.length > 0 && (
            <div className="ml-6 space-y-3">
              {bio.titles.map((sub: any, subIdx: number) => (
                <div key={subIdx}>
                  {sub.title && <h4 className="text-lg font-medium text-gray-800">{sub.title}</h4>}
                  {sub.info && <p className="text-gray-700">{sub.info}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )
    }
    return <p className="text-gray-700">{String(bio)}</p>
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p className="mt-2 text-gray-500">Загрузка страницы памяти...</p>
      </div>
    )
  }

  // Определяем данные для отображения
  let displayPage = page
  if (selectedPage || agent) {
    displayPage = {
      id: selectedPage?.id_page || agent?.id_agent || pageId,
      title: agent?.full_name || 'Без названия',
      epitaph: selectedPage?.epitaph || '',
      biography: selectedPage?.biography || '',
      is_public: selectedPage?.is_public ?? false,
      is_draft: selectedPage?.is_draft ?? false,
      created_at: selectedPage?.created_at || agent?.created_at || new Date().toISOString(),
      updated_at: selectedPage?.updated_at || agent?.updated_at || new Date().toISOString(),
      agent_id: agent?.id_agent || pageId,
      full_name: agent?.full_name || '',
      gender: agent?.gender || '',
      birth_date: agent?.birth_date,
      death_date: agent?.death_date,
      place_of_birth: agent?.place_of_birth,
      place_of_death: agent?.place_of_death,
      is_human: agent?.is_human ?? true,
      avatar_url: agent?.avatar_url,
    }
  }
  // Если displayPage всё ещё null (маловероятно), создаём пустой объект
  if (!displayPage) {
    displayPage = {
      id: pageId,
      title: 'Без названия',
      epitaph: '',
      biography: '',
      is_public: false,
      is_draft: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      agent_id: pageId,
      full_name: '',
      gender: '',
      birth_date: null,
      death_date: null,
      place_of_birth: null,
      place_of_death: null,
      is_human: true,
      avatar_url: null,
    }
  }

  if (error || (!agent && !page)) {
    return (
      <div className="space-y-6">
        <Link
          href="/public_memory_pages"
          className="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Назад к списку
        </Link>
        <div className="text-center py-12 border-2 border-dashed rounded-xl">
          <p className="text-gray-500 text-lg">{error || 'Страница не найдена'}</p>
          <Link
            href="/public_memory_pages"
            className="mt-4 inline-block text-indigo-600 hover:text-indigo-800 font-medium"
          >
            Вернуться к списку страниц
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Хлебные крошки и действия */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-4">
          <Link
            href="/public_memory_pages"
            className="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад к списку
          </Link>
          <div className="flex items-center gap-2">
            {displayPage.is_public ? (
              <span className="inline-flex items-center gap-1 text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full">
                <Eye className="w-3 h-3" />
                Публичная
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-sm bg-gray-100 text-gray-800 px-3 py-1 rounded-full">
                <EyeOff className="w-3 h-3" />
                Приватная
              </span>
            )}
            {displayPage.is_draft && (
              <span className="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full">
                Черновик
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4">
          {/* Выбор страницы, если есть несколько */}
          {pages.length > 1 && (
            <select
              className="border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={selectedPage?.id_page}
              onChange={(e) => {
                const pageId = e.target.value
                const page = pages.find(p => p.id_page === pageId)
                setSelectedPage(page)
              }}
            >
              {pages.map(p => (
                <option key={p.id_page} value={p.id_page}>
                  {p.is_public ? 'Публичная' : 'Приватная'} {p.is_draft ? '(Черновик)' : ''} - {p.epitaph?.substring(0, 30) || 'Без эпиграфа'}
                </option>
              ))}
            </select>
          )}
          {user && displayPage.agent_id && (
            <button
              onClick={handleEditClick}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Edit className="w-4 h-4" />
              {editing ? 'Отменить редактирование' : 'Редактировать'}
            </button>
          )}
        </div>
      </div>

      {/* Заголовок */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900">{displayPage.title}</h1>
        <p className="text-xl text-gray-600 italic mt-4">"{displayPage.epitaph}"</p>
      </div>

      {editing ? (
        <>
          {/* Форма редактирования */}
          <div className="bg-white rounded-xl shadow-sm border p-6 space-y-6">
            <h2 className="text-2xl font-semibold text-gray-900">Редактирование страницы памяти</h2>
            
            {/* Поля агента */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-800">Агент</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Полное имя</label>
                  <input
                    type="text"
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editAgent?.full_name || ''}
                    onChange={(e) => setEditAgent((prev: any) => ({ ...prev, full_name: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Пол</label>
                  <select
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editAgent?.gender || ''}
                    onChange={(e) => setEditAgent((prev: any) => ({ ...prev, gender: e.target.value }))}
                  >
                    <option value="">Не указан</option>
                    <option value="M">Мужской</option>
                    <option value="F">Женский</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Дата рождения</label>
                  <input
                    type="date"
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editAgent?.birth_date?.split('T')[0] || ''}
                    onChange={(e) => setEditAgent((prev: any) => ({ ...prev, birth_date: e.target.value || null }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Дата смерти</label>
                  <input
                    type="date"
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editAgent?.death_date?.split('T')[0] || ''}
                    onChange={(e) => setEditAgent((prev: any) => ({ ...prev, death_date: e.target.value || null }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Место рождения</label>
                  <input
                    type="text"
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editAgent?.place_of_birth || ''}
                    onChange={(e) => setEditAgent((prev: any) => ({ ...prev, place_of_birth: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Место смерти</label>
                  <input
                    type="text"
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editAgent?.place_of_death || ''}
                    onChange={(e) => setEditAgent((prev: any) => ({ ...prev, place_of_death: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Тип</label>
                  <select
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editAgent?.is_human ? 'true' : 'false'}
                    onChange={(e) => setEditAgent((prev: any) => ({ ...prev, is_human: e.target.value === 'true' }))}
                  >
                    <option value="true">Человек</option>
                    <option value="false">Питомец</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Поля страницы */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-800">Страница памяти</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Эпитафия</label>
                  <input
                    type="text"
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editPage?.epitaph || ''}
                    onChange={(e) => setEditPage((prev: any) => ({ ...prev, epitaph: e.target.value }))}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Биография</label>
                  <textarea
                    rows={4}
                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    value={editPage?.biography || ''}
                    onChange={(e) => setEditPage((prev: any) => ({ ...prev, biography: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={editPage?.is_public || false}
                      onChange={(e) => setEditPage((prev: any) => ({ ...prev, is_public: e.target.checked }))}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="text-sm text-gray-700">Публичная</span>
                  </label>
                </div>
                <div>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={editPage?.is_draft || false}
                      onChange={(e) => setEditPage((prev: any) => ({ ...prev, is_draft: e.target.checked }))}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="text-sm text-gray-700">Черновик</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Кнопки действий */}
            <div className="flex flex-wrap gap-4 pt-6 border-t">
              <button
                onClick={handleUpdateAgent}
                disabled={updating}
                className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Обновить агента
              </button>
              <button
                onClick={handleUpdatePage}
                disabled={updating || !editPage}
                className="px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                Обновить страницу
              </button>
              <button
                onClick={handleUpdateBoth}
                disabled={updating}
                className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                Обновить страницу памяти
              </button>
              <button
                onClick={handleEditClick}
                className="px-4 py-2 bg-gray-300 text-gray-800 font-medium rounded-lg hover:bg-gray-400"
              >
                Отмена
              </button>
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Информация об агенте */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Информация</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="flex items-center gap-3">
                <User className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Пол</p>
                  <p className="font-medium">{displayPage.gender === 'M' ? 'Мужской' : displayPage.gender === 'F' ? 'Женский' : 'Не указан'}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Дата рождения</p>
                  <p className="font-medium">{displayPage.birth_date ? new Date(displayPage.birth_date).toLocaleDateString('ru-RU') : 'Не указана'}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Дата смерти</p>
                  <p className="font-medium">{displayPage.death_date ? new Date(displayPage.death_date).toLocaleDateString('ru-RU') : 'Не указана'}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-500">Место рождения</p>
                  <p className="font-medium">{displayPage.place_of_birth || 'Не указано'}</p>
                </div>
              </div>
            </div>
            <div className="mt-6">
              <p className="text-sm text-gray-500">Тип</p>
              <p className="font-medium">{displayPage.is_human ? 'Человек' : 'Питомец'}</p>
            </div>
          </div>

          {/* Биография */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Биография</h2>
            <div className="prose max-w-none">
              {renderBiography(displayPage.biography)}
            </div>
          </div>

          {/* Метаданные */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center text-sm text-gray-500">
            <div>
              <p>Создано: {new Date(displayPage.created_at).toLocaleDateString('ru-RU')} {new Date(displayPage.created_at).toLocaleTimeString('ru-RU')}</p>
              {displayPage.updated_at && displayPage.updated_at !== displayPage.created_at && (
                <p>Обновлено: {new Date(displayPage.updated_at).toLocaleDateString('ru-RU')} {new Date(displayPage.updated_at).toLocaleTimeString('ru-RU')}</p>
              )}
            </div>
            <p>ID страницы: {displayPage.id}</p>
          </div>
        </>
      )}
    </div>
  )
}