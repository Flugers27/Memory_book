import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navbar from '@/components/Navbar'
import { Toaster } from 'sonner'
import ClientLayoutWrapper from '@/components/ClientLayoutWrapper'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Memory Book - Страницы памяти',
  description: 'Создание страниц памяти для умерших членов семьи и питомцев',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ru">
      <body className={`${inter.className} min-h-screen bg-gray-50`}>
        <Navbar />
        <main>
          <ClientLayoutWrapper>{children}</ClientLayoutWrapper>
        </main>
        <Toaster richColors position="top-right" />
        <footer className="mt-12 border-t py-6 text-center text-gray-500">
          <p>© {new Date().getFullYear()} Memory Book. Все права защищены.</p>
        </footer>
      </body>
    </html>
  )
}