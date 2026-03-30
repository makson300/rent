"use client";

import { useState } from "react";
import {
  Warehouse, MapPin, Zap, Battery, Wifi, CheckCircle,
  Clock, ChevronRight, Lock, Plus, QrCode, AlertCircle,
  Globe2, TrendingUp, RefreshCw, Shield, Loader2
} from "lucide-react";
import { toast } from "react-hot-toast";
import { droneportApi } from "@/lib/api";

// --- Мок-данные дронопортов по России ---
const DRONEPORTS = [
  {
    id: "GRZ-DP-MSK-01",
    name: "Горизонт-Москва (МКАД 35)",
    city: "Москва",
    address: "МКАД, 35 км, промзона «Западный»",
    lat: 55.721, lng: 37.298,
    status: "online",
    slots: 4, occupied: 2,
    charge_speed: "140W Turbo",
    supports: ["Matrice 350", "DJI M30", "EVO II"],
    tariff_per_h: 850,
    distance_km: 12.4,
    weather: "ok",
  },
  {
    id: "GRZ-DP-MSK-02",
    name: "Горизонт-Химки (Промпарк)",
    city: "Москва",
    address: "г. Химки, Промышленный пр-д, 5",
    lat: 55.901, lng: 37.415,
    status: "online",
    slots: 6, occupied: 1,
    charge_speed: "200W Turbo+",
    supports: ["Matrice 350", "Геоскан 401", "Agras T50"],
    tariff_per_h: 1100,
    distance_km: 18.1,
    weather: "ok",
  },
  {
    id: "GRZ-DP-SPB-01",
    name: "Горизонт-СПБ (Колпино)",
    city: "Санкт-Петербург",
    address: "г. Колпино, Индустриальная улица, 9",
    lat: 59.744, lng: 30.586,
    status: "maintenance",
    slots: 4, occupied: 0,
    charge_speed: "140W Turbo",
    supports: ["DJI M30", "EVO II"],
    tariff_per_h: 700,
    distance_km: null,
    weather: "warn",
  },
  {
    id: "GRZ-DP-KZN-01",
    name: "Горизонт-Казань (Агропарк)",
    city: "Казань",
    address: "РТ, Пестречинский р-н, с. Богородское",
    lat: 55.896, lng: 49.432,
    status: "online",
    slots: 8, occupied: 3,
    charge_speed: "200W Turbo+",
    supports: ["Agras T50", "Геоскан Агро", "XAG V40"],
    tariff_per_h: 650,
    distance_km: null,
    weather: "ok",
  },
  {
    id: "GRZ-DP-KRD-01",
    name: "Горизонт-Краснодар (Агро-юг)",
    city: "Краснодар",
    address: "Краснодарский край, Тимашевский р-н",
    lat: 45.612, lng: 38.941,
    status: "coming_soon",
    slots: 12, occupied: 0,
    charge_speed: "200W Turbo+",
    supports: ["Agras T50", "XAG V40", "Геоскан Агро"],
    tariff_per_h: 600,
    distance_km: null,
    weather: "ok",
  },
];

