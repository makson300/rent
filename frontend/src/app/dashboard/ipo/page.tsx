"use client";

import {
  TrendingUp, DollarSign, BarChart2, Globe2, Users, Shield,
  CheckCircle, Clock, Zap, Star, ChevronRight, Flag,
  Building2, Rocket, Crown, FileText
} from "lucide-react";

// Финансовая модель 2026-2029
const FINANCIAL_MODEL = [
  { year: "2026", arr_m: 1.2,  pilots: 4400,  companies: 180,  countries: 1, milestone: "Product-Market Fit (РФ)" },
  { year: "2027", arr_m: 6.8,  pilots: 18000, companies: 740,  countries: 4, milestone: "Экспансия СНГ (KZ, BY, UZ, AM)" },
  { year: "2028", arr_m: 28.4, pilots: 62000, companies: 2800, countries: 7, milestone: "Series A / IPO подготовка" },
  { year: "2029", arr_m: 95.0, pilots: 180000,companies: 9400, countries: 12,milestone: "IPO на Московской Бирже" },
];

// Блоки экосистемы
const ECOSYSTEM_BLOCKS = [
  { emoji: "🏪", title: "Маркетплейс аренды",    rev_pct: 18, color: "text-amber-400" },
  { emoji: "📋", title: "B2G/B2B Тендеры",       rev_pct: 31, color: "text-blue-400" },
  { emoji: "🏦", title: "Лизинг & Факторинг",    rev_pct: 14, color: "text-violet-400" },
  { emoji: "🏫", title: "Академия & Сертификаты",rev_pct: 12, color: "text-emerald-400" },
  { emoji: "📡", title: "Квазар-ID подписка",     rev_pct: 9,  color: "text-cyan-400" },
  { emoji: "🛬", title: "Дронопорты",             rev_pct: 8,  color: "text-indigo-400" },
  { emoji: "💾", title: "Data Marketplace",       rev_pct: 5,  color: "text-yellow-400" },
  { emoji: "🌐", title: "Горизонт.СНГ (роялти)",  rev_pct: 3,  color: "text-rose-400" },
];

// Конкурентное преимущество
const MOATS = [
  { title: "Единое Окно БАС", desc: "Единственная платформа в РФ, объединяющая ОрВД-интеграцию, тендеры, реестр и IoT в одном продукте." },
  { title: "Network Effect", desc: "Каждый новый пилот увеличивает ценность для заказчиков B2G. Виральный рост через реестр МЧС." },
  { title: "Данные как барьер", desc: "150 000+ часов верифицированной телеметрии — уникальный датасет для обучения AutoPilot-систем." },
  { title: "Госсвязи & Регуляторика", desc: "Интеграция с Росавиацией, МЧС, ФАП-69. Создание нового регулятора требует лет — мы уже внутри." },
];

// Инвест-раунды
const ROUNDS = [
  { round: "Seed",    amount: "$1.5M",  valuation: "$7M",   status: "closed",   date: "Q4 2025", investors: "Ангелы (авиа-отрасль)" },
  { round: "Pre-A",   amount: "$5M",    valuation: "$28M",  status: "open",     date: "Q2 2026", investors: "Венчур / Стратеги" },
  { round: "Series A",amount: "$18M",   valuation: "$95M",  status: "future",   date: "Q4 2027", investors: "VC + Госфонды (РВК/АСИ)" },
  { round: "IPO",     amount: "$50M+",  valuation: "$400M+",status: "future",   date: "Q3 2029", investors: "Мосбиржа / Инвесторы СНГ" },
];

