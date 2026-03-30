"use client";

import { useState } from "react";
import {
  Shield, Zap, TrendingUp, Activity,
  Clock, CheckCircle, Target, Heart, AlertTriangle,
  ChevronUp, ChevronDown, BarChart2, Ban, TrendingDown,
  ShieldOff, ThumbsUp, Satellite
} from "lucide-react";
import { profileApi, type Profile, type PilotStats } from "@/lib/api";
import { useApiData } from "@/hooks/useApiData";

// ---------------------------------------------------------------------------
// Бейджи вычисляются из реальных данных
// ---------------------------------------------------------------------------
interface Badge { id: number; icon: string; label: string; desc: string; earned: boolean; }

function computeBadges(stats: PilotStats | null, profile: Profile | null): Badge[] {
  return [
    { id: 1, icon: "🚀", label: "Первый Трекер",       desc: "Зарегистрирован Квазар-ID",       earned: (stats?.trackers ?? 0) > 0 },
    { id: 2, icon: "📡", label: "ОрВД Онлайн",         desc: "Трекер виден в ЕС ОрВД",           earned: (stats?.trackers ?? 0) > 0 },
    { id: 3, icon: "🛡️", label: "Резерв МЧС",          desc: "Статус добровольца",               earned: profile?.is_emergency_volunteer ?? false },
    { id: 4, icon: "🎓", label: "Первый Курс",         desc: "Записан на курс Академии",          earned: (stats?.enrollments ?? 0) > 0 },
    { id: 5, icon: "📜", label: "Сертификат Горизонт", desc: "Получен сертификат ФАП-69",         earned: (stats?.certificates ?? 0) > 0 },
    { id: 6, icon: "💰", label: "Data Seller",         desc: "Датасет выставлен на маркете",      earned: (stats?.datasets_listed ?? 0) > 0 },
    { id: 7, icon: "⚖️", label: "Патентовладелец",     desc: "Подана патентная заявка",           earned: (stats?.patents ?? 0) > 0 },
    { id: 8, icon: "🏭", label: "B2B Лизинг",          desc: "Подана заявка на лизинг дрона",     earned: (stats?.leasing_applications ?? 0) > 0 },
  ];
}

// ---------------------------------------------------------------------------
// Mini SVG chart
// ---------------------------------------------------------------------------
function MiniChart({ data }: { data: number[] }) {
  const min   = Math.min(...data);
  const max   = Math.max(...data);
  const range = max - min || 1;
  const w = 200; const h = 50;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / range) * h;
    return `${x},${y}`;
  }).join(" ");

  const last = data[data.length - 1];
  const lx = w;
  const ly = h - ((last - min) / range) * h;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-12" preserveAspectRatio="none">
      <defs>
        <linearGradient id="line-grad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#22c55e" />
        </linearGradient>
      </defs>
      <polyline points={pts} fill="none" stroke="url(#line-grad)"
        strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={lx} cy={ly} r="3.5" fill="#22c55e" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Главный компонент
