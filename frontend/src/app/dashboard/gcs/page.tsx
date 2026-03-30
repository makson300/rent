"use client";

import {
  Smartphone, Radio, MapPin, Zap, Shield, ChevronRight,
  Wifi, Battery, Plane, Target, BarChart2, CheckCircle,
  ArrowRight, Play, Globe2, QrCode, Bell, Eye
} from "lucide-react";

// Ключевые фичи приложения
const FEATURES = [
  {
    icon: <Radio className="w-6 h-6 text-blue-400" />,
    title: "ОрВД прямо с пульта",
    desc: "Подача заявки на вылет в ЕС ОрВД одной кнопкой. Автоматическое закрытие зоны по посадке.",
  },
  {
    icon: <MapPin className="w-6 h-6 text-emerald-400" />,
    title: "Live NOTAM на карте",
    desc: "Отображение запретных зон, временных ограничений и предупреждений прямо на полётной карте.",
  },
  {
    icon: <Zap className="w-6 h-6 text-amber-400" />,
    title: "Автовыгрузка телеметрии",
    desc: "По посадке — лог немедленно уходит в Горизонт. Участие в Data Marketplace автоматическое.",
  },
  {
    icon: <Shield className="w-6 h-6 text-violet-400" />,
    title: "Квазар-ID интеграция",
    desc: "Трекер и приложение синхронизируются автоматически. Дрон всегда виден в ЕС ОрВД.",
  },
  {
    icon: <Target className="w-6 h-6 text-red-400" />,
    title: "Анти-Демпинг в реальном времени",
    desc: "Перед подачей заявки на тендер — мгновенный анализ рыночной цены и предупреждение о риске.",
  },
  {
    icon: <Bell className="w-6 h-6 text-cyan-400" />,
    title: "Push-уведомления МЧС",
    desc: "Если вы в резерве ПСО — немедленный Push с маршрутом до инцидента и NFZ override.",
  },
];

// Совместимые платформы управления
const COMPATIBLE = [
  { name: "DJI Pilot 2",       logo: "⚡", note: "Overlay SDK" },
  { name: "ArduPilot GCS",     logo: "🛠️", note: "MAVLink 2.0" },
  { name: "QGroundControl",    logo: "🎯", note: "MAVLink 2.0" },
  { name: "Autel Enterprise",  logo: "🤖", note: "Autel SDK" },
  { name: "Геоскан Planner",   logo: "🗺️", note: "REST API" },
];

