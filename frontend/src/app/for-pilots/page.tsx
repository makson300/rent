"use client";

import {
  Box, MapPin, Briefcase, FileCheck, ShieldCheck, Heart,
  ArrowRight, BookOpen, Banknote, Rocket, Lightbulb,
  GraduationCap, Smartphone, Coins, Satellite, Trophy,
  TrendingUp, Zap, Globe2
} from "lucide-react";
import Link from "next/link";

// Ценностные предложения
const VALUE_PROPS = [
  {
    icon: <Briefcase className="w-7 h-7 text-amber-400" />,
    iconBg: "bg-amber-400/10",
    border: "hover:border-amber-400/30",
    title: "Заказы B2B и B2G",
    desc: "Доступ к закрытому Радару тендеров. Система сама рассчитает, хватит ли вашему дрону батареи для выполнения контракта.",
  },
  {
    icon: <MapPin className="w-7 h-7 text-blue-400" />,
    iconBg: "bg-blue-500/10",
    border: "hover:border-blue-500/30",
    title: "ОрВД в 2 клика",
    desc: "Встроенный генератор формализованной заявки (ТШС) для Росавиации. Скопировал, отправил, получил разрешение на ИВП.",
  },
  {
    icon: <ShieldCheck className="w-7 h-7 text-emerald-400" />,
    iconBg: "bg-emerald-500/10",
    border: "hover:border-emerald-500/30",
    title: "Льготное КАСКО",
    desc: "Страхуем даже самосборы. Оценка состояния по лог-файлам (TXT). Юридический щит от претензий третьих лиц.",
  },
  {
    icon: <Heart className="w-7 h-7 text-red-400" />,
    iconBg: "bg-red-500/10",
    border: "hover:border-red-500/30",
    title: "Резерв МЧС (ПСО)",
    desc: "Статус добровольца — при ЧС штаб выдаёт бесплатный зелёный коридор на полёты в любой зоне без задержки.",
  },
  {
    icon: <GraduationCap className="w-7 h-7 text-violet-400" />,
    iconBg: "bg-violet-500/10",
    border: "hover:border-violet-500/30",
    title: "Академия Горизонт",
    desc: "ФАП-69, B2G тендеры, инспекция инфраструктуры. Курсы с сертификатами Минтранс. Обучение за 2–6 недель онлайн.",
    link: "/dashboard/academy",
  },
  {
    icon: <Coins className="w-7 h-7 text-yellow-400" />,
    iconBg: "bg-yellow-500/10",
    border: "hover:border-yellow-500/30",
    title: "Data Marketplace",
    desc: "Продавайте аэрофотосъёмку Яндексу, агрокомпаниям и МЧС. Автоматический пассивный доход с каждого полёта в USDT.",
    link: "/dashboard/data-market",
  },
  {
    icon: <Satellite className="w-7 h-7 text-cyan-400" />,
    iconBg: "bg-cyan-500/10",
    border: "hover:border-cyan-500/30",
    title: "Квазар-ID Трекер",
    desc: "IoT-трекер обязательной регистрации в ЕС ОрВД (ФАП-69). Видимость в диспетчерской, защита при инцидентах.",
    link: "/dashboard/tracker",
  },
  {
    icon: <FileCheck className="w-7 h-7 text-purple-400" />,
    iconBg: "bg-purple-500/10",
    border: "hover:border-purple-500/30",
    title: "Единый Реестр Лицензий",
    desc: "Все сертификаты внешнего пилота в одном профиле. Верификация через Минтранс. Траст-фактор виден заказчикам B2B.",
    isWide: true,
  },
];

// Ключевые цифры экосистемы
const STATS = [
  { val: "4 400+",  label: "Верифицированных пилотов" },
  { val: "180+",    label: "B2G тендеров в месяц" },
  { val: "38",      label: "Регионов присутствия" },
  { val: "$840M",   label: "TAM рынка РФ+СНГ (2029)" },
];