const ROUND_STATUS = {
  closed: { label: "Закрыт",  cls: "bg-gray-500/10 text-gray-400 border-gray-500/20" },
  open:   { label: "Открыт",  cls: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 animate-pulse" },
  future: { label: "Планируется", cls: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
};

export default function IPOPage() {
  const maxARR = Math.max(...FINANCIAL_MODEL.map(y => y.arr_m));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-10">
        <span className="px-3 py-1 rounded-full bg-rose-500/15 text-rose-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Crown className="w-3.5 h-3.5" /> Фаза 53 · Инвестиционный Дашборд
        </span>
        <h1 className="text-5xl font-extrabold text-white mb-4 flex items-center gap-4">
          <Rocket className="w-10 h-10 text-rose-400" />
          Горизонт — IPO 2029
        </h1>
        <p className="text-gray-400 max-w-3xl text-lg">
          Первый и единственный вертикально-интегрированный<br />
          <span className="text-white font-black">инфраструктурный монополист рынка БПЛА в РФ и СНГ.</span>
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10">
        {[
          { label: "TAM (РФ + СНГ, 2029)", val: "$840M",      icon: <Globe2 className="w-5 h-5 text-blue-400" />,    bg: "border-blue-500/15" },
          { label: "ARR (Run Rate 2026)",  val: "$1.2M",      icon: <TrendingUp className="w-5 h-5 text-emerald-400" />, bg: "border-emerald-500/15" },
          { label: "Пилотов на платформе",val: "4 400+",      icon: <Users className="w-5 h-5 text-violet-400" />, bg: "border-violet-500/15" },
          { label: "Целевая оценка IPO",   val: "$400M",      icon: <Crown className="w-5 h-5 text-amber-400" />,    bg: "border-amber-500/15" },
        ].map((m, i) => (
          <div key={i} className={`bg-[#0A0A0B] border ${m.bg} rounded-2xl p-5`}>
            <div className="flex items-center gap-2 mb-2">{m.icon}<div className="text-xs text-gray-500">{m.label}</div></div>
            <div className="text-3xl font-black text-white">{m.val}</div>
          </div>
        ))}
      </div>

      {/* Revenue Growth Chart */}
      <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl p-6 mb-8">
        <h2 className="font-black text-white text-xl mb-6 flex items-center gap-2">
          <BarChart2 className="w-5 h-5 text-rose-400" /> Прогноз ARR 2026–2029
        </h2>
        <div className="flex items-end gap-4 h-48">
          {FINANCIAL_MODEL.map((y, i) => {
            const height = (y.arr_m / maxARR) * 100;
            return (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div className="text-sm font-black text-white">${y.arr_m}M</div>
                <div className="w-full flex items-end justify-center" style={{ height: "140px" }}>
                  <div
                    className="w-full rounded-t-xl bg-gradient-to-t from-rose-600 to-rose-400 transition-all duration-1000"
                    style={{ height: `${height}%` }}
                  />
                </div>
                <div className="text-xs font-black text-gray-400">{y.year}</div>
                <div className="text-[10px] text-gray-600 text-center leading-tight">{y.milestone}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Revenue Breakdown */}
        <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl p-6">
          <h2 className="font-black text-white text-xl mb-5 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-amber-400" /> Источники Revenue
          </h2>
          <div className="space-y-3">
            {ECOSYSTEM_BLOCKS.map((b, i) => (
              <div key={i}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="flex items-center gap-2 text-gray-300">
                    <span>{b.emoji}</span> {b.title}
                  </span>
                  <span className={`font-black ${b.color}`}>{b.rev_pct}%</span>
                </div>
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r ${b.color.replace("text-", "from-")} to-transparent`}
                    style={{ width: `${b.rev_pct * 3}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Competitive Moats */}
        <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl p-6">
          <h2 className="font-black text-white text-xl mb-5 flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-400" /> Конкурентный Ров
          </h2>
          <div className="space-y-4">
            {MOATS.map((m, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0 mt-0.5">
                  <CheckCircle className="w-4 h-4 text-blue-400" />
                </div>
                <div>
                  <div className="font-black text-white text-sm">{m.title}</div>
                  <div className="text-xs text-gray-500 mt-0.5 leading-relaxed">{m.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Investment Rounds */}
      <div className="mb-8">
        <h2 className="font-black text-white text-xl mb-5 flex items-center gap-2">
          <Building2 className="w-5 h-5 text-violet-400" /> Инвестиционные Раунды
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {ROUNDS.map((r, i) => {
            const st = ROUND_STATUS[r.status as keyof typeof ROUND_STATUS];
            return (
              <div key={i} className={`bg-[#0A0A0B] border rounded-2xl p-5 ${r.status === "open" ? "border-emerald-500/25" : "border-white/5"}`}>
                <div className="flex items-center justify-between mb-3">
                  <div className="font-black text-white text-lg">{r.round}</div>
                  <span className={`text-[10px] font-black px-2 py-0.5 rounded border ${st.cls}`}>{st.label}</span>
                </div>
                <div className="text-2xl font-black text-white mb-0.5">{r.amount}</div>
                <div className="text-xs text-gray-500 mb-3">Оценка: {r.valuation}</div>
                <div className="flex items-center gap-1.5 text-[10px] text-gray-500">
                  <Clock className="w-3 h-3" /> {r.date}
                </div>
                <div className="text-[10px] text-gray-600 mt-1">{r.investors}</div>
                {r.status === "open" && (
                  <button className="w-full mt-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black rounded-lg transition-all">
                    Запросить Тизер
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* IPO Vision */}
      <div className="bg-gradient-to-br from-rose-900/30 via-[#0A0A0B] to-blue-900/20 border border-rose-500/20 rounded-3xl p-10 text-center">
        <Crown className="w-16 h-16 text-rose-400 mx-auto mb-4" />
        <h2 className="font-black text-white text-3xl mb-4">IPO — Мосбиржа, Q3 2029</h2>
        <p className="text-gray-400 max-w-2xl mx-auto mb-6 text-sm leading-relaxed">
          Горизонт становится публичной компанией как монопольный оператор цифровой инфраструктуры
          беспилотной авиации в РФ и СНГ — первая технологическая IPO в отрасли БПЛА.
          <br /><br />
          Целевая оценка <span className="text-rose-400 font-black">$400M+</span> при ARR{" "}
          <span className="text-emerald-400 font-black">$95M</span>.
          Мультипликатор P/S = 4.2x (дисконт к западным аналогам).
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <button className="flex items-center gap-2 px-6 py-3 bg-rose-600 hover:bg-rose-500 text-white font-black rounded-xl text-sm transition-all">
            <FileText className="w-4 h-4" /> Инвest-Меморандум
          </button>
          <button className="flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 font-black rounded-xl text-sm transition-all">
            <BarChart2 className="w-4 h-4" /> Финансовая Модель (Excel)
          </button>
        </div>
      </div>
    </div>
  );
}
