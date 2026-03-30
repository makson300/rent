"use client";

import { useState } from "react";
import {
  Trophy, Medal, Crown, TrendingUp, Star, Shield,
  Zap, Target, Plane, MapPin, BarChart2, Filter
} from "lucide-react";

// --- Mock leaderboard data ---
const PILOTS = [
  { rank: 1,  name: "Игорь Самарин",     city: "Москва",           trust: 97, missions: 312, hours: 1840, tenders: 24, anti_dump: 0,  badge: "🏆", tier: "legend"   },
  { rank: 2,  name: "Алексей Воронов",   city: "Казань",           trust: 94, missions: 278, hours: 1523, tenders: 19, anti_dump: 0,  badge: "🥈", tier: "master"   },
  { rank: 3,  name: "Марина Ступак",     city: "Краснодар",        trust: 92, missions: 241, hours: 1218, tenders: 16, anti_dump: 2,  badge: "🥉", tier: "master"   },
  { rank: 4,  name: "Денис Зотов",       city: "Новосибирск",      trust: 88, missions: 198, hours: 987,  tenders: 11, anti_dump: 0,  badge: "⭐", tier: "pro"      },
  { rank: 5,  name: "Сергей Ковалёв",    city: "Санкт-Петербург",  trust: 86, missions: 187, hours: 924,  tenders: 9,  anti_dump: 0,  badge: "⭐", tier: "pro"      },
  { rank: 6,  name: "Наталья Орлова",    city: "Екатеринбург",     trust: 84, missions: 162, hours: 801,  tenders: 7,  anti_dump: 5,  badge: "✦",  tier: "pro"      },
  { rank: 7,  name: "Роман Власов",      city: "Владивосток",      trust: 81, missions: 143, hours: 712,  tenders: 6,  anti_dump: 0,  badge: "✦",  tier: "pro"      },
  { rank: 8,  name: "Анна Петрова",      city: "Ростов-на-Дону",   trust: 79, missions: 128, hours: 634,  tenders: 5,  anti_dump: 1,  badge: "✦",  tier: "advanced" },
  { rank: 9,  name: "Тимур Садыков",     city: "Казань",           trust: 77, missions: 114, hours: 571,  tenders: 4,  anti_dump: 0,  badge: "•",  tier: "advanced" },
  { rank: 10, name: "Виктор Лебедев",    city: "Омск",             trust: 74, missions: 99,  hours: 487,  tenders: 3,  anti_dump: 8,  badge: "•",  tier: "advanced" },
];

const COMPANIES = [
  { rank: 1, name: "АэроПром Групп",      city: "Москва",          contracts: 48, volume_m: 142, rating: 98, tier: "platinum" },
  { rank: 2, name: "ДронСервис Поволжье", city: "Казань",          contracts: 37, volume_m: 89,  rating: 95, tier: "gold"     },
  { rank: 3, name: "УралАэро",            city: "Екатеринбург",    contracts: 28, volume_m: 71,  rating: 93, tier: "gold"     },
  { rank: 4, name: "СибирьДрон",         city: "Новосибирск",     contracts: 22, volume_m: 54,  rating: 90, tier: "silver"   },
  { rank: 5, name: "ЮжныйДрон",          city: "Краснодар",       contracts: 18, volume_m: 43,  rating: 88, tier: "silver"   },
];

const TIER_STYLES: Record<string, { bg: string; text: string; border: string; label: string }> = {
  legend:   { bg: "bg-amber-500/10",   text: "text-amber-400",   border: "border-amber-500/30",   label: "Легенда"   },
  master:   { bg: "bg-violet-500/10",  text: "text-violet-400",  border: "border-violet-500/30",  label: "Мастер"    },
  pro:      { bg: "bg-blue-500/10",    text: "text-blue-400",    border: "border-blue-500/30",    label: "Профи"     },
  advanced: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/30", label: "Опытный"   },
  platinum: { bg: "bg-cyan-500/10",    text: "text-cyan-400",    border: "border-cyan-500/30",    label: "Платинум"  },
  gold:     { bg: "bg-amber-500/10",   text: "text-amber-400",   border: "border-amber-500/30",   label: "Золото"    },
  silver:   { bg: "bg-gray-500/10",    text: "text-gray-300",    border: "border-gray-500/30",    label: "Серебро"   },
};

type SortKey = "trust" | "missions" | "hours" | "tenders";

const SORT_OPTIONS: { key: SortKey; label: string; icon: React.ReactNode }[] = [
  { key: "trust",    label: "Траст-Фактор",   icon: <Shield className="w-3.5 h-3.5" /> },
  { key: "missions", label: "Миссии",          icon: <Target className="w-3.5 h-3.5" /> },
  { key: "hours",    label: "Налёт часов",     icon: <Plane className="w-3.5 h-3.5" />  },
  { key: "tenders",  label: "Тендеры",         icon: <Zap className="w-3.5 h-3.5" />    },
];