export default function GCSMobilePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Smartphone className="w-3.5 h-3.5" /> Фаза 52 · GCS Мобайл
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Smartphone className="w-8 h-8 text-cyan-400" />
          Горизонт GCS — Ground Control Station
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Мобильное приложение для пультов, которое намертво интегрирует дрон с всей инфраструктурой платформы —
          от ОрВД до тендеров и дронопортов — прямо с поля.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-16">
        {/* Left: App mockup */}
        <div className="flex justify-center">
          <div className="relative">
            {/* Phone frame */}
            <div className="w-72 h-[580px] bg-[#0A0A0B] rounded-[42px] border-4 border-white/10 shadow-2xl shadow-cyan-500/10 overflow-hidden relative">
              {/* Status bar */}
              <div className="h-10 bg-[#050506] flex items-center justify-between px-6 text-[10px] text-gray-400">
                <span>9:41</span>
                <div className="flex items-center gap-1.5">
                  <Wifi className="w-3 h-3" />
                  <Battery className="w-4 h-3" />
                </div>
              </div>

              {/* App header */}
              <div className="bg-gradient-to-b from-[#090910] to-transparent px-4 pt-2 pb-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-white font-black text-lg">ГОРИЗОНТ GCS</div>
                  <div className="flex items-center gap-1 text-emerald-400 text-xs font-black">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    RTK LOCK
                  </div>
                </div>
              </div>

              {/* Map area (simulated) */}
              <div className="mx-3 h-48 rounded-2xl bg-[#0D1117] border border-white/5 relative overflow-hidden">
                {/* Grid lines */}
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="absolute w-full border-t border-white/[0.03]" style={{ top: `${i * 20}%` }} />
                ))}
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="absolute h-full border-l border-white/[0.03]" style={{ left: `${i * 20}%` }} />
                ))}
                {/* Drone position */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  <div className="w-4 h-4 rounded-full bg-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.7)]" />
                  <div className="w-16 h-16 rounded-full border border-blue-500/20 absolute -top-6 -left-6" />
                </div>
                {/* NFZ zone */}
                <div className="absolute top-4 right-4 w-20 h-20 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                  <span className="text-[8px] text-red-400 font-black text-center leading-tight">NOTAM<br />ЗОНА</span>
                </div>
                {/* Map labels */}
                <div className="absolute bottom-2 left-3 text-[8px] text-gray-600 font-mono">55.7558°N 37.6173°E</div>
              </div>

              {/* Telemetry strip */}
              <div className="mx-3 mt-2 grid grid-cols-4 gap-1">
                {[
                  { label: "АЛТ", val: "124", unit: "м", color: "text-blue-400" },
                  { label: "СКР", val: "38", unit: "км/ч", color: "text-cyan-400" },
                  { label: "ВОЗ", val: "7", unit: "м/с", color: "text-amber-400" },
                  { label: "БАТ", val: "76", unit: "%", color: "text-emerald-400" },
                ].map((t, i) => (
                  <div key={i} className="bg-white/[0.03] rounded-xl p-2 text-center">
                    <div className="text-[8px] text-gray-600">{t.label}</div>
                    <div className={`text-sm font-black ${t.color}`}>{t.val}</div>
                    <div className="text-[8px] text-gray-600">{t.unit}</div>
                  </div>
                ))}
              </div>

              {/* Action buttons */}
              <div className="mx-3 mt-3 space-y-2">
                <button className="w-full py-2.5 bg-blue-600/80 rounded-xl text-xs font-black text-white flex items-center justify-center gap-2">
                  <Radio className="w-3 h-3" /> Подать заявку в ОрВД
                </button>
                <div className="grid grid-cols-2 gap-2">
                  <button className="py-2 bg-emerald-600/60 rounded-xl text-[10px] font-black text-white">
                    📡 Квазар-ID
                  </button>
                  <button className="py-2 bg-amber-600/60 rounded-xl text-[10px] font-black text-white">
                    🏪 Тендеры
                  </button>
                </div>
              </div>

              {/* Bottom nav */}
              <div className="absolute bottom-0 left-0 right-0 h-16 bg-[#050506] border-t border-white/5 flex items-center justify-around px-2">
                {[
                  { icon: <MapPin className="w-5 h-5" />, label: "Карта",     active: true },
                  { icon: <BarChart2 className="w-5 h-5" />, label: "Данные", active: false },
                  { icon: <Plane className="w-5 h-5" />,   label: "Миссии",   active: false },
                  { icon: <Globe2 className="w-5 h-5" />,  label: "NOTAM",    active: false },
                ].map((n, i) => (
                  <div key={i} className={`flex flex-col items-center gap-0.5 ${n.active ? "text-cyan-400" : "text-gray-600"}`}>
                    {n.icon}
                    <span className="text-[8px] font-bold">{n.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Floating badges */}
            <div className="absolute -right-16 top-20 bg-emerald-500/15 border border-emerald-500/30 rounded-2xl px-3 py-2 text-xs text-emerald-400 font-black whitespace-nowrap">
              ✅ ОрВД одобрен
            </div>
            <div className="absolute -left-20 bottom-32 bg-amber-500/15 border border-amber-500/30 rounded-2xl px-3 py-2 text-xs text-amber-400 font-black whitespace-nowrap">
              💰 +$12 USDT
            </div>
          </div>
        </div>

        {/* Right: Features */}
        <div>
          <h2 className="font-black text-white text-2xl mb-6">Все возможности платформы — прямо в пульте</h2>
          <div className="space-y-4">
            {FEATURES.map((f, i) => (
              <div key={i} className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center justify-center shrink-0">
                  {f.icon}
                </div>
                <div>
                  <div className="font-black text-white text-sm mb-0.5">{f.title}</div>
                  <div className="text-xs text-gray-500">{f.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Compatible platforms */}
      <div className="mb-10">
        <h2 className="font-black text-white text-xl mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-400" /> Совместимые GCS-платформы
        </h2>
        <div className="flex flex-wrap gap-3">
          {COMPATIBLE.map(c => (
            <div key={c.name} className="flex items-center gap-2 bg-[#0A0A0B] border border-white/5 rounded-xl px-4 py-2.5">
              <span className="text-lg">{c.logo}</span>
              <div>
                <div className="text-sm font-black text-white">{c.name}</div>
                <div className="text-[10px] text-gray-500">{c.note}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Download CTA */}
      <div className="bg-gradient-to-r from-cyan-900/30 to-blue-900/20 border border-cyan-500/20 rounded-3xl p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <h3 className="font-black text-white text-2xl mb-3">Ранний доступ — Q2 2026</h3>
            <p className="text-gray-400 text-sm mb-5">
              Горизонт GCS сейчас в бета-тестировании. Первые 500 пилотов получают пожизненный бесплатный доступ
              и приоритетную поддержку от команды.
            </p>
            <div className="flex gap-3">
              <button className="flex items-center gap-2 px-5 py-3 bg-black border border-white/20 text-white font-black rounded-xl text-sm hover:border-white/40 transition-all">
                <span className="text-xl">🍎</span> App Store
              </button>
              <button className="flex items-center gap-2 px-5 py-3 bg-black border border-white/20 text-white font-black rounded-xl text-sm hover:border-white/40 transition-all">
                <span className="text-xl">🤖</span> Google Play
              </button>
            </div>
          </div>
          <div className="text-center">
            <div className="w-32 h-32 bg-white/5 border border-white/10 rounded-3xl mx-auto flex items-center justify-center mb-3">
              <QrCode className="w-16 h-16 text-cyan-400" />
            </div>
            <div className="text-xs text-gray-500">QR для скачивания TestFlight / APK</div>
          </div>
        </div>
      </div>
    </div>
  );
}
