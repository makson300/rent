"use client";

import {
  Globe2, TrendingUp, Building2, FileText, ChevronRight,
  CheckCircle, Clock, MapPin, Zap, Users, Shield, DollarSign,
  BarChart2, Plane, Flag, Star
} from "lucide-react";

// Целевые рынки
const MARKETS = [
  {
    country: "Казахстан",
    flag: "🇰🇿",
    code: "KZ",
    status: "active",
    pilot_count: 312,
    tender_platform: "Закупки.kz",
    regulator: "КГА РК (Комитет гражданской авиации)",
    key_sectors: ["Агро", "Горнодобывающая", "Нефтегаз (Тенгиз)", "Картография"],
    challenge: "Интеграция с платёжной системой Kaspi.kz",
    revenue_est_usd: "4.2M",
    active_tenders: 18,
    launch_q: "Q1 2026 ✅ ЗАПУЩЕНО",
    color: "border-blue-500/20 bg-blue-500/5",
    badge: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  },
  {
    country: "Беларусь",
    flag: "🇧🇾",
    code: "BY",
    status: "preparation",
    pilot_count: 94,
    tender_platform: "icetrade.by",
    regulator: "Государственная инспекция по авиации РБ",
    key_sectors: ["Сельское хозяйство", "Лесное хозяйство", "Промышленные зоны"],
    challenge: "Таможенный союз — нет барьеров, но нужна локализация",
    revenue_est_usd: "1.8M",
    active_tenders: 5,
    launch_q: "Q3 2026",
    color: "border-amber-500/15 bg-amber-500/5",
    badge: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  },
  {
    country: "Узбекистан",
    flag: "🇺🇿",
    code: "UZ",
    status: "research",
    pilot_count: 0,
    tender_platform: "(G2B Ресурс)",
    regulator: "Государственная инспекция по надзору РУ",
    key_sectors: ["Хлопковые поля", "Туризм", "Строительство Ташкента"],
    challenge: "Правовая база БПЛА формируется — возможность первого игрока",
    revenue_est_usd: "3.1M",
    active_tenders: 0,
    launch_q: "Q1 2027",
    color: "border-emerald-500/15 bg-emerald-500/5",
    badge: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  },
];

const STATUS_MAP: Record<string, { label: string; dot: string }> = {
  active:      { label: "Запущено",    dot: "bg-emerald-400 animate-pulse" },
  preparation: { label: "Подготовка",  dot: "bg-amber-400" },
  research:    { label: "Аналитика",   dot: "bg-blue-400" },
};

// Роадмап экспансии
const ROADMAP = [
  { q: "Q4 2025", title: "Анализ рынков СНГ",          done: true,  items: ["Правовое исследование (Казахстан, Беларусь, Узбекистан, Армения)", "Партнёрские переговоры"] },
  { q: "Q1 2026", title: "Горизонт.KZ — Казахстан",    done: true,  items: ["Интеграция Закупки.kz API", "Локализация (казахский язык)", "150+ пилотов онбординг"] },
  { q: "Q3 2026", title: "Горизонт.BY — Беларусь",     done: false, items: ["Интеграция icetrade.by", "Партнёрство с ДОСААФ РБ", "Регистрация ЮЛ в Минске"] },
  { q: "Q1 2027", title: "Горизонт.UZ — Узбекистан",   done: false, items: ["Лобби авиарегулятора", "Программа агро-пилотов (500 фермеров)", "Офис в Ташкенте"] },
  { q: "Q3 2027", title: "Горизонт.AM/AZ — Кавказ",    done: false, items: ["Армения (яблочные сады)", "Азербайджан (нефтяные поля SOCAR)", "Мультивалютный кошелёк"] },
];

// Для инвесторов
const INVESTOR_METRICS = [
  { label: "TAM СНГ (рынок БПЛА)",    val: "$840M",  sub: "к 2028 году" },
  { label: "SAM (коммерческие услуги)", val: "$210M",  sub: "В2В + В2G" },
  { label: "Текущий рост MoM",         val: "+18%",   sub: "пилотов на платформе" },
  { label: "Revenue Run Rate",         val: "$1.2M",  sub: "ARR 2026" },
];

