'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authAPI } from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { toast } from 'sonner'
import { LogIn, Mail, Lock } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const { setUser } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const decodeJWT = (token: string) => {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      let jsonPayload
      if (typeof window !== 'undefined') {
        // Браузерная среда
        jsonPayload = decodeURIComponent(
          atob(base64)
            .split('')
            .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        )
      } else {
        // Node.js среда (во время сборки)
        jsonPayload = Buffer.from(base64, 'base64').toString('utf-8')
      }
      return JSON.parse(jsonPayload)
    } catch {
      return null
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await authAPI.login({ email, password })
      const { access_token, refresh_token } = response
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      
      // Decode JWT to get user info
      const decoded = decodeJWT(access_token)
      if (decoded) {
        setUser({ id: decoded.sub, email: decoded.email })
      } else {
        // Fallback: use email from form
        setUser({ id: '', email })
      }
      
      toast.success('Вход выполнен успешно!')
      router.push('/pages')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка входа. Проверьте данные.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Вход в аккаунт</h1>
        <p className="text-gray-600 mt-2">
          Введите ваши данные для доступа к страницам памяти
        </p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Mail className="inline w-4 h-4 mr-1" />
            Email
          </label>
          <input
            type="email"
            required
            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="example@mail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Lock className="inline w-4 h-4 mr-1" />
            Пароль
          </label>
          <input
            type="password"
            required
            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Вход...
            </>
          ) : (
            <>
              <LogIn className="w-5 h-5" />
              Войти
            </>
          )}
        </button>
      </form>
      <div className="mt-8 text-center">
        <p className="text-gray-600">
          Ещё нет аккаунта?{' '}
          <Link href="/register" className="text-indigo-600 hover:text-indigo-800 font-medium">
            Зарегистрироваться
          </Link>
        </p>
        <p className="mt-2 text-sm text-gray-500">
          <Link href="/forgot-password" className="hover:text-indigo-600">
            Забыли пароль?
          </Link>
        </p>
      </div>
    </div>
  )
}