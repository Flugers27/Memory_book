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

export default function MyPagesList() {
  const { user } = useAuthStore()
  const [pages, setPages] = useState<Page[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'public' | 'private' | 'draft'>('all')
  const [search, setSearch] = useState('')

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

  const mapResponseToPages = (data: any): Page[] => {
    // data.memory_page_list - список объектов MemoryPageResponse (agent + pages)
    const list = data.memory_page_list || []
    console.log('Raw memory_page_list:', list)
    const result: Page[] = []
    
    // Группируем страницы по агентам
    const agentsMap: Record<string, { agent: any; pages: any[] }> = {}
    
    list.forEach((memoryPage: any, index: number) => {
      const agent = memoryPage.agent
      const pages = memoryPage.pages || []
      const agentId = agent?.id_agent
      console.log(`Item ${index}: agentId=${agentId}, pages count=${pages.length}`)
      if (!agentId) return
      
      if (!agentsMap[agentId]) {
        agentsMap[agentId] = { agent, pages: [] }
      }
      // Добавляем все страницы этого агента
      agentsMap[agentId].pages.push(...pages)
    })
    
    console.log('AgentsMap after grouping:', agentsMap)
    
    // Для каждого агента выбираем одну страницу по приоритету
    Object.values(agentsMap).forEach(({ agent, pages }) => {
      const selectedPage = selectPriorityPage(pages)
      const agentId = agent?.id_agent
      console.log(`Agent ${agentId}: total pages=${pages.length}, selected page=`, selectedPage)
      
      let biography = ''
      let epitaph = ''
      let is_public = false
      let is_draft = false
      let created_at = agent?.created_at || new Date().toISOString()
      
      if (selectedPage) {
        biography = selectedPage.biography || ''
        if (Array.isArray(biography)) {
          const first = biography[0]
          if (first?.info) biography = first.info
          else if (first?.title) biography = first.title
          else biography = JSON.stringify(biography)
        }
        epitaph = selectedPage.epitaph || ''
        is_public = selectedPage.is_public ?? true
        is_draft = selectedPage.is_draft ?? false
        created_at = selectedPage.created_at || created_at
      }
      
      // ID для ссылки - agent_id
      const id = agentId || `agent-${Date.now()}`
      
      result.push({
        id,
        title: agent?.full_name || 'Без названия',
        epitaph,
        biography,
        is_public,
        is_draft,
        created_at,
        agent_id: agentId || id,
      })
    })
    
    console.log('Result pages:', result)
    return result
  }

  useEffect(() => {
    if (user) {
      memoryAPI.getUserPages().then((data) => {
        console.log('My pages data:', data)
        const mapped = mapResponseToPages(data)
        console.log('Mapped my pages:', mapped)
        setPages(mapped)
        setLoading(false)
      }).catch((err) => {
        console.error('Error fetching my pages:', err)
        setLoading(false)
      })
    } else {
      // Если пользователь не авторизован, перенаправить на страницу входа?
      // Пока просто очистим список
      setPages([])
      setLoading(false)
    }
  }, [user])

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

  if (!user) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <h1 className="text-3xl font-bold text-gray-900">Мои страницы памяти</h1>
          <p className="text-gray-600 mt-2">Для просмотра своих страниц необходимо войти в систему.</p>
          <Link
            href="/user/login"
            className="mt-6 inline-block px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Войти
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Мои страницы памяти</h1>
          <p className="text-gray-600">Все ваши страницы памяти, включая приватные и черновики</p>
        </div>
        <Link
          href="/memory_page/my/create"
          className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
        >
          <FileEdit className="w-4 h-4" />
          Создать страницу
        </Link>
      </div>

      {/* Фильтры и поиск */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Поиск по названию или эпиграфу..."
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
            <option value="private">Приватные</option>
            <option value="draft">Черновики</option>
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
          <p className="text-gray-500 text-lg">У вас ещё нет страниц памяти</p>
          <Link
            href="/memory_page/my/create"
            className="mt-4 inline-block text-indigo-600 hover:text-indigo-800 font-medium"
          >
            Создайте первую страницу
          </Link>
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
                    href={`/memory_page/my/${page.agent_id}`}
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