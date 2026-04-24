import { BookOpen, Shield, Users, Heart } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Герой секция */}
      <section className="text-center py-12 px-4 max-w-4xl mx-auto">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Сохраните память о близких навсегда
        </h1>
        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
          Memory Book — это сервис для создания страниц памяти об ушедших членах семьи и питомцах. 
          Храните фотографии, истории, даты и делитесь светлыми воспоминаниями.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/pages"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-8 py-3 text-lg font-semibold text-white hover:bg-indigo-700 transition-colors"
          >
            <BookOpen className="w-5 h-5" />
            Смотреть страницы памяти
          </Link>
          <Link
            href="/register"
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-8 py-3 text-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Users className="w-5 h-5" />
            Присоединиться
          </Link>
        </div>
      </section>

      {/* Особенности */}
      <section className="py-12">
        <h2 className="text-3xl font-bold text-center mb-12">Почему выбирают Memory Book?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
            <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mb-6">
              <Heart className="w-6 h-6 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold mb-4">Вечная память</h3>
            <p className="text-gray-600">
              Создайте страницу с биографией, фотографиями и важными датами. Сохраните память для будущих поколений.
            </p>
          </div>
          <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-6">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-xl font-bold mb-4">Совместный доступ</h3>
            <p className="text-gray-600">
              Пригласите родственников дополнять страницу. Управляйте правами доступа — только чтение или редактирование.
            </p>
          </div>
          <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mb-6">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold mb-4">Конфиденциальность</h3>
            <p className="text-gray-600">
              Вы решаете, сделать страницу публичной или приватной. Все данные надёжно защищены.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-3xl p-10 text-center text-white">
        <h2 className="text-3xl font-bold mb-6">Начните бесплатно сегодня</h2>
        <p className="text-xl mb-8 opacity-90">
          Создайте первую страницу памяти за 5 минут. Никаких скрытых платежей.
        </p>
        <Link
          href="/register"
          className="inline-flex items-center justify-center gap-2 rounded-full bg-white px-10 py-4 text-lg font-bold text-indigo-600 hover:bg-gray-100 transition-colors"
        >
          Создать аккаунт
        </Link>
      </section>

      {/* Статистика */}
      <section className="py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-4xl font-bold text-indigo-600">5K+</div>
            <div className="text-gray-600">страниц памяти</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-indigo-600">2K+</div>
            <div className="text-gray-600">семей</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-indigo-600">99.9%</div>
            <div className="text-gray-600">доступность</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-indigo-600">24/7</div>
            <div className="text-gray-600">поддержка</div>
          </div>
        </div>
      </section>
    </div>
  );
}
