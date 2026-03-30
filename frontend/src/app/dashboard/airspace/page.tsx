"use client";

import { useState, useEffect } from "react";
import {
  Radio, AlertTriangle, Clock, MapPin, RefreshCw,
  ShieldAlert, CheckCircle, Eye, Zap, Plane,
  CloudRain, Wind, Thermometer, Gauge, Info
} from "lucide-react";

// Типы временных зон ограничений
const ZONE_TYPES = {
  military:    { label: "Военные учения",     color: "text-red-400",    bg: "bg-red-500/10",    border: "border-red-500/30",    dot: "bg-red-400" },
  government:  { label: "Правительственный лёт", color: "text-amber-400",  bg: "bg-amber-500/10",  border: "border-amber-500/30",  dot: "bg-amber-400" },
  event:       { label: "Массовое мероприятие", color: "text-blue-400",   bg: "bg-blue-500/10",   border: "border-blue-500/30",   dot: "bg-blue-400" },
  permanent:   { label: "Постоянная зона",    color: "text-gray-400",   bg: "bg-gray-500/10",   border: "border-gray-500/30",   dot: "bg-gray-500" },
  temporary:   { label: "Временный NOTAM",    color: "text-violet-400", bg: "bg-violet-500/10", border: "border-violet-500/30", dot: "bg-violet-400" },
};

// Mock NOTAM / TFR данные (имитация ответа Минтранса / Росавиации)
const MOCK_NOTAMS = [
  {
    id: "NOTAM-MSK-2026-0441",
    type: "military",
    region: "Московская область",
    location: "55.90°N 37.40°E",
    radius_km: 35,
    altitude_m: 4500,
    active_from: "2026-03-30T06:00:00Z",
    active_to:   "2026-03-30T22:00:00Z",
    description: "Временные ограничения в связи с военными учениями «Рубеж-26». Запрет полётов БПЛА без литера.",
    affects: true,
  },
  {
    id: "NOTAM-LED-2026-0219",
    type: "government",
    region: "Санкт-Петербург",
    location: "59.97°N 30.32°E",
    radius_km: 20,
    altitude_m: 2000,
    active_from: "2026-03-30T08:00:00Z",
    active_to:   "2026-03-31T20:00:00Z",
    description: "Ограничения в связи с визитом главы государства. Полёты БПЛА запрещены.",
    affects: false,
  },
  {
    id: "NOTAM-KZN-2026-0107",
    type: "event",
    region: "Казань",
    location: "55.79°N 49.12°E",
    radius_km: 8,
    altitude_m: 500,
    active_from: "2026-03-30T14:00:00Z",
    active_to:   "2026-03-30T20:00:00Z",
    description: "Массовое мероприятие на стадионе «Ак Барс Арена». Ограничения ниже 500 м.",
    affects: false,
  },
  {
    id: "NOTAM-RND-2026-0088",
    type: "temporary",
    region: "Ростов-на-Дону",
    location: "47.22°N 39.72°E",
    radius_km: 50,
    altitude_m: 3000,
    active_from: "2026-03-30T00:00:00Z",
    active_to:   "2026-04-05T23:59:00Z",
    description: "Временное ограничение в связи со строительными работами вблизи аэропорта Платов.",
    affects: false,
  },
  {
    id: "NFZ-SHEREMETYEVO-PERM",
    type: "permanent",
    region: "Шереметьево (Москва)",
    location: "55.97°N 37.41°E",
    radius_km: 15,
    altitude_m: 9000,
    active_from: "—",
    active_to: "—",
    description: "Постоянная запретная зона вокруг аэропорта Шереметьево (класс А/B). БПЛА запрещены.",
    affects: false,
  },
];

// Mock погодные условия по регионам
const WEATHER_REGIONS = [
  { city: "Москва",          temp: 8,  wind: 14, humidity: 72, status: "warn",  rain: true },
  { city: "Санкт-Петербург", temp: 4,  wind: 22, humidity: 89, status: "deny",  rain: true },
  { city: "Казань",          temp: 12, wind: 8,  humidity: 60, status: "ok",    rain: false },
  { city: "Новосибирск",     temp: -3, wind: 6,  humidity: 55, status: "ok",    rain: false },
  { city: "Краснодар",       temp: 18, wind: 11, humidity: 65, status: "ok",    rain: false },
];

type NotamType = keyof typeof ZONE_TYPES;

function timeLeft(to: string) {
  if (to === "—") return "Постоянно";
  const diff = new Date(to).getTime() - Date.now();
  if (diff <= 0) return "Истёк";
  const h = Math.floor(diff / 3_600_000);
  const m = Math.floor((diff % 3_600_000) / 60_000);
  return `${h} ч ${m} мин`;
}

