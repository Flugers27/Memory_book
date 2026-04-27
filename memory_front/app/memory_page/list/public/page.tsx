'use client'

import { useState, useEffect } from 'react'
import { memoryAPI } from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { Filter, Search, Eye, EyeOff, FileEdit } from 'lucide-react'
import Link from 'next/link'

type Page = {
  id: string
  title: string
  epitaph: string
  biography: string
  is_public: boolean
  is_draft: boolean
  created_at: string
  agent_id: string
}

export default function PagesList() {
  const { user } = useAuthStore()
  const [pages, setPages] = useState<Page[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'public' | 'private' | 'draft'>('all')
  const [search, setSearch] = useState('')

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

  const mapResponseToPages = (data: any): Page[] => {
    // data.memory_page_list для публичных страниц? Проверим структуру
    const list = data.memory_page_list || data.pages || []
    return list.map((item: any, index: number) => {
      const page = item.page || item
      // biography может быть массивом объектов, преобразуем в строку
      const biography = normalizeBiography(page.biography || item.biography || '')
      // Генерируем уникальный ID: используем agent_id или создаем временный
      const agentId = item.id_agent || item.agent_id
      const id = agentId || `temp-${index}-${Date.now()}`
      
      return {
        id,
        title: item.full_name || 'Без названия',
        epitaph: page.epitaph || item.epitaph || '',
        biography,
        is_public: page.is_public ?? item.is_public ?? true,
        is_draft: page.is_draft ?? item.is_draft ?? false,
        created_at: page.created_at || item.created_at || new Date().toISOString(),
        agent_id: agentId || id,
      }
    })
  }

  useEffect(() => {
    // Всегда загружаем публичные страницы на этой странице
    memoryAPI.getPublicPages().then((data) => {
      console.log('Public pages data:', data)
      const mapped = mapResponseToPages(data)
      console.log('Mapped pages:', mapped)
      setPages(mapped)
      setLoading(false)
    }).catch((err) => {
      console.error('Error fetching public pages:', err)
      setLoading(false)
    })
  }, [])

  const filteredPages = pages.filter((page) => {
    if (filter === 'public' && !page.is_public) return false
    if (filter === 'private' && page.is_public) return false
    if (filter === 'draft' && !page.is_draft) return false
    if (search) {
      const searchLower = search.toLowerCase()
      const title = page.title?.toLowerCase() || ''
      const epitaph = page.epitaph?.toLowerCase() || ''
      const biography = typeof page.biography === 'string' ? page.biography.toLowerCase() : ''
      if (!title.includes(searchLower) && !epitaph.includes(searchLower) && !biography.includes(searchLower)) {
        return false
      }
    }
    return true
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Публичные страницы памяти</h1>
          <p className="text-gray-600">
            Страницы памяти, доступные всем пользователям
          </p>
        </div>
        {user && (
          <Link
            href="/pages/create"
            className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
          >
            <FileEdit className="w-4 h-4" />
            Создать страницу
          </Link>
        )}
      </div>

      {/* Фильтры и поиск */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Поиск по имени, эпиграфу или биографии..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="text-gray-500 w-5 h-5" />
          <select
            className="border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
          >
            <option value="all">Все</option>
            <option value="public">Публичные</option>
          </select>
        </div>
      </div>

      {/* Список */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p className="mt-2 text-gray-500">Загрузка страниц...</p>
        </div>
      ) : filteredPages.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed rounded-xl">
          <p className="text-gray-500 text-lg">Страницы памяти не найдены</p>
          {user && (
            <Link
              href="/pages/create"
              className="mt-4 inline-block text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Создайте первую страницу
            </Link>
          )}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPages.map((page) => (
            <div
              key={page.id}
              className="bg-white rounded-xl shadow-sm border overflow-hidden hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 truncate">{page.title}</h3>
                  <div className="flex items-center gap-2">
                    {page.is_public ? (
                      <Eye className="w-4 h-4 text-green-600" />
                    ) : (
                      <EyeOff className="w-4 h-4 text-gray-600" />
                    )}
                    {page.is_draft && (
                      <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                        Черновик
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-gray-700 italic border-l-4 border-indigo-300 pl-3 mb-4">
                  "{page.epitaph}"
                </p>
                <p className="text-gray-600 line-clamp-3 mb-6">{page.biography}</p>
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>{new Date(page.created_at).toLocaleDateString('ru-RU')}</span>
                  <Link
                    href={`/memory_page/public/${page.agent_id}`}
                    className="text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Подробнее →
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}