"use client";

import { useAuth } from "@/components/AuthProvider";
import { CheckCircle2, Clock, FileText, FileCheck, ExternalLink, Navigation } from "lucide-react";
import Link from "next/link";

export default function MyTasksPage() {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center p-20 text-center">
        <h2 className="text-2xl font-bold mb-4">Авторизуйтесь для просмотра ваших задач</h2>
        <p className="text-gray-400">Только пользователи системы могут управлять сделками.</p>
      </div>
    );
  }

  // Dummy tasks data representing MVP state
  const tasks = [
    {
      id: "784",
      title: "Аэрофотосъемка земельного участка (10 Га)",
      role: "Исполнитель (Пилот)",
      city: "Москва",
      budget: "15 000 ₽",
      status: "in_progress",
      date: "2026-04-05",
      employerId: "9832145"
    },
    {
      id: "762",
      title: "Аренда DJI Mavic 3 Enterprise RTK",
      role: "Арендатор",
      city: "Санкт-Петербург",
      budget: "5 000 ₽ / день",
      status: "in_progress",
      date: "2026-03-30",
      employerId: "1029345"
    },
    {
      id: "710",
      title: "Тепловизионная инспекция фасада БЦ",
      role: "Исполнитель (Пилот)",
      city: "Екатеринбург",
      budget: "25 000 ₽",
      status: "completed",
      date: "2026-03-20",
      employerId: "5812390"
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-white mb-2">Мои Задачи</h1>
        <p className="text-gray-400">
          Управление вашими активными заказами, сделками по аренде и документами.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Sidebar Stats */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-blue-600/10 border border-blue-500/20 rounded-2xl p-6">
            <h3 className="text-blue-400 font-bold mb-1">Актуальные</h3>
            <div className="text-3xl font-black text-white">2 <span className="text-sm font-medium text-blue-300">задачи</span></div>
          </div>
          <div className="bg-emerald-600/10 border border-emerald-500/20 rounded-2xl p-6">
            <h3 className="text-emerald-400 font-bold mb-1">Завершено</h3>
            <div className="text-3xl font-black text-white">12 <span className="text-sm font-medium text-emerald-300">сделок</span></div>
          </div>
          <div className="bg-[#0A0A0B] border border-white/10 rounded-2xl p-6">
            <h3 className="text-gray-400 font-bold mb-4 text-sm uppercase tracking-wider">Инструменты</h3>
            <div className="space-y-3">
              <Link href="/dashboard/orvd" className="flex items-center text-sm text-gray-300 hover:text-white transition-colors group">
                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center mr-3 group-hover:bg-indigo-500/20 group-hover:text-indigo-400 transition-colors">
                  <Navigation className="w-4 h-4" />
                </div>
                ЕС ОрВД (ИВП)
              </Link>
              <Link href="/dashboard/docs" className="flex items-center text-sm text-gray-300 hover:text-white transition-colors group">
                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center mr-3 group-hover:bg-blue-500/20 group-hover:text-blue-400 transition-colors">
                  <FileText className="w-4 h-4" />
                </div>
                Договоры (PDF)
              </Link>
            </div>
          </div>
        </div>

        {/* Tasks List */}
        <div className="lg:col-span-3 space-y-4">
          <h2 className="text-xl font-bold text-white mb-4">В работе</h2>
          
          {tasks.filter(t => t.status === "in_progress").map(task => (
            <div key={task.id} className="bg-white/5 border border-white/10 p-6 rounded-2xl hover:bg-white/10 transition-colors flex flex-col md:flex-row gap-6 items-start md:items-center">
              
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md ${
                    task.role.includes("Пилот") 
                      ? "bg-purple-500/20 text-purple-400 border border-purple-500/30" 
                      : "bg-orange-500/20 text-orange-400 border border-orange-500/30"
                  }`}>
                    {task.role}
                  </span>
                  <span className="text-gray-500 text-sm flex items-center">
                    <Clock className="w-3.5 h-3.5 mr-1" />
                    {task.date}
                  </span>
                </div>
                
                <h3 className="text-xl font-bold text-white mb-2">{task.title}</h3>
                <p className="text-gray-400 text-sm flex items-center gap-2 mb-4">
                  <span>📍 {task.city}</span>
                  <span>•</span>
                  <span>ID Заказа: #{task.id}</span>
                </p>
                <div className="font-mono text-lg font-bold text-emerald-400">
                  {task.budget}
                </div>
              </div>

              <div className="w-full md:w-auto flex flex-col gap-2 shrink-0">
                <Link href="/dashboard/docs" className="w-full md:w-48 py-2.5 px-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-sm font-medium rounded-xl text-center transition-colors flex items-center justify-center">
                  <FileText className="w-4 h-4 mr-2 text-blue-400" />
                  Договор (PDF)
                </Link>
                
                {task.role.includes("Пилот") ? (
                  <Link href="/dashboard/orvd" className="w-full md:w-48 py-2.5 px-4 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-300 text-sm font-medium rounded-xl text-center transition-colors flex items-center justify-center">
                    <Navigation className="w-4 h-4 mr-2" />
                    План Полета
                  </Link>
                ) : (
                  <button className="w-full md:w-48 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-xl text-center transition-colors shadow-lg shadow-emerald-500/20">
                    Принять работу
                  </button>
                )}

                <Link href={`https://t.me/SkyRentAdminBot?start=contact_${task.employerId}`} target="_blank" className="w-full py-2 text-center text-sm text-gray-400 hover:text-white transition-colors flex items-center justify-center mt-1">
                  Связь в Telegram <ExternalLink className="w-3.5 h-3.5 ml-1" />
                </Link>
              </div>
            </div>
          ))}

          <h2 className="text-xl font-bold text-white mt-12 mb-4">Завершенные</h2>
          {tasks.filter(t => t.status === "completed").map(task => (
            <div key={task.id} className="bg-[#0A0A0B] border border-white/5 p-5 rounded-2xl flex flex-col md:flex-row gap-4 items-center opacity-70">
              <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-white line-clamp-1">{task.title}</h4>
                <p className="text-xs text-gray-500">{task.date} • {task.role}</p>
              </div>
              <div className="font-mono font-medium text-gray-400">
                {task.budget}
              </div>
              <button className="text-gray-500 hover:text-white p-2">
                <FileCheck className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