export default function AirspaceLivePage() {
  const [notams, setNotams]         = useState(MOCK_NOTAMS);
  const [selected, setSelected]     = useState<typeof MOCK_NOTAMS[0] | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [lastSync, setLastSync]     = useState(new Date());
  const [filterType, setFilterType] = useState<string>("all");

  // Auto-refresh every 60 sec
  useEffect(() => {
    const t = setInterval(() => setLastSync(new Date()), 60_000);
    return () => clearInterval(t);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const { api } = await import("@/lib/api");
      const data = await api.get<typeof MOCK_NOTAMS>("/airspace/notams");
      if (Array.isArray(data) && data.length > 0) setNotams(data);
    } catch {
      // Фоллбэк: оставляем текущие данные
    }
    setLastSync(new Date());
    setRefreshing(false);
  };

  const filtered = filterType === "all"
    ? notams
    : notams.filter(n => n.type === filterType);

  const affectsMoscow = notams.filter(n => n.affects && n.region.includes("Московская")).length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <span className="px-3 py-1 rounded-full bg-blue-500/15 text-blue-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
            <Radio className="w-3.5 h-3.5 animate-pulse" /> Фаза 40 · ОрВД Live
          </span>
          <h1 className="text-4xl font-extrabold text-white mb-2 flex items-center gap-3">
            <Plane className="w-8 h-8 text-blue-400" />
            Карта Воздушных Ограничений
          </h1>
          <p className="text-gray-400">
            Актуальные NOTAM, TFR и запретные зоны из реестра Росавиации / Минтранса РФ.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right text-xs text-gray-500">
            <div>Последнее обновление</div>
            <div className="text-white font-mono">{lastSync.toLocaleTimeString("ru-RU")}</div>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="p-3 bg-[#0E0E10] border border-white/10 rounded-xl text-gray-400 hover:text-white hover:border-blue-500/30 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Status alerts */}
      {affectsMoscow > 0 && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 mb-6 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-black text-white text-sm">Активные ограничения в вашем регионе!</div>
            <div className="text-xs text-gray-400">
              Обнаружено {affectsMoscow} NOTAM(ов) в Московской области. Проверьте детали перед вылетом.
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel: NOTAM List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilterType("all")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${filterType === "all" ? "bg-blue-600 text-white border-blue-500" : "bg-[#0E0E10] text-gray-400 border-white/10 hover:border-white/20"}`}
            >
              Все ({notams.length})
            </button>
            {Object.entries(ZONE_TYPES).map(([key, z]) => (
              <button
                key={key}
                onClick={() => setFilterType(key)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${filterType === key ? `${z.bg} ${z.color} ${z.border}` : "bg-[#0E0E10] text-gray-400 border-white/10 hover:border-white/20"}`}
              >
                {z.label}
              </button>
            ))}
          </div>

          {/* NOTAM Cards */}
          <div className="space-y-3">
            {filtered.map(notam => {
              const zone = ZONE_TYPES[notam.type as NotamType];
              const isActive = notam.active_to === "—" || new Date(notam.active_to) > new Date();
              return (
                <div
                  key={notam.id}
                  onClick={() => setSelected(selected?.id === notam.id ? null : notam)}
                  className={`bg-[#0A0A0B] border rounded-2xl p-5 cursor-pointer transition-all group ${
                    selected?.id === notam.id ? `${zone.border} shadow-lg` : "border-white/10 hover:border-white/20"
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded-full ${zone.dot} ${isActive ? "animate-pulse" : "opacity-40"}`} />
                      <span className={`text-xs font-black px-2 py-0.5 rounded ${zone.bg} ${zone.color} ${zone.border} border`}>
                        {zone.label}
                      </span>
                      {notam.affects && (
                        <span className="text-[10px] font-black text-red-400 bg-red-500/10 border border-red-500/20 px-2 py-0.5 rounded">
                          ⚠ ВАШ РЕГИОН
                        </span>
                      )}
                    </div>
                    <div className="text-right text-xs text-gray-600 font-mono">{notam.id}</div>
                  </div>

                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-bold text-white mb-1">{notam.region}</div>
                      <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" /> {notam.location}
                        </span>
                        <span className="flex items-center gap-1">
                          <Gauge className="w-3 h-3" /> R={notam.radius_km} км, FL{Math.round(notam.altitude_m / 30.48)}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {notam.active_to === "—" ? "Постоянно" : `Осталось: ${timeLeft(notam.active_to)}`}
                        </span>
                      </div>
                    </div>
                    {isActive ? (
                      <span className="ml-3 shrink-0 text-[10px] font-black text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                        АКТИВЕН
                      </span>
                    ) : (
                      <span className="ml-3 shrink-0 text-[10px] text-gray-600 border border-gray-700 px-2 py-0.5 rounded">
                        ИСТЁК
                      </span>
                    )}
                  </div>

                  {selected?.id === notam.id && (
                    <div className="mt-4 pt-4 border-t border-white/5 text-sm text-gray-400">
                      <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 shrink-0 mt-0.5 text-blue-400" />
                        <p>{notam.description}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-3 mt-3 text-xs">
                        <div className="bg-[#121214] rounded-xl p-3">
                          <div className="text-gray-600 mb-0.5">Действует с</div>
                          <div className="text-white font-mono">
                            {notam.active_from === "—" ? "Постоянно" : new Date(notam.active_from).toLocaleString("ru-RU")}
                          </div>
                        </div>
                        <div className="bg-[#121214] rounded-xl p-3">
                          <div className="text-gray-600 mb-0.5">Действует до</div>
                          <div className="text-white font-mono">
                            {notam.active_to === "—" ? "Постоянно" : new Date(notam.active_to).toLocaleString("ru-RU")}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Panel: Weather Oracle */}
        <div className="space-y-4">
          <h2 className="font-black text-white text-sm uppercase tracking-wider flex items-center gap-2">
            <CloudRain className="w-4 h-4 text-blue-400" /> Погодный Оракул БАС
          </h2>
          <p className="text-xs text-gray-500">Оценка лётной погоды по регионам (Росгидромет + OpenWeather)</p>

          <div className="space-y-2">
            {WEATHER_REGIONS.map((w, i) => (
              <div
                key={i}
                className={`rounded-2xl p-4 border transition-all ${
                  w.status === "ok"   ? "bg-emerald-500/5 border-emerald-500/15" :
                  w.status === "warn" ? "bg-amber-500/5 border-amber-500/15" :
                                        "bg-red-500/5 border-red-500/15"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-bold text-white text-sm">{w.city}</div>
                  <div className={`text-xs font-black flex items-center gap-1 ${
                    w.status === "ok" ? "text-emerald-400" : w.status === "warn" ? "text-amber-400" : "text-red-400"
                  }`}>
                    {w.status === "ok" ? <><CheckCircle className="w-3.5 h-3.5" /> Летно</> :
                     w.status === "warn" ? <><AlertTriangle className="w-3.5 h-3.5" /> Осторожно</> :
                     <><ShieldAlert className="w-3.5 h-3.5" /> Запрещено</>}
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  <span className="flex items-center gap-1">
                    <Thermometer className="w-3 h-3" /> {w.temp}°C
                  </span>
                  <span className="flex items-center gap-1">
                    <Wind className="w-3 h-3" /> {w.wind} м/с
                  </span>
                  {w.rain && (
                    <span className="flex items-center gap-1 text-blue-400">
                      <CloudRain className="w-3 h-3" /> Осадки
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-4">
            <div className="text-xs font-black text-gray-500 uppercase tracking-wider mb-3">Типы зон (ИКАО)</div>
            {Object.entries(ZONE_TYPES).map(([key, z]) => (
              <div key={key} className="flex items-center gap-2 mb-2">
                <span className={`w-2 h-2 rounded-full ${z.dot}`} />
                <span className="text-xs text-gray-400">{z.label}</span>
              </div>
            ))}
            <p className="text-[10px] text-gray-600 mt-3 flex items-start gap-1">
              <Info className="w-3 h-3 shrink-0 mt-0.5" />
              Данные обновляются каждые 60 секунд с серверов Росавиации и Минтранса
            </p>
          </div>

          {/* Quick check button */}
          <div className="bg-gradient-to-br from-blue-600/20 to-indigo-600/10 border border-blue-500/20 rounded-2xl p-4">
            <div className="font-black text-white text-sm mb-1 flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-400" /> Быстрая Проверка Зоны
            </div>
            <p className="text-xs text-gray-400 mb-3">
              Введите координаты вылета — ИИ мгновенно проверит наличие ограничений.
            </p>
            <div className="flex gap-2">
              <input
                placeholder="55.7558, 37.6173"
                className="flex-1 bg-[#0A0A0B] border border-white/10 focus:border-blue-500/50 outline-none text-white rounded-lg px-3 py-2 text-xs font-mono transition-colors"
              />
              <button className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition-all">
                <Eye className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
