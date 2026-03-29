"use client";

import { useAuth } from "@/components/AuthProvider";
import { Copy, Plus, FileText, CheckCircle2, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const { user } = useAuth();
  
  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center p-20">
        <h2 className="text-2xl font-bold mb-4">Для доступа к профилю необходимо авторизоваться</h2>
        <p className="text-gray-400 mb-8">Используйте кнопку Telegram в верхнем меню</p>
      </div>
    );
  }

  const isPiloteVerified = user.has_license;
  const isCompany = user.user_type === "company";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Личный кабинет</h1>
          <p className="text-gray-400">Добро пожаловать в панель управления экосистемой SkyRent</p>
        </div>
        <div className="mt-4 md:mt-0 flex space-x-4">
          <Link href="/catalog/create" className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-xl transition-colors flex items-center shadow-lg shadow-blue-500/20">
            <Plus className="w-4 h-4 mr-2" />
            Добавить Технику
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Profile Card */}
        <div className="col-span-1 md:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
          <div className="flex items-start gap-6">
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-tr from-blue-500/20 to-cyan-500/20 flex items-center justify-center border border-white/10 overflow-hidden">
              {user.photo_url ? (
                <img src={user.photo_url} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <span className="text-3xl font-bold text-blue-400">{user.first_name?.[0]}</span>
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-white">{user.first_name} {user.last_name || ""}</h2>
                {isPiloteVerified && (
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center text-xs font-semibold">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Проверенный Пилот
                  </span>
                )}
              </div>
              
              <div className="space-y-1 mb-4">
                <p className="text-sm text-gray-400 flex items-center">
                  <span className="w-24">Статус:</span>
                  <span className="text-white font-medium">{isCompany ? "🏢 Компания" : "👤 Частное лицо"}</span>
                </p>
                <p className="text-sm text-gray-400 flex items-center">
                  <span className="w-24">Telegram ID:</span>
                  <span className="text-white font-medium flex items-center">
                    {user.id} 
                    <button className="ml-2 text-gray-500 hover:text-white"><Copy className="w-3 h-3" /></button>
                  </span>
                </p>
              </div>

              {!isPiloteVerified && (
                <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-3 flex items-start gap-3">
                  <ShieldAlert className="w-5 h-5 text-orange-400 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-semibold text-orange-400 mb-1">Получите статус «Проверен»</h4>
                    <p className="text-xs text-orange-300/80 mb-2">Подтвердите ВЛЭК и лицензию, чтобы продвигаться в ТОП и получать лучшие заказы.</p>
                    <button className="text-xs font-semibold px-3 py-1.5 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors">
                      Пройти верификацию
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Balance Card */}
        <div className="col-span-1 bg-gradient-to-br from-blue-900/40 to-[#0A0A0B] border border-blue-500/20 rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/20 rounded-full mix-blend-screen filter blur-3xl" />
          
          <h3 className="text-lg font-bold text-white mb-6">Баланс</h3>
          
          <div className="mb-6">
            <span className="text-4xl font-black text-white">0 <span className="text-xl text-gray-400 font-medium">₽</span></span>
          </div>
          
          <div className="flex gap-3">
            <button className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-xl transition-colors text-center shadow-lg shadow-blue-500/20">
              Пополнить
            </button>
          </div>
        </div>
      </div>

      <h2 className="text-xl font-bold text-white mb-4">Быстрый доступ</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link href="/dashboard/tasks" className="bg-white/5 hover:bg-white/10 border border-white/5 rounded-2xl p-4 flex flex-col items-center justify-center text-center transition-all hover:-translate-y-1 cursor-pointer">
          <div className="w-12 h-12 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center mb-3">
            <FileText className="w-6 h-6" />
          </div>
          <span className="font-semibold text-white">Мои Задачи</span>
          <span className="text-xs text-gray-400 mt-1">Актуальные работы</span>
        </Link>
        <Link href="/dashboard/orvd" className="bg-white/5 hover:bg-white/10 border border-white/5 rounded-2xl p-4 flex flex-col items-center justify-center text-center transition-all hover:-translate-y-1 cursor-pointer">
          <div className="w-12 h-12 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-3">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <span className="font-semibold text-white">ОрВД (Планы)</span>
          <span className="text-xs text-gray-400 mt-1">Генератор запросов</span>
        </Link>
      </div>
    </div>
  );
}
