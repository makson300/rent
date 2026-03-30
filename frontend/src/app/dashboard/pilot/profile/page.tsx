"use client";

import { useState } from "react";
import {
  Shield, Award, Star, Zap, TrendingUp, Activity,
  Clock, CheckCircle, Target, Heart, AlertTriangle,
  ChevronUp, ChevronDown, BarChart2
} from "lucide-react";

// --- Mock pilot data (будет заменено реальным API в Фазе 44) ---
const PILOT_DATA = {
  name: "Игорь Самарин",
  callsign: "ALPHA-7",
  trust_score: 97,
  total_flight_hours: 312.5,
  successful_missions: 148,
  total_missions: 153,
  tenders_won: 24,
  mcs_member: true,
  registered_drones: 3,
  earnings_total: 1_840_000,
  weekly_growth: [62, 68, 71, 75, 81, 88, 97], // trust score по неделям
  badges: [
    { id: 1, icon: "🚀", label: "Первый Тендер", desc: "Выполнен первый коммерческий заказ", earned: true },
    { id: 2, icon: "💯", label: "100 Полётов", desc: "Налетано 100+ миссий", earned: true },
    { id: 3, icon: "🛡️", label: "Резерв МЧС", desc: "Зарегистрирован в реестре ПСО", earned: true },
    { id: 4, icon: "⭐", label: "Топ Пилот", desc: "Рейтинг выше 95 баллов", earned: true },
    { id: 5, icon: "🌿", label: "Агро Эксперт", desc: "10+ агрономических миссий", earned: false },
    { id: 6, icon: "🗺️", label: "Картограф LIDAR", desc: "Завершены 5 гео-съёмок", earned: false },
  ],
};

// Mini SVG line chart
function MiniChart({ data }: { data: number[] }) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const w = 200;
  const h = 50;
  const pts = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * w;
      const y = h - ((v - min) / range) * h;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-12" preserveAspectRatio="none">
      <defs>
        <linearGradient id="line-grad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#22c55e" />
        </linearGradient>
      </defs>
      <polyline
        points={pts}
        fill="none"
        stroke="url(#line-grad)"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Last point dot */}
      {(() => {
        const last = data[data.length - 1];
        const lx = w;
        const ly = h - ((last - min) / range) * h;
        return <circle cx={lx} cy={ly} r="3.5" fill="#22c55e" />;
      })()}
    </svg>
  );
}

