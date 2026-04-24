'use client'

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/lib/store'
import { authAPI, memoryAPI } from '@/lib/api'
import { toast } from 'sonner'
import { User, Mail, Calendar, FileText, LogOut } from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function ProfilePage() {
  const { user, clearUser } = useAuthStore()
  const router = useRouter()
  const [pageCount, setPageCount] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }
    memoryAPI.getUserPages().then((data) => {
      const list = data.memory_page_list || data.pages || []
      setPageCount(list.length)
      setLoading(false)
    }).catch(() => {
      setLoading(false)
    })
  }, [user, router])

  const handleLogout = () => {
    authAPI.logout().finally(() => {
      clearUser()
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      toast.success('Вы вышли из аккаунта')
      router.push('/')
    })
  }

  if (!user) return null

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-8 text-white mb-8">
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center space-x-6">
            <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
              <User className="w-12 h-12" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">{user.email}</h1>
              <p className="text-indigo-100">Участник Memory Book</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="mt-6 md:mt-0 flex items-center gap-2 px-6 py-3 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Выйти
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500">Страниц памяти</p>
              <p className="text-3xl font-bold text-gray-900">{loading ? '...' : pageCount}</p>
            </div>
            <FileText className="w-10 h-10 text-indigo-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500">Email</p>
              <p className="text-xl font-semibold text-gray-900 truncate">{user.email}</p>
            </div>
            <Mail className="w-10 h-10 text-indigo-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500">ID пользователя</p>
              <p className="text-sm font-mono text-gray-900 truncate">{user.id}</p>
            </div>
            <User className="w-10 h-10 text-indigo-600" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          Активность
        </h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium">Создание аккаунта</p>
              <p className="text-sm text-gray-500">Дата регистрации</p>
            </div>
            <p className="text-gray-700">—</p>
          </div>
          <div className="flex items-center justify-between py-3 border-b">
            <div>
              <p className="font-medium">Последний вход</p>
              <p className="text-sm text-gray-500">Сегодня, 14:30</p>
            </div>
            <p className="text-gray-700">—</p>
          </div>
          <div className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium">Статус аккаунта</p>
              <p className="text-sm text-gray-500">Активен</p>
            </div>
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              Активен
            </span>
          </div>
        </div>
      </div>

      <div className="mt-8 text-center text-gray-500 text-sm">
        <p>Если у вас есть вопросы, обратитесь в поддержку support@memorybook.example.com</p>
      </div>
    </div>
  )
}