const STATUS_MAP = {
  online:       { label: "Онлайн",    dot: "bg-emerald-400 animate-pulse", badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" },
  maintenance:  { label: "ТО",        dot: "bg-amber-400",                  badge: "bg-amber-500/10 text-amber-400 border-amber-500/30" },
  coming_soon:  { label: "Скоро",     dot: "bg-blue-400",                   badge: "bg-blue-500/10 text-blue-400 border-blue-500/30" },
  offline:      { label: "Офлайн",    dot: "bg-red-400",                    badge: "bg-red-500/10 text-red-400 border-red-500/30" },
};

type Droneport = typeof DRONEPORTS[0];

export default function DroneportsPage() {
  const [selected, setSelected] = useState<Droneport | null>(null);
  const [booking, setBooking] = useState(false);
  const [booked, setBooked] = useState<string[]>([]);
  const [filterCity, setFilterCity] = useState("Все");

  const CITIES = ["Все", "Москва", "Санкт-Петербург", "Казань", "Краснодар"];

  const filtered = DRONEPORTS.filter(d => filterCity === "Все" || d.city === filterCity);
  const onlineCount = DRONEPORTS.filter(d => d.status === "online").length;
  const totalSlots = DRONEPORTS.filter(d => d.status === "online").reduce((a, d) => a + d.slots, 0);
  const freeSlots = DRONEPORTS.filter(d => d.status === "online").reduce((a, d) => a + (d.slots - d.occupied), 0);

  const handleBook = async (port: Droneport) => {
    if (port.status !== "online") { toast.error("Дронопорт недоступен для бронирования"); return; }
    setBooking(true);
    try {
      const now = new Date();
      const slotFrom = now.toISOString();
      const slotTo = new Date(now.getTime() + 3600000).toISOString(); // +1 час
      await droneportApi.book({
        port_id: port.id,
        port_name: port.name,
        slot_from: slotFrom,
        slot_to: slotTo,
        tariff_per_h: port.tariff_per_h,
      });
      setBooked(prev => [...prev, port.id]);
      toast.success(`✅ Слот в «${port.name}» забронирован! QR отправлен в Telegram.`);
    } catch (err: unknown) {
      const e = err as { detail?: string };
      toast.error(e.detail ?? "Ошибка бронирования");
    } finally {
      setBooking(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-blue-500/15 text-blue-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Warehouse className="w-3.5 h-3.5" /> Фаза 47 · Hardware Инфраструктура
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Warehouse className="w-8 h-8 text-blue-400" />
          Сеть Дронопортов «Горизонт»
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Автоматизированные зарядные ангары для BVLOS-полётов по России.
          Зарезервируйте слот — дрон будет заряжен и готов к вылету по вашему расписанию.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {[
          { icon: <Globe2 className="w-4 h-4 text-blue-400" />,    label: "Всего портов",   val: DRONEPORTS.length },
          { icon: <Zap className="w-4 h-4 text-emerald-400" />,    label: "Онлайн",          val: onlineCount },
          { icon: <Battery className="w-4 h-4 text-amber-400" />,  label: "Свободных слотов",val: `${freeSlots} / ${totalSlots}` },
          { icon: <TrendingUp className="w-4 h-4 text-violet-400" />, label: "BVLOS-маршрутов",val: "14 активных" },
        ].map((s, i) => (
          <div key={i} className="bg-[#0E0E10] border border-white/5 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-1">{s.icon}<span className="text-xs text-gray-500">{s.label}</span></div>
            <div className="text-xl font-black text-white">{s.val}</div>
          </div>
        ))}
      </div>

      {/* City filter */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {CITIES.map(c => (
          <button key={c} onClick={() => setFilterCity(c)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${filterCity === c ? "bg-blue-600 text-white border-blue-500" : "bg-[#0E0E10] text-gray-400 border-white/10 hover:border-white/20"}`}>
            {c}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Droneport List */}
        <div className="lg:col-span-2 space-y-3">
          {filtered.map(port => {
            const st = STATUS_MAP[port.status as keyof typeof STATUS_MAP];
            const isBooked = booked.includes(port.id);
            const freeCount = port.slots - port.occupied;
            return (
              <div
                key={port.id}
                onClick={() => setSelected(selected?.id === port.id ? null : port)}
                className={`bg-[#0A0A0B] border rounded-2xl p-5 cursor-pointer transition-all ${selected?.id === port.id ? "border-blue-500/40 shadow-lg shadow-blue-500/10" : "border-white/5 hover:border-white/15"}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center shrink-0">
                      <Warehouse className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <div className="font-black text-white">{port.name}</div>
                      <div className="flex items-center gap-1 text-xs text-gray-500 mt-0.5">
                        <MapPin className="w-3 h-3" /> {port.address}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {port.distance_km && (
                      <span className="text-xs text-gray-500">{port.distance_km} км</span>
                    )}
                    <span className={`flex items-center gap-1.5 px-2 py-0.5 text-[11px] font-black rounded border ${st.badge}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} />
                      {st.label}
                    </span>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Battery className="w-3 h-3 text-amber-400" /> {port.charge_speed}
                  </span>
                  <span className="flex items-center gap-1">
                    <Warehouse className="w-3 h-3" />
                    <span className={freeCount === 0 ? "text-red-400" : freeCount <= 2 ? "text-amber-400" : "text-emerald-400"}>
                      {freeCount} свободно
                    </span>
                    <span>/ {port.slots} слотов</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Zap className="w-3 h-3 text-blue-400" /> {port.tariff_per_h} ₽/ч
                  </span>
                </div>

                {/* Slot bar */}
                <div className="flex gap-1 mt-3">
                  {Array.from({ length: port.slots }).map((_, i) => (
                    <div key={i} className={`flex-1 h-1.5 rounded-full ${i < port.occupied ? "bg-amber-500" : "bg-emerald-500/40"}`} />
                  ))}
                </div>

                {/* Expanded details */}
                {selected?.id === port.id && (
                  <div className="mt-4 pt-4 border-t border-white/5 space-y-3">
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Поддерживаемые платформы:</div>
                      <div className="flex flex-wrap gap-2">
                        {port.supports.map(s => (
                          <span key={s} className="px-2 py-0.5 text-xs bg-white/5 border border-white/10 text-gray-300 rounded-lg">{s}</span>
                        ))}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-[#121214] rounded-xl p-3">
                        <div className="text-gray-600 mb-0.5">ID порта</div>
                        <div className="text-white font-mono">{port.id}</div>
                      </div>
                      <div className="bg-[#121214] rounded-xl p-3">
                        <div className="text-gray-600 mb-0.5">Тариф</div>
                        <div className="text-white font-black">{port.tariff_per_h} ₽ / час</div>
                      </div>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleBook(port); }}
                      disabled={booking || port.status !== "online" || isBooked}
                      className={`w-full py-3 rounded-xl font-black text-sm transition-all flex items-center justify-center gap-2 ${
                        isBooked
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : port.status !== "online"
                          ? "bg-white/5 text-gray-600 cursor-not-allowed border border-white/5"
                          : "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20"
                      }`}
                    >
                      {booking ? <><Loader2 className="w-4 h-4 animate-spin" /> Бронирование...</> :
                       isBooked ? <><CheckCircle className="w-4 h-4" /> Забронировано</> :
                       port.status !== "online" ? <><Lock className="w-4 h-4" /> Недоступен</>  :
                       <><QrCode className="w-4 h-4" /> Забронировать слот</>}
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right Panel */}
        <div className="space-y-4">
          {/* How it works */}
          <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5">
            <h3 className="font-black text-white text-sm mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-400" /> Как это работает
            </h3>
            {[
              { n: "01", label: "Выберите Дронопорт", desc: "По маршруту BVLOS-полёта" },
              { n: "02", label: "Забронируйте слот",  desc: "По времени прибытия дрона" },
              { n: "03", label: "QR-разблокировка",   desc: "Ангар открывается автоматически" },
              { n: "04", label: "Зарядка 140–200W",   desc: "Быстрая зарядка за 35–55 мин" },
              { n: "05", label: "Вылет по расписанию",desc: "Автозакрытие ангара и отчёт" },
            ].map(step => (
              <div key={step.n} className="flex items-start gap-3 mb-3">
                <div className="w-6 h-6 rounded-full bg-blue-500/15 text-blue-400 text-[10px] font-black flex items-center justify-center shrink-0 mt-0.5">
                  {step.n}
                </div>
                <div>
                  <div className="text-sm font-bold text-white">{step.label}</div>
                  <div className="text-xs text-gray-500">{step.desc}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Opening promo */}
          <div className="bg-gradient-to-br from-blue-900/30 to-indigo-900/20 border border-blue-500/20 rounded-2xl p-5">
            <div className="font-black text-white mb-1 text-sm">🚀 Открытие Краснодара</div>
            <p className="text-xs text-gray-400 mb-3">Крупнейший агро-дронопорт на юге России: 12 слотов, Agras T50 + XAG V40. Q3 2026.</p>
            <button className="w-full py-2.5 bg-blue-600/30 hover:bg-blue-600/40 border border-blue-500/30 text-blue-400 text-xs font-black rounded-lg transition-all">
              Подписаться на открытие
            </button>
          </div>

          {/* Map placeholder */}
          <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5 text-center">
            <Globe2 className="w-8 h-8 text-gray-600 mx-auto mb-2" />
            <div className="text-sm text-gray-500 font-bold">Карта дронопортов</div>
            <div className="text-xs text-gray-600 mt-1">Интерактивная карта Leaflet интегрируется в Фазе 50</div>
          </div>
        </div>
      </div>
    </div>
  );
}
