'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, BookOpen, PlusCircle, User, LogIn, UserPlus, Book } from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { useEffect, useState } from 'react'
import { authAPI } from '@/lib/api'

export default function Navbar() {
  const pathname = usePathname()
  const { user, setUser, clearUser } = useAuthStore()

  useEffect(() => {
    // Проверяем токен при загрузке
    const token = localStorage.getItem('access_token')
    if (token) {
      authAPI.validateToken(token).then((res) => {
        if (res.valid) {
          setUser({ id: res.user_id, email: res.email })
        } else {
          clearUser()
          localStorage.removeItem('access_token')
        }
      }).catch(() => {
        clearUser()
        localStorage.removeItem('access_token')
      })
    }
  }, [setUser, clearUser])

  const [bookTheme, setBookTheme] = useState(false)

  useEffect(() => {
    // Отключаем книжную тему по умолчанию, даже если ранее была включена
    localStorage.removeItem('bookTheme')
    setBookTheme(false)
  }, [])

  const toggleBookTheme = () => {
    const newValue = !bookTheme
    setBookTheme(newValue)
    localStorage.setItem('bookTheme', newValue.toString())
    // Перезагружаем страницу для применения темы (можно обойтись без перезагрузки, но для простоты)
    window.location.reload()
  }

  const handleLogout = () => {
    authAPI.logout().finally(() => {
      clearUser()
      localStorage.removeItem('access_token')
    })
  }

  const navItems = [
    { href: '/', label: 'Главная', icon: <Home className="w-4 h-4" /> },
    { href: '/memory_page/list/public', label: 'Страницы памяти', icon: <BookOpen className="w-4 h-4" /> },
  ]

  if (user) {
    navItems.push(
      { href: '/memory_page/list/my', label: 'Мои страницы памяти', icon: <BookOpen className="w-4 h-4" /> },
      { href: '/memory_page/my/create', label: 'Создать страницу', icon: <PlusCircle className="w-4 h-4" /> },
      { href: '/user/profile', label: 'Профиль', icon: <User className="w-4 h-4" /> }
    )
  }

  return (
    <nav className="sticky top-0 z-50 border-b bg-white shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-2 text-xl font-bold text-indigo-700">
              <BookOpen className="w-6 h-6" />
              <span>Memory Book</span>
            </Link>
            <div className="hidden md:flex items-center space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-lg transition-colors ${pathname === item.href
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-700 hover:bg-gray-100'
                    }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {/* Кнопка переключения темы книги */}
            <button
              onClick={toggleBookTheme}
              className={`flex items-center space-x-1 px-3 py-2 rounded-lg transition-colors ${bookTheme ? 'bg-amber-100 text-amber-800 border border-amber-300' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              title={bookTheme ? 'Переключить на обычный дизайн' : 'Переключить на дизайн книги'}
            >
              <Book className="w-4 h-4" />
              <span className="hidden md:inline">{bookTheme ? 'Книга' : 'Книга'}</span>
            </button>

            {user ? (
              <>
                <span className="text-sm text-gray-600">{user.email}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Выйти
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/user/login"
                  className="flex items-center space-x-1 px-4 py-2 text-sm font-medium text-gray-700 hover:text-indigo-700 transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Вход</span>
                </Link>
                <Link
                  href="/user/register"
                  className="flex items-center space-x-1 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Регистрация</span>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}