export default function PilotProfilePage() {
  const p = PILOT_DATA;
  const successRate = Math.round((p.successful_missions / p.total_missions) * 100);
  const [showBadges, setShowBadges] = useState(true);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Header Card */}
      <div className="bg-[#0E0E10] border border-white/5 rounded-3xl p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center gap-6">
          {/* Avatar */}
          <div className="relative shrink-0">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-700 flex items-center justify-center text-3xl font-black text-white shadow-xl">
              {p.name.charAt(0)}
            </div>
            {p.mcs_member && (
              <div className="absolute -bottom-2 -right-2 w-7 h-7 bg-red-500 rounded-full flex items-center justify-center border-2 border-[#0E0E10]">
                <Heart className="w-3.5 h-3.5 text-white fill-white" />
              </div>
            )}
          </div>

          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h1 className="text-2xl font-black text-white">{p.name}</h1>
              <span className="px-2 py-0.5 text-xs font-black bg-indigo-500/20 text-indigo-400 rounded-md border border-indigo-500/30 uppercase tracking-wider">
                {p.callsign}
              </span>
            </div>
            <p className="text-gray-400 text-sm mb-3">
              {p.registered_drones} дрона · {p.mcs_member ? "Резерв МЧС ✓" : "Нет статуса МЧС"}
            </p>
            <div className="flex flex-wrap gap-2">
              {p.badges.filter(b => b.earned).map(b => (
                <span key={b.id} title={b.desc} className="text-lg cursor-help" role="img" aria-label={b.label}>
                  {b.icon}
                </span>
              ))}
            </div>
          </div>

          {/* Trust Score */}
          <div className="shrink-0 text-center bg-gradient-to-br from-emerald-500/10 to-green-500/5 border border-emerald-500/20 rounded-2xl px-8 py-4">
            <div className="text-5xl font-black text-emerald-400">{p.trust_score}</div>
            <div className="text-xs font-bold text-emerald-400/70 uppercase tracking-widest mt-1">Траст-Фактор</div>
            <div className="flex items-center justify-center gap-1 mt-1 text-xs text-emerald-400">
              <ChevronUp className="w-3 h-3" /> +6 за месяц
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { icon: <Clock className="w-5 h-5 text-blue-400" />, label: "Налёт (часов)", val: p.total_flight_hours.toFixed(1), sub: "+12.5 за месяц" },
          { icon: <CheckCircle className="w-5 h-5 text-emerald-400" />, label: "Успех миссий", val: `${successRate}%`, sub: `${p.successful_missions}/${p.total_missions}` },
          { icon: <Target className="w-5 h-5 text-amber-400" />, label: "Тендеров выиграно", val: p.tenders_won, sub: "контракты B2G" },
          { icon: <BarChart2 className="w-5 h-5 text-violet-400" />, label: "Заработок", val: `${(p.earnings_total / 1_000_000).toFixed(2)}M ₽`, sub: "за всё время" },
        ].map((s, i) => (
          <div key={i} className="bg-[#0E0E10] border border-white/5 rounded-2xl p-4 hover:border-white/10 transition-all">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center shrink-0">{s.icon}</div>
              <span className="text-xs text-gray-500">{s.label}</span>
            </div>
            <div className="text-2xl font-black text-white">{s.val}</div>
            <div className="text-xs text-gray-600 mt-0.5">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Trust Growth Chart */}
      <div className="bg-[#0E0E10] border border-white/5 rounded-3xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-400" />
            <h2 className="font-bold text-white">Траст неделя за неделей</h2>
          </div>
          <div className="flex items-center gap-1 text-emerald-400 text-sm font-bold">
            <ChevronUp className="w-4 h-4" /> +35 за 7 недель
          </div>
        </div>
        <MiniChart data={p.weekly_growth} />
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>7 нед. назад</span>
          <span>Сегодня</span>
        </div>
      </div>

      {/* Mission Health */}
      <div className="bg-[#0E0E10] border border-white/5 rounded-3xl p-6">
        <div className="flex items-center gap-2 mb-5">
          <Activity className="w-5 h-5 text-amber-400" />
          <h2 className="font-bold text-white">Здоровье Профиля</h2>
        </div>
        <div className="space-y-4">
          {[
            { label: "Успешность миссий", val: successRate, color: "bg-emerald-500", icon: <CheckCircle className="w-4 h-4 text-emerald-400" /> },
            { label: "Подтверждённые документы", val: 85, color: "bg-blue-500", icon: <Shield className="w-4 h-4 text-blue-400" /> },
            { label: "Скорость отклика (медиана)", val: 72, color: "bg-amber-500", icon: <Zap className="w-4 h-4 text-amber-400" /> },
            { label: "Отсутствие нарушений", val: 100, color: "bg-emerald-500", icon: <AlertTriangle className="w-4 h-4 text-emerald-400" /> },
          ].map((m, i) => (
            <div key={i} className="flex items-center gap-4">
              {m.icon}
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">{m.label}</span>
                  <span className="text-white font-bold">{m.val}%</span>
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                  <div className={`h-full ${m.color} rounded-full transition-all`} style={{ width: `${m.val}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Badges & Achievements */}
      <div className="bg-[#0E0E10] border border-white/5 rounded-3xl p-6">
        <button
          onClick={() => setShowBadges(!showBadges)}
          className="flex items-center justify-between w-full"
        >
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-400" />
            <h2 className="font-bold text-white">Достижения и Бейджи</h2>
            <span className="text-xs text-gray-500">({p.badges.filter(b => b.earned).length}/{p.badges.length})</span>
          </div>
          {showBadges ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
        </button>

        {showBadges && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-5">
            {p.badges.map((b) => (
              <div
                key={b.id}
                className={`rounded-2xl p-4 border flex items-center gap-3 transition-all ${
                  b.earned
                    ? "bg-white/5 border-white/10 hover:border-amber-500/30"
                    : "bg-white/[0.02] border-white/5 opacity-40 grayscale"
                }`}
              >
                <span className="text-3xl" role="img" aria-label={b.label}>{b.icon}</span>
                <div>
                  <div className="font-bold text-sm text-white">{b.label}</div>
                  <div className="text-[11px] text-gray-500">{b.desc}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
