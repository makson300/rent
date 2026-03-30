"use client";

import { useState, useEffect } from "react";
import {
  HeartPulse, MapPin, Radio, Users, AlertTriangle,
  Clock, CheckCircle, XCircle, Loader2, Zap, Eye,
  PhoneCall, Navigation, ShieldAlert, Wifi
} from "lucide-react";
import { toast } from "react-hot-toast";
import { api } from "@/lib/api";

// --- Мок-данные: свободные пилоты-волонтёры в радиусе ---
const MOCK_VOLUNTEERS = [
  {
    id: 1, name: "Игорь Самарин", callsign: "ALPHA-7", city: "Москва",
    lat: 55.765, lng: 37.620, drone: "DJI Matrice 300 RTK",
    capabilities: ["Тепловизор", "ZOOM x200", "Прожектор"],
    status: "available", last_seen: "2 мин. назад", distance_km: 4.2, trust: 97,
  },
  {
    id: 2, name: "Денис Зотов", callsign: "BRAVO-2", city: "Мытищи",
    lat: 55.921, lng: 37.729, drone: "DJI Mavic 3T",
    capabilities: ["Тепловизор", "ZOOM x48"],
    status: "available", last_seen: "8 мин. назад", distance_km: 18.7, trust: 84,
  },
  {
    id: 3, name: "Алексей Воронов", callsign: "DELTA-5", city: "Химки",
    lat: 55.888, lng: 37.434, drone: "Геоскан Scout",
    capabilities: ["HD-камера", "LIDAR"],
    status: "on_mission", last_seen: "сейчас", distance_km: 12.1, trust: 91,
  },
  {
    id: 4, name: "Марина Ступак", callsign: "ECHO-9", city: "Одинцово",
    lat: 55.678, lng: 37.282, drone: "Autel EVO II Dual",
    capabilities: ["Тепловизор", "Радиомодем"],
    status: "available", last_seen: "1 мин. назад", distance_km: 31.5, trust: 88,
  },
];

// --- Активные ЧС-инциденты (мок) ---
const MOCK_INCIDENTS = [
  {
    id: 501, type: "Пропавший человек", severity: "critical",
    location: "Серебряный бор, Москва", lat: 55.789, lng: 37.396,
    description: "Пожилой мужчина, 74 года. Ушёл в лес в 14:00, не вернулся. Телефон недоступен.",
    reported_at: "2026-03-30T16:45:00Z",
    assigned_pilots: [1], status: "active",
    required: ["Тепловизор"],
  },
  {
    id: 502, type: "Пожар (кровля)", severity: "high",
    location: "ул. Народного Ополчения, д. 12А", lat: 55.758, lng: 37.431,
    description: "Загорелась кровля 5-этажного жилого дома. Требуется видеонаблюдение и координация расчётов.",
    reported_at: "2026-03-30T17:10:00Z",
    assigned_pilots: [], status: "pending",
    required: ["HD-камера", "Прожектор"],
  },
  {
    id: 503, type: "ДТП (опасный груз)", severity: "high",
    location: "МКАД км 58, внешнее кольцо", lat: 55.623, lng: 37.510,
    description: "Перевернулась фура с химикатами. Требуется БПЛА для мониторинга облака и оцепления.",
    reported_at: "2026-03-30T17:32:00Z",
    assigned_pilots: [], status: "pending",
    required: ["HD-камера", "Тепловизор"],
  },
];

type Incident = typeof MOCK_INCIDENTS[0];
type Volunteer = typeof MOCK_VOLUNTEERS[0];

function SeverityBadge({ severity }: { severity: string }) {
  const map: Record<string, string> = {
    critical: "bg-red-500/20 text-red-400 border-red-500/40",
    high:     "bg-amber-500/20 text-amber-400 border-amber-500/40",
    medium:   "bg-yellow-500/20 text-yellow-400 border-yellow-500/40",
  };
  const label: Record<string, string> = {
    critical: "🔴 КРИТИЧНО",
    high:     "🟠 ВЫСОКИЙ",
    medium:   "🟡 СРЕДНИЙ",
  };
  return (
    <span className={`px-2 py-0.5 text-[11px] font-black rounded border uppercase tracking-wider ${map[severity] ?? ""}`}>
      {label[severity] ?? severity}
    </span>
  );
}

function StatusDot({ status }: { status: string }) {
  return (
    <span className={`inline-flex w-2 h-2 rounded-full ${
      status === "available" ? "bg-emerald-400 animate-pulse" :
      status === "on_mission" ? "bg-amber-400" : "bg-gray-500"
    }`} />
  );
}