function RankBadge({ rank }: { rank: number }) {
  if (rank === 1) return <Crown className="w-6 h-6 text-amber-400" />;
  if (rank === 2) return <Medal className="w-5 h-5 text-gray-300" />;
  if (rank === 3) return <Medal className="w-5 h-5 text-amber-700" />;
  return <span className="text-gray-500 font-black text-sm w-6 text-center">#{rank}</span>;
}

export default function LeaderboardPage() {
  const [tab, setTab]         = useState<"pilots" | "companies">("pilots");
  const [sortBy, setSortBy]   = useState<SortKey>("trust");
  const [region, setRegion]   = useState("Все");

  const REGIONS = ["Все", "Москва", "Санкт-Петербург", "Казань", "Новосибирск", "Краснодар", "Екатеринбург"];

  const sorted = [...PILOTS]
    .filter(p => region === "Все" || p.city === region)
    .sort((a, b) => b[sortBy] - a[sortBy])
    .map((p, i) => ({ ...p, rank: i + 1 }));

  // Top-3 для подиума
  const podium = sorted.slice(0, 3);
  const rest   = sorted.slice(3);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-amber-500/15 text-amber-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Trophy className="w-3.5 h-3.5" /> Фаза 45 · Рейтинг Платформы
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Trophy className="w-8 h-8 text-amber-400" />
          Лидерборд «Горизонт»
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Рейтинг лучших пилотов и компаний по Траст-Фактору, объёму миссий и выигранных тендеров.
          Обновляется в реальном времени.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10 mb-6 gap-1">
        {(["pilots", "companies"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-5 py-2.5 text-sm font-bold border-b-2 transition-colors ${tab === t ? "border-amber-500 text-amber-400" : "border-transparent text-gray-400 hover:text-white"}`}>
            {t === "pilots" ? "🧑‍✈️ Пилоты" : "🏢 Компании"}
          </button>
        ))}
      </div>

      {tab === "pilots" && (
        <>
          {/* Controls */}
          <div className="flex flex-wrap gap-3 mb-6">
            {/* Sort */}
            <div className="flex gap-1.5">
              {SORT_OPTIONS.map(opt => (
                <button key={opt.key} onClick={() => setSortBy(opt.key)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
                    sortBy === opt.key ? "bg-amber-500/15 text-amber-400 border-amber-500/30" : "bg-[#0E0E10] text-gray-400 border-white/10 hover:border-white/20"
                  }`}>
                  {opt.icon} {opt.label}
                </button>
              ))}
            </div>
            {/* Region filter */}
            <select
              value={region}
              onChange={e => setRegion(e.target.value)}
              className="ml-auto bg-[#0E0E10] border border-white/10 text-gray-300 text-xs font-bold rounded-lg px-3 py-1.5 outline-none"
            >
              {REGIONS.map(r => <option key={r}>{r}</option>)}
            </select>
          </div>

          {/* Podium (top 3) */}
          {sorted.length >= 3 && region === "Все" && (
            <div className="grid grid-cols-3 gap-3 mb-8">
              {[podium[1], podium[0], podium[2]].map((p, idx) => {
                const isFirst = p.rank === 1;
                const tier = TIER_STYLES[p.tier];
                return (
                  <div key={p.rank} className={`relative rounded-3xl border p-5 text-center transition-all ${tier.bg} ${tier.border} ${isFirst ? "scale-105 shadow-xl shadow-amber-500/10 -mt-3" : ""}`}>
                    {isFirst && <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 text-2xl">👑</div>}
                    <div className="text-3xl mb-2">{p.badge}</div>
                    <div className="font-black text-white text-sm">{p.name}</div>
                    <div className="text-xs text-gray-500 flex items-center justify-center gap-1 mb-2">
                      <MapPin className="w-3 h-3" /> {p.city}
                    </div>
                    <div className={`text-2xl font-black ${tier.text}`}>{p.trust}%</div>
                    <div className="text-[10px] text-gray-500 uppercase tracking-wider">Траст-Фактор</div>
                    <div className={`mt-2 inline-block px-2 py-0.5 rounded text-[10px] font-black ${tier.bg} ${tier.text} border ${tier.border}`}>
                      {tier.label}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Full Table */}
          <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl overflow-hidden">
            {/* Table header */}
            <div className="grid grid-cols-12 gap-2 px-5 py-3 border-b border-white/5 text-[10px] font-black text-gray-500 uppercase tracking-wider">
              <div className="col-span-1">#</div>
              <div className="col-span-4">Пилот</div>
              <div className="col-span-2 text-right">Траст</div>
              <div className="col-span-2 text-right">Миссии</div>
              <div className="col-span-2 text-right">Налёт</div>
              <div className="col-span-1 text-right">Тендеры</div>
            </div>

            {sorted.map((pilot, idx) => {
              const tier = TIER_STYLES[pilot.tier];
              return (
                <div
                  key={pilot.rank}
                  className={`grid grid-cols-12 gap-2 px-5 py-3.5 border-b border-white/[0.03] items-center transition-all hover:bg-white/[0.02] ${idx < 3 ? "bg-white/[0.01]" : ""}`}
                >
                  {/* Rank */}
                  <div className="col-span-1 flex items-center justify-center">
                    <RankBadge rank={pilot.rank} />
                  </div>
                  {/* Name */}
                  <div className="col-span-4 flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center font-black text-white text-xs shrink-0">
                      {pilot.name.charAt(0)}
                    </div>
                    <div>
                      <div className="font-bold text-white text-sm">{pilot.name}</div>
                      <div className="flex items-center gap-1 text-[10px] text-gray-500">
                        <MapPin className="w-2.5 h-2.5" /> {pilot.city}
                        {pilot.anti_dump > 0 && <span className="ml-1 text-red-400 font-black">⚠ -{pilot.anti_dump}</span>}
                      </div>
                    </div>
                  </div>
                  {/* Trust */}
                  <div className="col-span-2 text-right">
                    <div className={`font-black text-sm ${sortBy === "trust" ? tier.text : "text-white"}`}>{pilot.trust}%</div>
                    <div className="w-full h-1 bg-white/5 rounded-full mt-1 ml-auto">
                      <div className={`h-full rounded-full ${tier.bg.replace("/10", "/60")}`} style={{ width: `${pilot.trust}%` }} />
                    </div>
                  </div>
                  {/* Missions */}
                  <div className={`col-span-2 text-right font-black text-sm ${sortBy === "missions" ? "text-blue-400" : "text-gray-400"}`}>
                    {pilot.missions}
                  </div>
                  {/* Hours */}
                  <div className={`col-span-2 text-right font-black text-sm ${sortBy === "hours" ? "text-violet-400" : "text-gray-400"}`}>
                    {pilot.hours} ч
                  </div>
                  {/* Tenders */}
                  <div className={`col-span-1 text-right font-black text-sm ${sortBy === "tenders" ? "text-emerald-400" : "text-gray-400"}`}>
                    {pilot.tenders}
                  </div>
                </div>
              );
            })}
          </div>

          {sorted.length === 0 && (
            <div className="text-center py-12 text-gray-500 text-sm">Нет пилотов в выбранном регионе</div>
          )}
        </>
      )}

      {tab === "companies" && (
        <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl overflow-hidden">
          <div className="grid grid-cols-12 gap-2 px-5 py-3 border-b border-white/5 text-[10px] font-black text-gray-500 uppercase tracking-wider">
            <div className="col-span-1">#</div>
            <div className="col-span-4">Компания</div>
            <div className="col-span-2 text-right">Рейтинг</div>
            <div className="col-span-2 text-right">Контракты</div>
            <div className="col-span-3 text-right">Объём</div>
          </div>
          {COMPANIES.map((company, idx) => {
            const tier = TIER_STYLES[company.tier];
            return (
              <div key={company.rank} className="grid grid-cols-12 gap-2 px-5 py-4 border-b border-white/[0.03] items-center hover:bg-white/[0.02] transition-all">
                <div className="col-span-1 flex items-center justify-center">
                  <RankBadge rank={company.rank} />
                </div>
                <div className="col-span-4">
                  <div className="font-black text-white text-sm">{company.name}</div>
                  <div className="flex items-center gap-1 text-[10px] text-gray-500">
                    <MapPin className="w-2.5 h-2.5" /> {company.city}
                  </div>
                </div>
                <div className="col-span-2 text-right">
                  <div className={`font-black text-sm ${tier.text}`}>{company.rating}</div>
                  <div className={`text-[10px] font-black ${tier.text} ${tier.bg} ${tier.border} border px-1.5 py-0.5 rounded inline-block mt-0.5`}>
                    {tier.label}
                  </div>
                </div>
                <div className="col-span-2 text-right font-black text-sm text-blue-400">{company.contracts}</div>
                <div className="col-span-3 text-right font-black text-sm text-emerald-400">{company.volume_m} млн ₽</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Footer note */}
      <p className="text-xs text-gray-600 text-center mt-6 flex items-center justify-center gap-1">
        <TrendingUp className="w-3 h-3" />
        Рейтинг рассчитывается автоматически на основе верифицированных данных телеметрии, тендерной истории и Анти-Демпинг Индекса
      </p>
    </div>
  );
}
