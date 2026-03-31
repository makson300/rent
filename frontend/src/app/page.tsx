"use client";

import Link from "next/link";
import BenefitsCarousel from "@/components/Carousel";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

// Ключевые модули экосистемы — линкуются на реальные страницы
const MODULES = [
  { icon: "🛒", label: "Маркетплейс",   href: "/catalog",                   desc: "Аренда техники B2B/B2C" },
  { icon: "📋", label: "Тендеры B2G",    href: "/dashboard/tenders",         desc: "Госзакупки и конкурсы" },
  { icon: "📡", label: "Квазар-ID",      href: "/dashboard/tracker",         desc: "IoT трекеры в ЕС ОрВД" },
  { icon: "🎓", label: "Академия",       href: "/dashboard/academy",         desc: "ФАП-69, ОрВД, SORA" },
  { icon: "🗺️", label: "Дронопорты",    href: "/dashboard/droneports",      desc: "Бронирование слотов" },
  { icon: "💾", label: "Data Market",   href: "/dashboard/data-market",     desc: "БПЛА датасеты LIDAR" },
  { icon: "⚖️", label: "Патенты ФИПС",  href: "/dashboard/patents",         desc: "Онлайн-подача в ФИПС" },
  { icon: "🏭", label: "Лизинг",        href: "/dashboard/leasing",         desc: "Финансирование дронов" },
  { icon: "📊", label: "Арбитраж",      href: "/dashboard/radar",           desc: "AI-радар тендеров" },
  { icon: "🚨", label: "МЧС Резерв",    href: "/for-pilots",                desc: "Добровольный реестр ПСО" },
  { icon: "🏢", label: "Для бизнеса",   href: "/franchise",              desc: "Корпоративная программа" },
  { icon: "🤝", label: "Франшиза",      href: "/franchise",                 desc: "Горизонт в вашем регионе" },
];

// Статика платформы — в продакшне подгружать из /api/v1/public/stats
const STATS = [
  { label: "Операторов", val: "2 400+", sub: "из 73 регионов" },
  { label: "Тендеров B2G", val: "840+", sub: "с НМЦК > 500 тыс." },
  { label: "Дронов в ЕС ОрВД", val: "1 200", sub: "Квазар-ID трекеры" },
  { label: "Выдано сертификатов", val: "360", sub: "Академия Горизонт" },
];

export default function Home() {
  const ref = useRef(null);

  return (
    <div ref={ref} className="relative overflow-hidden bg-[#050505] min-h-screen">

      {/* Parallax Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-khokhloma-red rounded-full mix-blend-screen filter blur-[150px] opacity-10 animate-blob" />
        <div className="absolute top-0 -right-4 w-72 h-72 bg-khokhloma-gold rounded-full mix-blend-screen filter blur-[150px] opacity-10 animate-blob animation-delay-2000" />
        <div className="absolute inset-0 bg-pattern-khokhloma opacity-5 z-0" />
      </div>

      {/* Hero */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-8">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center"
        >
          <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-khokhloma-gold/10 border border-khokhloma-gold/20 text-khokhloma-gold text-xs font-bold uppercase tracking-widest mb-6">
            🇷🇺 Национальная экосистема БАС · 20 фаз развития
          </span>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 uppercase">
            <span className="block text-white">Национальная Экосистема</span>
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-khokhloma-gold to-khokhloma-red drop-shadow-lg">
              Инфраструктуры БАС
            </span>
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-400 leading-relaxed font-light">
            Единая государственная платформа «Горизонт»: маркетплейс, биржа B2G тендеров, IoT-трекеры ОрВД,
            Академия, Data Marketplace, патентование и лизинг дронов в одном окне.
          </p>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="mt-12 flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Link href="/catalog"
              className="w-full sm:w-auto text-center px-10 py-4 text-lg font-bold rounded-xl text-black bg-gradient-to-r from-khokhloma-gold via-yellow-400 to-khokhloma-gold shadow-[0_0_30px_rgba(245,176,65,0.4)] hover:shadow-[0_0_50px_rgba(245,176,65,0.6)] transition-all hover:-translate-y-1">
              Перейти к сервисам
            </Link>
            <Link href="/for-pilots"
              className="w-full sm:w-auto text-center px-8 py-4 border border-white/10 text-lg font-medium rounded-xl text-white bg-white/5 hover:bg-white/10 backdrop-blur-md transition-all hover:-translate-y-1">
              Для пилотов →
            </Link>
            <Link href="/franchise"
              className="w-full sm:w-auto text-center px-8 py-4 border border-white/10 text-lg font-medium rounded-xl text-white bg-white/5 hover:bg-white/10 backdrop-blur-md transition-all hover:-translate-y-1">
              Для бизнеса →
            </Link>
          </motion.div>
        </motion.div>

        {/* Platform Stats */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {STATS.map((s, i) => (
            <div key={i} className="bg-white/[0.03] border border-white/5 rounded-2xl p-5 text-center hover:border-khokhloma-gold/20 transition-all">
              <div className="text-3xl font-black text-khokhloma-gold">{s.val}</div>
              <div className="text-sm font-bold text-white mt-1">{s.label}</div>
              <div className="text-xs text-gray-500 mt-0.5">{s.sub}</div>
            </div>
          ))}
        </motion.div>

        {/* Modules Grid */}
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="mt-16"
        >
          <h2 className="text-center text-2xl font-black text-white mb-8">
            Все модули экосистемы
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {MODULES.map((m, i) => (
              <Link
                key={i}
                href={m.href}
                className="group bg-white/[0.02] border border-white/5 rounded-2xl p-4 text-center hover:bg-white/[0.06] hover:border-khokhloma-gold/30 transition-all hover:-translate-y-1"
              >
                <div className="text-3xl mb-2">{m.icon}</div>
                <div className="text-xs font-black text-white group-hover:text-khokhloma-gold transition-colors">{m.label}</div>
                <div className="text-[10px] text-gray-600 mt-0.5 hidden sm:block">{m.desc}</div>
              </Link>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Carousel */}
      <motion.div
        initial={{ opacity: 0, y: 100 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.7 }}
        className="relative z-20 mt-8"
      >
        <BenefitsCarousel />
      </motion.div>

    </div>
  );
}
