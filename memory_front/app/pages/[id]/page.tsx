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

  useEffect(() => {
    if (!pageId) return

    const fetchPage = async () => {
      try {
        let data
        if (user) {
          // Пытаемся получить страницу как свою (требует авторизации)
          try {
            data = await memoryAPI.getUserPage(pageId)
          } catch (err: any) {
            // Если 404 или 403, возможно, это публичная страница другого пользователя
            console.log('Failed to fetch as user page, trying public...')
            data = await memoryAPI.getPublicPage(pageId)
          }
        } else {
          data = await memoryAPI.getPublicPage(pageId)
        }

        // Преобразуем данные
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
        setError(null)
      } catch (err: any) {
        console.error('Error fetching page:', err)
        setError('Не удалось загрузить страницу памяти. Возможно, она не существует или у вас нет доступа.')
      } finally {
        setLoading(false)
      }
    }

    fetchPage()
  }, [pageId, user])

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p className="mt-2 text-gray-500">Загрузка страницы памяти...</p>
      </div>
    )
  }

  if (error || !page) {
    return (
      <div className="space-y-6">
        <Link
          href="/pages"
          className="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Назад к списку
        </Link>
        <div className="text-center py-12 border-2 border-dashed rounded-xl">
          <p className="text-gray-500 text-lg">{error || 'Страница не найдена'}</p>
          <Link
            href="/pages"
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
            href="/pages"
            className="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад к списку
          </Link>
          <div className="flex items-center gap-2">
            {page.is_public ? (
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
            {page.is_draft && (
              <span className="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full">
                Черновик
              </span>
            )}
          </div>
        </div>
        {user && page.agent_id && (
          <Link
            href={`/pages/edit/${page.id}`}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Edit className="w-4 h-4" />
            Редактировать
          </Link>
        )}
      </div>

      {/* Заголовок */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900">{page.title}</h1>
        <p className="text-xl text-gray-600 italic mt-4">"{page.epitaph}"</p>
      </div>

      {/* Информация об агенте */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Информация</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="flex items-center gap-3">
            <User className="w-5 h-5 text-gray-500" />
            <div>
              <p className="text-sm text-gray-500">Пол</p>
              <p className="font-medium">{page.gender === 'M' ? 'Мужской' : page.gender === 'F' ? 'Женский' : 'Не указан'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-gray-500" />
            <div>
              <p className="text-sm text-gray-500">Дата рождения</p>
              <p className="font-medium">{page.birth_date ? new Date(page.birth_date).toLocaleDateString('ru-RU') : 'Не указана'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-gray-500" />
            <div>
              <p className="text-sm text-gray-500">Дата смерти</p>
              <p className="font-medium">{page.death_date ? new Date(page.death_date).toLocaleDateString('ru-RU') : 'Не указана'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <MapPin className="w-5 h-5 text-gray-500" />
            <div>
              <p className="text-sm text-gray-500">Место рождения</p>
              <p className="font-medium">{page.place_of_birth || 'Не указано'}</p>
            </div>
          </div>
        </div>
        <div className="mt-6">
          <p className="text-sm text-gray-500">Тип</p>
          <p className="font-medium">{page.is_human ? 'Человек' : 'Питомец'}</p>
        </div>
      </div>

      {/* Биография */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Биография</h2>
        <div className="prose max-w-none">
          <p className="text-gray-700 whitespace-pre-line">{page.biography}</p>
        </div>
      </div>

      {/* Метаданные */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center text-sm text-gray-500">
        <div>
          <p>Создано: {new Date(page.created_at).toLocaleDateString('ru-RU')} {new Date(page.created_at).toLocaleTimeString('ru-RU')}</p>
          {page.updated_at && page.updated_at !== page.created_at && (
            <p>Обновлено: {new Date(page.updated_at).toLocaleDateString('ru-RU')} {new Date(page.updated_at).toLocaleTimeString('ru-RU')}</p>
          )}
        </div>
        <p>ID страницы: {page.id}</p>
      </div>
    </div>
  )
}