export default function ForPilotsPage() {
  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white">

      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <div className="relative pt-32 pb-20 px-4 overflow-hidden border-b border-white/5">
        {/* Ambient glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-amber-500/5 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-5xl mx-auto relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/20 text-sm font-bold text-amber-400 mb-8 uppercase tracking-widest">
            <ShieldCheck className="w-4 h-4" /> Единое Окно Пилота БАС
          </div>
          <h1 className="text-5xl md:text-7xl font-black mb-6 tracking-tight">
            Зарабатывай. Летай.{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-yellow-500">
              Легально.
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Горизонт — первая платформа, которая объединяет B2G-тендеры,
            регистрацию в ОрВД, IoT-трекер, академию и Data Marketplace
            в одном личном кабинете пилота.
          </p>

          {/* Stats row */}
          <div className="flex flex-wrap justify-center gap-8 mb-12">
            {STATS.map((s, i) => (
              <div key={i} className="text-center">
                <div className="text-3xl font-black text-white">{s.val}</div>
                <div className="text-xs text-gray-500 mt-0.5">{s.label}</div>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/login"
              className="px-8 py-4 bg-amber-500 hover:bg-amber-400 text-black font-black uppercase tracking-wider rounded-xl transition-all shadow-[0_0_30px_rgba(245,158,11,0.25)] flex items-center gap-2"
            >
              Регистрация через ЕСИА <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 bg-[#1A1A1D] hover:bg-[#252529] border border-white/10 text-white font-bold rounded-xl transition-all shadow-lg"
            >
              Вход через VK ID
            </Link>
          </div>
        </div>
      </div>

      {/* ── Value Props ─────────────────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-4 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-black mb-4">
            Почему пилоты выбирают{" "}
            <span className="text-amber-400">Горизонт</span>?
          </h2>
          <p className="text-gray-400 text-lg">
            Мы сняли бюрократию — вы фокусируетесь на полётах.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {VALUE_PROPS.map((v, i) => (
            <div
              key={i}
              className={`bg-[#121214] border border-white/5 ${v.border} transition-colors rounded-3xl p-8 group ${v.isWide ? "lg:col-span-2" : ""}`}
            >
              <div className={`w-14 h-14 ${v.iconBg} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                {v.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{v.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed mb-4">{v.desc}</p>
              {v.link && (
                <Link
                  href={v.link}
                  className="inline-flex items-center gap-1 text-xs font-bold text-amber-400 hover:text-amber-300 transition-colors"
                >
                  Открыть <ArrowRight className="w-3 h-3" />
                </Link>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ── GCS Мобайл промо ────────────────────────────────────────────── */}
      <div className="border-t border-white/5 bg-gradient-to-br from-[#0D0D12] to-cyan-900/10 py-24 px-4">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-16">
          {/* Phone mockup */}
          <div className="shrink-0 relative">
            <div className="w-56 h-[430px] bg-[#0A0A0B] rounded-[36px] border-4 border-white/10 shadow-2xl shadow-cyan-500/10 overflow-hidden">
              <div className="h-8 bg-black flex items-center justify-between px-5 text-[9px] text-gray-500">
                <span>9:41</span><span>●●●</span>
              </div>
              <div className="px-3 pt-2">
                <div className="text-white font-black text-sm mb-2">ГОРИЗОНТ GCS</div>
                <div className="h-32 rounded-xl bg-[#0D1117] border border-white/5 flex items-center justify-center relative overflow-hidden mb-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.7)]" />
                  <div className="absolute text-[7px] text-gray-700 bottom-1 left-2 font-mono">55.7558°N</div>
                </div>
                <div className="grid grid-cols-4 gap-1 mb-2">
                  {[["АЛТ","124м"],["СКР","38"],["ВОЗ","7"],["БАТ","76%"]].map(([l,v],i)=>(
                    <div key={i} className="bg-white/5 rounded-lg p-1 text-center">
                      <div className="text-[6px] text-gray-600">{l}</div>
                      <div className="text-[9px] font-black text-cyan-400">{v}</div>
                    </div>
                  ))}
                </div>
                <div className="w-full py-2 bg-blue-600/70 rounded-lg text-[9px] font-black text-white text-center">
                  📡 Подать в ОрВД
                </div>
              </div>
            </div>
            <div className="absolute -right-12 top-16 bg-emerald-500/15 border border-emerald-500/30 rounded-xl px-2 py-1 text-[10px] text-emerald-400 font-black whitespace-nowrap">
              ✅ ОрВД одобрен
            </div>
            <div className="absolute -left-14 bottom-20 bg-amber-500/15 border border-amber-500/30 rounded-xl px-2 py-1 text-[10px] text-amber-400 font-black whitespace-nowrap">
              💰 +$12 USDT
            </div>
          </div>

          {/* Text */}
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs font-bold text-cyan-400 mb-5 uppercase tracking-widest">
              <Smartphone className="w-3.5 h-3.5" /> Горизонт GCS — Q2 2026
            </div>
            <h2 className="text-3xl md:text-5xl font-black mb-5">
              Весь дашборд прямо{" "}
              <span className="text-cyan-400">в пульте</span>
            </h2>
            <p className="text-gray-400 text-lg mb-8 leading-relaxed max-w-xl">
              Мобильное приложение, которое намертво интегрирует дрон с платформой —
              подача в ОрВД, привязка Квазар-ID трекера, автоматическая выгрузка
              телеметрии в Data Marketplace, участие в тендерах — всё прямо с поля.
            </p>
            <div className="flex flex-wrap gap-3 mb-6">
              {["MAVLink 2.0","DJI Pilot 2","ArduPilot GCS","Геоскан Planner"].map(p => (
                <span key={p} className="text-xs px-3 py-1 bg-white/5 border border-white/10 rounded-xl text-gray-400">{p}</span>
              ))}
            </div>
            <Link
              href="/dashboard/gcs"
              className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-600 hover:bg-cyan-500 text-white font-black rounded-xl transition-all shadow-[0_0_20px_rgba(6,182,212,0.2)]"
            >
              <Smartphone className="w-4 h-4" /> Ранний доступ — TestFlight
            </Link>
          </div>
        </div>
      </div>

      {/* ── Лидерборд & Трофеи ─────────────────────────────────────────── */}
      <div className="border-t border-white/5 bg-[#0A0A0B] py-24 px-4">
        <div className="max-w-7xl mx-auto text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs font-bold text-amber-400 mb-5 uppercase tracking-widest">
            <Trophy className="w-3.5 h-3.5" /> Рейтинг пилотов
          </div>
          <h2 className="text-3xl md:text-5xl font-black mb-4">
            Траст-Фактор — ваша{" "}
            <span className="text-amber-400">репутация на рынке</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Выполняйте тендеры, загружайте логи полётов и проходите сертификацию —
            Траст-Фактор растёт автоматически. Высокий TF открывает B2G-тендеры
            Росавиации и МЧС.
          </p>
        </div>

        {/* Подиум мок */}
        <div className="max-w-2xl mx-auto flex items-end justify-center gap-4 mb-8">
          {[
            { pos: 2, name: "А. Волков",   tf: 94, h: "h-28", bg: "bg-gray-400/20", medal: "🥈" },
            { pos: 1, name: "М. Петров",   tf: 99, h: "h-40", bg: "bg-amber-400/20 border-amber-500/30", medal: "🥇" },
            { pos: 3, name: "В. Сорокин",  tf: 89, h: "h-20", bg: "bg-amber-700/20", medal: "🥉" },
          ].map(p => (
            <div key={p.pos} className="flex-1 text-center">
              <div className="text-2xl mb-1">{p.medal}</div>
              <div className="text-sm font-black text-white mb-1">{p.name}</div>
              <div className="text-xs text-gray-500 mb-2">TF {p.tf}</div>
              <div className={`${p.h} ${p.bg} border border-white/10 rounded-t-2xl flex items-center justify-center`}>
                <span className="text-xl font-black text-gray-500">#{p.pos}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Link
            href="/dashboard/leaderboard"
            className="inline-flex items-center gap-2 px-6 py-3 bg-amber-600/80 hover:bg-amber-500 text-white font-black rounded-xl transition-all"
          >
            <Trophy className="w-4 h-4" /> Моё место в рейтинге
          </Link>
        </div>
      </div>

      {/* ── Субсидии + Правовой архив ────────────────────────────────────── */}
      <div className="border-t border-white/5 py-24 px-4 bg-[#0D0D12]">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-gradient-to-br from-[#121214] to-[#1A1A1D] border border-white/10 rounded-[2rem] p-10 relative overflow-hidden group">
            <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center mb-8 border border-emerald-500/20">
              <Banknote className="w-8 h-8 text-emerald-400" />
            </div>
            <h3 className="text-3xl font-black text-white mb-4">Государственные <span className="text-emerald-400">Субсидии</span></h3>
            <p className="text-gray-400 mb-8 leading-relaxed">
              Дотации Минпромторга на закупку отечественных БПЛА и компенсацию части затрат
              на сертификацию инженеров. Автоматический подбор подходящих программ.
            </p>
            <button className="flex items-center gap-2 text-emerald-400 font-bold hover:text-emerald-300 transition-colors">
              Открыть базу программ поддержки <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>

          <div className="bg-gradient-to-br from-[#121214] to-[#1A1A1D] border border-white/10 rounded-[2rem] p-10 relative overflow-hidden group">
            <div className="w-16 h-16 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-8 border border-purple-500/20">
              <BookOpen className="w-8 h-8 text-purple-400" />
            </div>
            <h3 className="text-3xl font-black text-white mb-4">Правовой <span className="text-purple-400">Архив</span></h3>
            <p className="text-gray-400 mb-8 leading-relaxed">
              Актуальный Воздушный Кодекс, ФАП-69, постановления о зонировании (ЭПР) и правила
              регистрации БАС. ИИ-парсер ежедневно обновляет базу.
            </p>
            <button className="flex items-center gap-2 text-purple-400 font-bold hover:text-purple-300 transition-colors">
              Изучить нормативную базу <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>
      </div>

      {/* ── Стартап-хаб ────────────────────────────────────────────────── */}
      <div className="border-t border-white/5 bg-[#0A0A0B] py-24 px-4 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/5 rounded-full blur-[150px] pointer-events-none" />
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-bold text-blue-400 mb-4 uppercase tracking-widest">
                <Rocket className="w-4 h-4" /> Хаб Инженеров
              </div>
              <h2 className="text-3xl md:text-5xl font-black mb-4">
                Витрина <span className="text-blue-500">Стартапов</span>
              </h2>
              <p className="text-gray-400 text-lg max-w-2xl">
                Горизонт поддерживает конструкторов и инженеров. Связываем прорывные
                идеи с инвесторами и государственными фондами (РВК, АСИ, Сколково).
              </p>
            </div>
            <button className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] flex items-center gap-2 shrink-0">
              <Lightbulb className="w-5 h-5" /> Предложить Идею
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                tag: "Ищем Инвестиции", tagColor: "text-amber-400 bg-amber-400/10",
                title: "SkyNet Agro T-X",
                desc: "Тяжёлый агродрон с нагрузкой 60кг, локализация 90% в РФ.",
                stage: "Pre-Seed · $1.5M"
              },
              {
                tag: "Грант Получен", tagColor: "text-emerald-400 bg-emerald-400/10",
                title: "Horizon Link Pro",
                desc: "Защищённый цифровой видеолинк, невосприимчивый к РЭБ-помехам.",
                stage: "Seed · РВК ✓"
              },
              {
                tag: "Патент Подан", tagColor: "text-violet-400 bg-violet-400/10",
                title: "АвтоДронIT-X1",
                desc: "Автономная система доставки по BVLOS для маркетплейсов Wildberries.",
                stage: "Pre-A · $5M"
              },
            ].map((s, i) => (
              <div key={i} className="bg-[#15151A] border border-white/5 rounded-3xl p-6 hover:border-white/15 transition-all group">
                <div className="h-36 bg-zinc-900 rounded-2xl mb-5 flex items-center justify-center border border-white/5">
                  <TrendingUp className="w-12 h-12 text-gray-700" />
                </div>
                <div className={`text-xs font-black px-2 py-1 rounded w-max mb-3 uppercase tracking-wide ${s.tagColor}`}>
                  {s.tag}
                </div>
                <h3 className="text-lg font-bold mb-1 text-white group-hover:text-blue-400 transition-colors">{s.title}</h3>
                <p className="text-sm text-gray-400 mb-3">{s.desc}</p>
                <div className="text-xs text-gray-600 font-mono">{s.stage}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── CTA ─────────────────────────────────────────────────────────── */}
      <div className="border-t border-white/5 bg-gradient-to-br from-[#0D0D0F] to-amber-900/10 py-20 text-center px-4">
        <Zap className="w-12 h-12 text-amber-400 mx-auto mb-6" />
        <h2 className="text-4xl font-black mb-4">Готовы стать частью Авиации Будущего?</h2>
        <p className="text-gray-400 mb-8 max-w-xl mx-auto">
          Первые 500 пилотов получают пожизненный Pro доступ к Академии, приоритет в B2G-тендерах и раннее место в рейтинге.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/login"
            className="px-8 py-4 bg-amber-500 hover:bg-amber-400 text-black font-black uppercase tracking-wider rounded-xl transition-all shadow-[0_0_30px_rgba(245,158,11,0.2)]"
          >
            Зарегистрировать Дрон
          </Link>
          <Link
            href="/dashboard/ipo"
            className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-black rounded-xl transition-all"
          >
            <Globe2 className="w-4 h-4 inline mr-2" />
            IPO Dashboard 2029
          </Link>
        </div>
      </div>

    </div>
  );
}
