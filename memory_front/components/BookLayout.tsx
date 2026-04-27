'use client'

import { ReactNode, useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'

interface BookLayoutProps {
  children: ReactNode
}

export default function BookLayout({ children }: BookLayoutProps) {
  const pathname = usePathname()
  const [isTurning, setIsTurning] = useState(false)

  // Эффект перелистывания при смене страницы
  useEffect(() => {
    setIsTurning(true)
    const timer = setTimeout(() => setIsTurning(false), 600)
    return () => clearTimeout(timer)
  }, [pathname])

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100 p-4 md:p-8 flex justify-center items-start">
      {/* Книжная обложка и тень */}
      <div className="relative w-full max-w-6xl">
        {/* Тень книги */}
        <div className="absolute -bottom-4 left-4 right-4 h-8 bg-gradient-to-t from-amber-900/20 to-transparent rounded-full blur-md"></div>

        {/* Книга */}
        <div className="relative bg-gradient-to-r from-amber-100 to-amber-50 border-8 border-amber-300 rounded-xl shadow-2xl overflow-hidden">
          {/* Корешок книги слева */}
          <div className="absolute left-0 top-0 bottom-0 w-6 bg-gradient-to-r from-amber-800 to-amber-600 border-r-4 border-amber-900"></div>

          {/* Верхняя часть книги (заголовок) */}
          <div className="pt-8 pb-4 px-12 border-b-2 border-amber-300 bg-gradient-to-b from-amber-200 to-amber-100">
            <h1 className="text-3xl font-serif text-amber-900 text-center italic">
              Книга памяти
            </h1>
            <p className="text-center text-amber-700 mt-2 font-serif">
              Страница: {pathname.split('/').pop() || 'Главная'}
            </p>
          </div>

          {/* Контент страницы с эффектом перелистывания */}
          <div className={`p-8 md:p-12 transition-all duration-500 ${isTurning ? 'opacity-0 scale-95' : 'opacity-100 scale-100'}`}>
            <div className="prose prose-lg max-w-none font-serif text-amber-900">
              {children}
            </div>
          </div>

          {/* Номер страницы внизу */}
          <div className="px-12 py-6 border-t-2 border-amber-300 bg-gradient-to-t from-amber-200 to-amber-100 text-center">
            <span className="text-amber-700 font-serif italic">
              — Страница {Math.floor(Math.random() * 100) + 1} —
            </span>
          </div>
        </div>

        {/* Декоративные уголки */}
        <div className="absolute -top-4 -left-4 w-8 h-8 border-t-4 border-l-4 border-amber-500 rounded-tl-xl"></div>
        <div className="absolute -top-4 -right-4 w-8 h-8 border-t-4 border-r-4 border-amber-500 rounded-tr-xl"></div>
        <div className="absolute -bottom-4 -left-4 w-8 h-8 border-b-4 border-l-4 border-amber-500 rounded-bl-xl"></div>
        <div className="absolute -bottom-4 -right-4 w-8 h-8 border-b-4 border-r-4 border-amber-500 rounded-br-xl"></div>
      </div>
    </div>
  )
}