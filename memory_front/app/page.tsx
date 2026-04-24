import Link from 'next/link'
import { BookOpen, Heart, Users, Shield } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center py-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Сохраняйте память о близких
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-10">
          Memory Book — это сервис для создания страниц памяти об умерших членах семьи и питомцах.
          Делитесь воспоминаниями, храните фотографии и эпиграфы в безопасном цифровом пространстве.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/pages"
            className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Посмотреть страницы памяти
          </Link>
          <Link
            href="/register"
            className="px-8 py-3 border-2 border-indigo-600 text-indigo-600 font-semibold rounded-lg hover:bg-indigo-50 transition-colors"
          >
            Создать аккаунт
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        <div className="p-6 bg-white rounded-xl shadow-sm border">
          <BookOpen className="w-12 h-12 text-indigo-600 mb-4" />
          <h3 className="text-xl font-semibold mb-2">Страницы памяти</h3>
          <p className="text-gray-600">
            Создайте персонализированную страницу с биографией, фотографиями и эпиграфом.
          </p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border">
          <Shield className="w-12 h-12 text-indigo-600 mb-4" />
          <h3 className="text-xl font-semibold mb-2">Конфиденциальность</h3>
          <p className="text-gray-600">
            Настройте видимость: публичная страница, только для семьи или черновик.
          </p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border">
          <Users className="w-12 h-12 text-indigo-600 mb-4" />
          <h3 className="text-xl font-semibold mb-2">Совместный доступ</h3>
          <p className="text-gray-600">
            Пригласите родственников для совместного редактирования и дополнения воспоминаний.
          </p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow-sm border">
          <Heart className="w-12 h-12 text-indigo-600 mb-4" />
          <h3 className="text-xl font-semibold mb-2">Вечная память</h3>
          <p className="text-gray-600">
            Сохраните светлые моменты и передайте историю будущим поколениям.
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-10 text-center">
        <h2 className="text-3xl font-bold mb-4">Начните создавать память сегодня</h2>
        <p className="text-gray-700 mb-8 max-w-2xl mx-auto">
          Зарегистрируйтесь бесплатно и создайте свою первую страницу памяти за несколько минут.
        </p>
        <Link
          href="/pages/create"
          className="inline-flex items-center px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:opacity-90 transition-opacity"
        >
          Создать страницу памяти
        </Link>
      </section>
    </div>
  )
}