export default function SNGPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Globe2 className="w-3.5 h-3.5" /> Фаза 50 · Экспансия
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Flag className="w-8 h-8 text-emerald-400" />
          Горизонт.СНГ — Региональная Экспансия
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Выход на рынки Казахстана, Беларуси и Узбекистана. Интеграция тендерных систем,
          локализация платформы и создание сети сертифицированных пилотов в СНГ.
        </p>
      </div>

      {/* Investor Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        {INVESTOR_METRICS.map((m, i) => (
          <div key={i} className="bg-gradient-to-br from-[#0E0E10] to-emerald-900/5 border border-emerald-500/10 rounded-2xl p-4">
            <div className="text-xs text-gray-500 mb-1">{m.label}</div>
            <div className="text-2xl font-black text-emerald-400">{m.val}</div>
            <div className="text-xs text-gray-600">{m.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {MARKETS.map(market => {
          const st = STATUS_MAP[market.status];
          return (
            <div key={market.code} className={`border rounded-3xl overflow-hidden ${market.color}`}>
              {/* Country Header */}
              <div className="p-6 border-b border-white/5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{market.flag}</span>
                    <div>
                      <div className="font-black text-white text-lg">{market.country}</div>
                      <div className="text-xs text-gray-500">{market.regulator}</div>
                    </div>
                  </div>
                  <span className={`flex items-center gap-1.5 px-2 py-1 text-[11px] font-black rounded-lg border ${market.badge}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} />
                    {st.label}
                  </span>
                </div>
                <div className="text-sm font-black text-white mb-0.5">{market.launch_q}</div>
              </div>

              {/* Stats */}
              <div className="p-5 space-y-3">
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div>
                    <div className="font-black text-white text-lg">{market.pilot_count || "—"}</div>
                    <div className="text-[10px] text-gray-500">Пилотов</div>
                  </div>
                  <div>
                    <div className="font-black text-white text-lg">{market.active_tenders || "—"}</div>
                    <div className="text-[10px] text-gray-500">Тендеров</div>
                  </div>
                  <div>
                    <div className="font-black text-emerald-400 text-lg">${market.revenue_est_usd}</div>
                    <div className="text-[10px] text-gray-500">TAM (оц.)</div>
                  </div>
                </div>

                {/* Key sectors */}
                <div>
                  <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1.5">Ключевые отрасли</div>
                  <div className="flex flex-wrap gap-1.5">
                    {market.key_sectors.map(s => (
                      <span key={s} className="text-[10px] px-2 py-0.5 bg-white/5 border border-white/5 text-gray-400 rounded-lg">{s}</span>
                    ))}
                  </div>
                </div>

                {/* Challenge */}
                <div className="text-[11px] text-gray-500 flex items-start gap-1.5 pt-1 border-t border-white/5">
                  <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                  {market.challenge}
                </div>

                {/* Platform integration */}
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">Тендерная платформа:</span>
                  <span className="text-white font-black">{market.tender_platform}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Roadmap */}
      <div className="mb-8">
        <h2 className="font-black text-white text-xl mb-6 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-400" /> Роадмап Экспансии
        </h2>
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-[76px] top-4 bottom-4 w-0.5 bg-gradient-to-b from-emerald-500 via-amber-500 to-blue-500 opacity-20" />

          <div className="space-y-4">
            {ROADMAP.map((r, i) => (
              <div key={i} className="flex gap-5">
                <div className="w-[72px] text-right shrink-0">
                  <div className="text-xs font-black text-gray-500 mt-1">{r.q}</div>
                </div>
                <div className="relative">
                  <div className={`w-4 h-4 rounded-full border-2 mt-0.5 ${r.done ? "bg-emerald-400 border-emerald-500" : "bg-[#0A0A0B] border-gray-700"}`} />
                </div>
                <div className={`flex-1 bg-[#0A0A0B] border rounded-2xl p-4 mb-1 ${r.done ? "border-emerald-500/15" : "border-white/5"}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="font-black text-white text-sm">{r.title}</div>
                    {r.done && <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />}
                  </div>
                  <ul className="space-y-1">
                    {r.items.map((item, j) => (
                      <li key={j} className="text-xs text-gray-400 flex items-center gap-1.5">
                        <span className={`w-1 h-1 rounded-full shrink-0 ${r.done ? "bg-emerald-400" : "bg-gray-600"}`} />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA for investors */}
      <div className="bg-gradient-to-r from-emerald-900/30 to-blue-900/20 border border-emerald-500/20 rounded-3xl p-8 text-center">
        <h3 className="font-black text-white text-2xl mb-3">🚀 Горизонт — Монополия БПЛА-Инфраструктуры СНГ</h3>
        <p className="text-gray-400 max-w-2xl mx-auto mb-6 text-sm">
          Первая и единственная платформа, объединяющая реестр пилотов, тендеры B2G/B2B,
          IoT-трекеры, дронопорты и образование в одном экосистемном продукте для 6 стран.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <button className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-xl transition-all text-sm flex items-center gap-2">
            <DollarSign className="w-4 h-4" /> Инвест-меморандум (PDF)
          </button>
          <button className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 font-black rounded-xl transition-all text-sm flex items-center gap-2">
            <BarChart2 className="w-4 h-4" /> Финансовая модель 2026–2029
          </button>
        </div>
      </div>
    </div>
  );
}
