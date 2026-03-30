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
          <p className="text-gray-400">Добро пожаловать в панель управления экосистемой «Горизонт»</p>
        </div>
        <div className="mt-4 md:mt-0 flex space-x-4">
          <Link href="/catalog/create" className="px-5 py-2.5 bg-gradient-to-r from-khokhloma-gold to-khokhloma-red hover:from-yellow-500 hover:to-red-600 text-white text-sm font-bold rounded-xl transition-all hover:-translate-y-0.5 flex items-center shadow-lg shadow-khokhloma-red/20">
            <Plus className="w-4 h-4 mr-2" />
            Добавить Технику
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="col-span-1 md:col-span-2 bg-[#111111]/90 border border-white/5 rounded-2xl p-6 backdrop-blur-xl shadow-2xl relative overflow-hidden group hover:border-khokhloma-gold/30 transition-colors">
          <div className="absolute inset-0 bg-pattern-khokhloma opacity-20 pointer-events-none"></div>
          <div className="absolute top-0 right-0 w-64 h-64 bg-khokhloma-gold/5 rounded-full filter blur-[80px] pointer-events-none"></div>
          <div className="flex items-start gap-6 relative z-10">
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-tr from-khokhloma-red/20 to-khokhloma-gold/20 flex items-center justify-center border border-khokhloma-gold/20 overflow-hidden shadow-inner backdrop-blur-md">
              {user.photo_url ? (
                <img src={user.photo_url} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <span className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-khokhloma-gold to-yellow-600 drop-shadow-sm">{user.first_name?.[0]}</span>
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

        <div className="col-span-1 bg-gradient-to-br from-[#1a1a1a] to-[#0A0A0B] border border-white/5 hover:border-khokhloma-red/30 rounded-2xl p-6 relative overflow-hidden transition-colors shadow-2xl">
          <div className="absolute inset-0 bg-pattern-khokhloma opacity-10 pointer-events-none"></div>
          <div className="absolute top-0 right-0 w-32 h-32 bg-khokhloma-red/10 rounded-full mix-blend-screen filter blur-3xl pointer-events-none" />
          
          <h3 className="text-lg font-bold text-gray-300 mb-6 uppercase tracking-wider text-xs relative z-10">Баланс Счета</h3>
          
          <div className="mb-6 relative z-10">
            <span className="text-4xl font-extrabold text-white drop-shadow-md">0 <span className="text-xl text-khokhloma-gold font-medium">₽</span></span>
          </div>
          
          <div className="flex gap-3">
            <button className="flex-1 py-2.5 bg-white/5 border border-white/10 hover:border-khokhloma-gold/50 hover:bg-khokhloma-gold/10 text-white text-sm font-bold rounded-xl transition-all text-center">
              Пополнить
            </button>
          </div>
        </div>
      </div>

      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><div className="w-1.5 h-6 bg-khokhloma-gold rounded-full"></div>Быстрый доступ</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link href="/dashboard/tasks" className="relative overflow-hidden group bg-[#111111]/80 hover:bg-[#1a1a1a] border border-white/5 hover:border-khokhloma-gold/30 rounded-2xl p-4 flex flex-col items-center justify-center text-center transition-all hover:-translate-y-1 cursor-pointer shadow-lg shadow-black/50">
          <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-pattern-khokhloma opacity-5 group-hover:opacity-20 transition-opacity duration-500 rounded-full" style={{ maskImage: "radial-gradient(circle, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 70%)", WebkitMaskImage: "radial-gradient(circle, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 70%)", transform: "rotate(-15deg)" }}></div>
          <div className="relative z-10 w-12 h-12 rounded-xl bg-khokhloma-gold/10 text-khokhloma-gold flex items-center justify-center mb-3 group-hover:bg-khokhloma-gold/20 transition-colors">
            <FileText className="w-6 h-6" />
          </div>
          <span className="relative z-10 font-bold text-white group-hover:text-khokhloma-gold transition-colors">Мои Задачи</span>
          <span className="relative z-10 text-xs text-gray-400 mt-1">Актуальные работы</span>
        </Link>
        <Link href="/dashboard/orvd" className="relative overflow-hidden group bg-[#111111]/80 hover:bg-[#1a1a1a] border border-white/5 hover:border-khokhloma-red/30 rounded-2xl p-4 flex flex-col items-center justify-center text-center transition-all hover:-translate-y-1 cursor-pointer shadow-lg shadow-black/50">
          <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-pattern-khokhloma opacity-5 group-hover:opacity-20 transition-opacity duration-500 rounded-full" style={{ maskImage: "radial-gradient(circle, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 70%)", WebkitMaskImage: "radial-gradient(circle, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 70%)", transform: "rotate(-15deg)" }}></div>
          <div className="relative z-10 w-12 h-12 rounded-xl bg-khokhloma-red/10 text-khokhloma-red flex items-center justify-center mb-3 group-hover:bg-khokhloma-red/20 transition-colors">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <span className="relative z-10 font-bold text-white group-hover:text-khokhloma-red transition-colors">ОрВД (Планы)</span>
          <span className="relative z-10 text-xs text-gray-400 mt-1">Генератор запросов</span>
        </Link>
      </div>
    </div>
  );
}