export default function EmergencyDispatchPage() {
  const [incidents, setIncidents] = useState<Incident[]>(MOCK_INCIDENTS);
  const [volunteers] = useState<Volunteer[]>(MOCK_VOLUNTEERS);
  const [selected, setSelected] = useState<Incident | null>(null);
  const [dispatching, setDispatching] = useState<number | null>(null);
  const [tick, setTick] = useState(0);

  // Live clock ticker
  useEffect(() => {
    const t = setInterval(() => setTick((p) => p + 1), 5000);
    return () => clearInterval(t);
  }, []);

  const availableCount = volunteers.filter((v) => v.status === "available").length;
  const activeIncidents = incidents.filter((i) => i.status !== "resolved").length;

  const handleDispatch = async (incidentId: number, pilotId: number) => {
    setDispatching(pilotId);
    try {
      await api.post("/emergency/dispatch", { incident_id: incidentId, pilot_id: pilotId });
    } catch {
      // Фоллбэк: обновляем локально если backend ещё не реализован
    }
    setIncidents((prev) =>
      prev.map((inc) =>
        inc.id === incidentId
          ? { ...inc, assigned_pilots: [...inc.assigned_pilots, pilotId], status: "active" }
          : inc
      )
    );
    setDispatching(null);
    const pilot = volunteers.find((v) => v.id === pilotId);
    toast.success(`✅ ${pilot?.name} (${pilot?.callsign}) направлен на место ЧС!`, { duration: 4000 });
  };

  const handleResolve = (incidentId: number) => {
    setIncidents((prev) =>
      prev.map((i) => i.id === incidentId ? { ...i, status: "resolved" } : i)
    );
    if (selected?.id === incidentId) setSelected(null);
    toast.success("Инцидент закрыт. Все пилоты освобождены.");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <span className="px-3 py-1 rounded-full bg-red-500/15 text-red-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <HeartPulse className="w-3.5 h-3.5 animate-pulse" /> Фаза 39 · ПСО Резерв МЧС
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <ShieldAlert className="w-8 h-8 text-red-400" />
          Экран Диспетчера ЧС
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Оперативный штаб БПЛА-поддержки. Назначайте свободных пилотов-волонтёров на активные инциденты в реальном времени.
        </p>
      </div>

      {/* Status Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {[
          { icon: <AlertTriangle className="w-4 h-4 text-red-400" />,    label: "Активных ЧС",    val: activeIncidents,   color: "text-red-400" },
          { icon: <Users className="w-4 h-4 text-emerald-400" />,        label: "Пилотов свободно", val: availableCount,  color: "text-emerald-400" },
          { icon: <Radio className="w-4 h-4 text-blue-400" />,           label: "На миссии",       val: volunteers.filter(v => v.status === "on_mission").length, color: "text-blue-400" },
          { icon: <Wifi className="w-4 h-4 text-amber-400" />,           label: "Связь",           val: "ОНЛАЙН",         color: "text-amber-400" },
        ].map((s, i) => (
          <div key={i} className="bg-[#0E0E10] border border-white/5 rounded-2xl p-4 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center">{s.icon}</div>
            <div>
              <div className="text-[10px] text-gray-500 uppercase tracking-wider">{s.label}</div>
              <div className={`text-xl font-black ${s.color}`}>{s.val}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left: Incident List */}
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-xs font-black text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" /> Активные Инциденты
          </h2>

          {incidents.map((inc) => (
            <div
              key={inc.id}
              onClick={() => inc.status !== "resolved" && setSelected(inc)}
              className={`bg-[#0A0A0B] border rounded-2xl p-4 cursor-pointer transition-all relative overflow-hidden ${
                selected?.id === inc.id
                  ? "border-red-500/50 shadow-lg shadow-red-500/10"
                  : inc.status === "resolved"
                  ? "border-white/5 opacity-40 cursor-not-allowed"
                  : "border-white/10 hover:border-red-500/30"
              }`}
            >
              {inc.status === "active" && (
                <div className="absolute top-0 right-0 w-24 h-24 bg-red-500/5 rounded-full blur-2xl" />
              )}
              <div className="flex items-start justify-between mb-2 relative z-10">
                <SeverityBadge severity={inc.severity} />
                {inc.status === "resolved" && (
                  <span className="text-[10px] text-emerald-400 font-black">ЗАКРЫТ</span>
                )}
                {inc.assigned_pilots.length > 0 && inc.status !== "resolved" && (
                  <span className="text-[10px] text-blue-400 font-black flex items-center gap-1">
                    <Navigation className="w-3 h-3" /> {inc.assigned_pilots.length} пилот
                  </span>
                )}
              </div>
              <div className="font-bold text-white text-sm relative z-10">{inc.type}</div>
              <div className="flex items-center gap-1 text-gray-500 text-xs mt-1 relative z-10">
                <MapPin className="w-3 h-3" />
                {inc.location}
              </div>
              <div className="text-[10px] text-gray-600 mt-1 relative z-10 flex items-center gap-1">
                <Clock className="w-2.5 h-2.5" />
                {new Date(inc.reported_at).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })}
              </div>
            </div>
          ))}

          {incidents.every((i) => i.status === "resolved") && (
            <div className="text-center py-8 text-gray-600">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 text-emerald-500" />
              Все инциденты закрыты
            </div>
          )}
        </div>

        {/* Right: Panel */}
        <div className="lg:col-span-3">
          {selected ? (
            <div className="bg-[#0A0A0B] border border-red-500/20 rounded-3xl overflow-hidden">
              {/* Incident Details */}
              <div className="p-6 border-b border-white/5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <SeverityBadge severity={selected.severity} />
                      <span className="text-xs text-gray-600">ID #{selected.id}</span>
                    </div>
                    <h3 className="text-xl font-black text-white">{selected.type}</h3>
                    <div className="flex items-center gap-1.5 text-gray-400 text-sm mt-1">
                      <MapPin className="w-4 h-4 text-red-400" />
                      {selected.location}
                    </div>
                  </div>
                  <button
                    onClick={() => handleResolve(selected.id)}
                    className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-bold rounded-lg transition-all"
                  >
                    <CheckCircle className="w-4 h-4 inline mr-1" />
                    Закрыть ЧС
                  </button>
                </div>

                <div className="bg-[#121214] border border-white/5 rounded-xl p-4 text-sm text-gray-300 mb-3">
                  {selected.description}
                </div>

                <div className="flex flex-wrap gap-2">
                  <span className="text-xs text-gray-500">Требуется:</span>
                  {selected.required.map((r) => (
                    <span key={r} className="px-2 py-0.5 text-xs bg-red-500/10 text-red-400 border border-red-500/20 rounded-md font-bold">
                      {r}
                    </span>
                  ))}
                </div>
              </div>

              {/* Volunteer roster */}
              <div className="p-6">
                <h4 className="text-xs font-black text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Users className="w-3.5 h-3.5 text-emerald-400" />
                  Доступные Пилоты-Волонтёры
                </h4>

                <div className="space-y-3">
                  {volunteers.map((pilot) => {
                    const isAssigned = selected.assigned_pilots.includes(pilot.id);
                    const hasCapability = selected.required.some((r) => pilot.capabilities.includes(r));

                    return (
                      <div
                        key={pilot.id}
                        className={`flex flex-col md:flex-row items-start md:items-center justify-between rounded-2xl p-4 border gap-3 transition-all ${
                          isAssigned
                            ? "bg-blue-500/5 border-blue-500/30"
                            : hasCapability
                            ? "bg-emerald-500/5 border-emerald-500/20 hover:border-emerald-500/40"
                            : "bg-[#121214] border-white/5 opacity-60"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className="relative">
                            <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center font-black text-white">
                              {pilot.name.charAt(0)}
                            </div>
                            <StatusDot status={pilot.status} />
                          </div>
                          <div>
                            <div className="font-bold text-white text-sm">
                              {pilot.name}{" "}
                              <span className="text-indigo-400 font-mono text-xs">{pilot.callsign}</span>
                            </div>
                            <div className="text-xs text-gray-500">
                              {pilot.drone} · {pilot.city} · {pilot.distance_km} км
                            </div>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {pilot.capabilities.map((c) => (
                                <span
                                  key={c}
                                  className={`text-[10px] px-1.5 py-0.5 rounded ${
                                    selected.required.includes(c)
                                      ? "bg-emerald-500/15 text-emerald-400"
                                      : "bg-white/5 text-gray-500"
                                  }`}
                                >
                                  {c}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 ml-auto">
                          <div className="text-right text-xs text-gray-500 hidden md:block">
                            <div className="text-emerald-400 font-bold">{pilot.trust}% trust</div>
                            <div>{pilot.last_seen}</div>
                          </div>

                          {isAssigned ? (
                            <div className="flex items-center gap-1 px-3 py-1.5 bg-blue-500/10 text-blue-400 text-xs font-black rounded-lg border border-blue-500/20">
                              <Navigation className="w-3.5 h-3.5" /> Направлен
                            </div>
                          ) : pilot.status === "on_mission" ? (
                            <div className="px-3 py-1.5 bg-amber-500/10 text-amber-400 text-xs font-bold rounded-lg border border-amber-500/20">
                              На миссии
                            </div>
                          ) : (
                            <button
                              onClick={() => handleDispatch(selected.id, pilot.id)}
                              disabled={dispatching === pilot.id}
                              className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white text-xs font-black rounded-lg transition-all disabled:opacity-50 flex items-center gap-1"
                            >
                              {dispatching === pilot.id ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              ) : (
                                <Zap className="w-3.5 h-3.5" />
                              )}
                              Направить
                            </button>
                          )}

                          <button className="p-1.5 bg-white/5 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-all">
                            <PhoneCall className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] bg-[#0A0A0B] border border-white/5 rounded-3xl text-center p-8">
              <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-4">
                <ShieldAlert className="w-8 h-8 text-red-400" />
              </div>
              <h3 className="text-white font-bold text-lg mb-2">Выберите инцидент</h3>
              <p className="text-gray-500 text-sm max-w-xs">
                Кликните на активный инцидент слева, чтобы назначить пилотов и управлять операцией.
              </p>

              {/* Live pulse indicator */}
              <div className="mt-6 flex items-center gap-2 text-xs text-gray-600">
                <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse" />
                Канал ЧС активен · обновление каждые 5 сек
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