// ---------------------------------------------------------------------------
export default function PilotProfilePage() {
  const { data: profile, loading: profileLoading } = useApiData(() => profileApi.me());
  const { data: stats,   loading: statsLoading }   = useApiData(() => profileApi.stats());
  const [showBadges, setShowBadges] = useState(true);

  const isLoading   = profileLoading || statsLoading;
  const badges      = computeBadges(stats, profile);
  const displayName = profile?.full_name ?? profile?.username ?? "Пилот Горизонт";
  const flightHours = stats?.flight_hours ?? 0;
  const rescues     = stats?.volunteer_rescues ?? 0;

  // Траст-фактор: рассчитывается на основе реальных метрик
  const trustScore = Math.min(
    50
    + (stats?.certificates ?? 0) * 10
    + (flightHours > 50 ? 15 : Math.floor(flightHours / 4))
    + (profile?.is_emergency_volunteer ? 10 : 0)
    + (rescues * 5),
    99
  );

  // Моковые данные для панелей, которые ещё не имеют реального API
  const WEEKLY_GROWTH = [62, 68, 71, 75, 81, 88, trustScore];
  const ANTI_DUMPING  = { score: 0, max_penalty: 30, violations: [] as {date:string;delta:number;tender:string}[], status: "clean" };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        <Satellite className="w-6 h-6 animate-pulse mr-3 text-indigo-400" />
        Загружаем профиль пилота...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">

      {/* Header Card */}
      <div className="bg-[#0E0E10] border border-white/5 rounded-3xl p-6 lg:p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center gap-6">
          {/* Avatar */}
          <div className="relative shrink-0">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-700 flex items-center justify-center text-3xl font-black text-white shadow-xl">
              {displayName.charAt(0).toUpperCase()}
            </div>
            {profile?.is_emergency_volunteer && (
              <div className="absolute -bottom-2 -right-2 w-7 h-7 bg-red-500 rounded-full flex items-center justify-center border-2 border-[#0E0E10]">
                <Heart className="w-3.5 h-3.5 text-white fill-white" />
              </div>
            )}
          </div>

          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h1 className="text-2xl font-black text-white">{displayName}</h1>
              {profile?.username && (
                <span className="px-2 py-0.5 text-xs font-black bg-indigo-500/20 text-indigo-400 rounded-md border border-indigo-500/30 uppercase tracking-wider">
                  @{profile.username}
                </span>
              )}
              {profile?.is_admin && (
                <span className="px-2 py-0.5 text-xs font-black bg-red-500/20 text-red-400 rounded-md border border-red-500/30 uppercase tracking-wider">
                  ADMIN
                </span>
              )}
            </div>
            <p className="text-gray-400 text-sm mb-3">
              {profile?.company_name ?? (profile?.user_type === "company" ? "Компания" : "Частный пилот")}
              {profile?.is_emergency_volunteer ? " · Резерв МЧС ✓" : ""}
            </p>
            <div className="flex flex-wrap gap-2">
              {badges.filter(b => b.earned).map(b => (
                <span key={b.id} title={b.desc} className="text-lg cursor-help" role="img" aria-label={b.label}>
                  {b.icon}
                </span>
              ))}
            </div>
          </div>

          {/* Trust Score */}
          <div className="shrink-0 text-center bg-gradient-to-br from-emerald-500/10 to-green-500/5 border border-emerald-500/20 rounded-2xl px-8 py-4">
            <div className="text-5xl font-black text-emerald-400">{trustScore}</div>
            <div className="text-xs font-bold text-emerald-400/70 uppercase tracking-widest mt-1">Траст-Фактор</div>
            <div className="flex items-center justify-center gap-1 mt-1 text-xs text-emerald-400">
              <ChevronUp className="w-3 h-3" /> Из 99 баллов
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid — реальные данные */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { icon: <Clock className="w-5 h-5 text-blue-400" />,    label: "Налёт (часов)",   val: flightHours.toFixed(1),               sub: "подтверждено" },
          { icon: <Satellite className="w-5 h-5 text-violet-400" />, label: "Трекеров",     val: String(stats?.trackers ?? 0),         sub: "Квазар-ID" },
          { icon: <CheckCircle className="w-5 h-5 text-emerald-400" />, label: "Сертификатов", val: String(stats?.certificates ?? 0), sub: "Академия Горизонт" },
          { icon: <BarChart2 className="w-5 h-5 text-amber-400" />, label: "Датасетов",     val: String(stats?.datasets_listed ?? 0),  sub: "Data Marketplace" },
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

      {/* Подробная статка по модулям */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { label: "Записей на курсы",      val: stats?.enrollments ?? 0,          color: "text-indigo-400" },
          { label: "Броней дронопортов",    val: stats?.active_bookings ?? 0,       color: "text-cyan-400" },
          { label: "Патентных заявок",      val: stats?.patents ?? 0,              color: "text-purple-400" },
          { label: "Лизинговых заявок",     val: stats?.leasing_applications ?? 0,  color: "text-amber-400" },
          { label: "Спасательных операций", val: rescues,                          color: "text-red-400" },
          { label: "Реферальный бонус",     val: `+${stats?.referral_bonus ?? 0} ₽`, color: "text-emerald-400" },
        ].map((s, i) => (
          <div key={i} className="bg-[#0E0E10] border border-white/5 rounded-xl p-4">
            <div className="text-xs text-gray-500 mb-1">{s.label}</div>
            <div className={`text-xl font-black ${s.color}`}>{s.val}</div>
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
            <ChevronUp className="w-4 h-4" /> {trustScore - 62} за 7 недель
          </div>
        </div>
        <MiniChart data={WEEKLY_GROWTH} />
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>7 нед. назад</span><span>Сегодня</span>
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
            { label: "Подтверждённые сертификаты", val: Math.min((stats?.certificates ?? 0) * 25, 100), color: "bg-emerald-500", icon: <CheckCircle className="w-4 h-4 text-emerald-400" /> },
            { label: "Часы налёта верифицированы",  val: Math.min(Math.floor(flightHours / 5), 100),    color: "bg-blue-500",    icon: <Clock className="w-4 h-4 text-blue-400" /> },
            { label: "Трекеры зарегистрированы",    val: (stats?.trackers ?? 0) > 0 ? 100 : 0,          color: "bg-violet-500",  icon: <Satellite className="w-4 h-4 text-violet-400" /> },
            { label: "Отсутствие нарушений",        val: 100,                                            color: "bg-emerald-500", icon: <Shield className="w-4 h-4 text-emerald-400" /> },
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

      {/* Badges */}
      <div className="bg-[#0E0E10] border border-white/5 rounded-3xl p-6">
        <button onClick={() => setShowBadges(!showBadges)} className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <span className="text-xl">🏅</span>
            <h2 className="font-bold text-white">Достижения и Бейджи</h2>
            <span className="text-xs text-gray-500">({badges.filter(b => b.earned).length}/{badges.length})</span>
          </div>
          {showBadges ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
        </button>

        {showBadges && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5">
            {badges.map(b => (
              <div
                key={b.id}
                className={`rounded-2xl p-4 border flex items-center gap-3 transition-all ${
                  b.earned
                    ? "bg-white/5 border-white/10 hover:border-amber-500/30"
                    : "bg-white/[0.02] border-white/5 opacity-40 grayscale"
                }`}
              >
                <span className="text-2xl" role="img" aria-label={b.label}>{b.icon}</span>
                <div>
                  <div className="font-bold text-sm text-white">{b.label}</div>
                  <div className="text-[11px] text-gray-500">{b.desc}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Anti-Dumping Panel */}
      <div className="bg-[#0E0E10] border border-white/5 rounded-3xl p-6">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <Ban className="w-5 h-5 text-red-400" />
            <h2 className="font-bold text-white">Анти-Демпинг Индекс</h2>
            <span className="text-xs text-gray-600">(Фаза 37)</span>
          </div>
          <span className="px-2.5 py-1 text-xs font-black rounded-full border bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
            ✅ Чистый профиль
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
          {/* Score Gauge */}
          <div className="bg-[#121214] rounded-2xl p-4 border border-white/5 flex flex-col items-center">
            <div className="relative w-28 h-28 mb-2">
              <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#1a1a1d" strokeWidth="10" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#22c55e"
                  strokeWidth="10"
                  strokeDasharray={`${(ANTI_DUMPING.score / ANTI_DUMPING.max_penalty) * 251.2} 251.2`}
                  strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="text-2xl font-black text-white">{ANTI_DUMPING.score}</div>
                <div className="text-[10px] text-gray-500">из {ANTI_DUMPING.max_penalty}</div>
              </div>
            </div>
            <div className="text-xs text-gray-400 text-center">Штрафных баллов (0 = чисто)</div>
          </div>

          {/* Rules */}
          <div className="space-y-2">
            {[
              { icon: <ThumbsUp className="w-4 h-4 text-emerald-400" />, label: "Предложение ≥ 70% от НМЦК" },
              { icon: <ThumbsUp className="w-4 h-4 text-emerald-400" />, label: "Не более 3 откликов ниже рынка в месяц" },
              { icon: <ShieldOff className="w-4 h-4 text-gray-500" />,   label: "Снижение на каждом тендере подряд" },
              { icon: <TrendingDown className="w-4 h-4 text-gray-500" />,label: "35%+ демпинг — авто-блокировка" },
            ].map((r, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-gray-400">
                {r.icon}
                <span>{r.label}</span>
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400 ml-auto" />
              </div>
            ))}
          </div>
        </div>

        {ANTI_DUMPING.violations.length === 0 ? (
          <div className="bg-emerald-500/5 border border-emerald-500/15 rounded-2xl p-4 flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <div className="text-sm font-bold text-white">Нарушений не зафиксировано</div>
              <div className="text-xs text-gray-500">ИИ-мониторинг активен. Продолжайте участвовать честно.</div>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {ANTI_DUMPING.violations.map((v, i) => (
              <div key={i} className="bg-red-500/5 border border-red-500/10 rounded-xl p-3 flex items-center justify-between">
                <div>
                  <div className="text-sm text-white font-bold">{v.tender}</div>
                  <div className="text-xs text-gray-500">{v.date}</div>
                </div>
                <div className="text-red-400 font-black text-sm">+{v.delta} балл.</div>
              </div>
            ))}
          </div>
        )}

        <p className="text-[11px] text-gray-600 mt-4 flex items-center gap-1">
          <AlertTriangle className="w-3 h-3" />
          При накоплении {ANTI_DUMPING.max_penalty} баллов участие в тендерах блокируется на 30 дней.
        </p>
      </div>

    </div>
  );
}
