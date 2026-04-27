'use client'

import { useEffect, useState } from 'react'
import BookLayout from './BookLayout'

interface ClientLayoutWrapperProps {
  children: React.ReactNode
}

export default function ClientLayoutWrapper({ children }: ClientLayoutWrapperProps) {
  const [bookTheme, setBookTheme] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('bookTheme')
    if (saved === 'true') {
      setBookTheme(true)
    }
    setMounted(true)
  }, [])

  if (!mounted) {
    // Пока не смонтировано, рендерим обычный контейнер без темы, чтобы избежать гидратационных ошибок
    return <div className="min-h-screen">{children}</div>
  }

  if (bookTheme) {
    return <BookLayout>{children}</BookLayout>
  }

  // Обычный контейнер (как в основном layout)
  return <div className="container mx-auto px-4 py-8">{children}</div>
}