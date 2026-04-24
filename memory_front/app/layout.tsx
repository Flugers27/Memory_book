import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = {
  title: "Memory Book - Управление воспоминаниями",
  description: "Приложение для хранения и организации ваших воспоминаний",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50 text-gray-900`}>
        <div className="min-h-full flex flex-col">
          <Navbar />
          <main className="flex-1 container mx-auto px-4 py-8">{children}</main>
          <footer className="border-t bg-white py-6">
            <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
              <p>Memory Book &copy; {new Date().getFullYear()} — храните свои воспоминания безопасно</p>
              <p className="mt-1">Версия 1.0.0</p>
            </div>
          </footer>
        </div>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
