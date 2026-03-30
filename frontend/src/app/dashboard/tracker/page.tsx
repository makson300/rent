"use client";

import { useState } from "react";
import {
  Wifi, Plus, QrCode, CheckCircle, AlertTriangle, Loader2,
  Radio, MapPin, Battery, Shield, Zap, Copy, RefreshCw,
  Satellite, Clock, Link2, Activity
} from "lucide-react";
import { toast } from "react-hot-toast";
import { trackerApi, type Tracker as ApiTracker } from "@/lib/api";
import { useApiData } from "@/hooks/useApiData";

type TrackerStatus = "active" | "idle" | "offline" | "charging";

// Маппим поле is_active → локальный статус
function resolveStatus(t: ApiTracker): TrackerStatus {
  if (!t.is_active) return "offline";
  if (t.last_speed_kmh && t.last_speed_kmh > 1) return "active";
  return "idle";
}

const STATUS_CONFIG: Record<TrackerStatus, { dot: string; text: string; label: string }> = {
  active:   { dot: "bg-emerald-400 animate-pulse", text: "text-emerald-400", label: "В полёте" },
  idle:     { dot: "bg-blue-400",                  text: "text-blue-400",    label: "На стоянке" },
  offline:  { dot: "bg-gray-500",                  text: "text-gray-500",    label: "Офлайн" },
  charging: { dot: "bg-amber-400 animate-pulse",   text: "text-amber-400",   label: "Зарядка" },
};

export default function TrackerPage() {
  const { data: apiTrackers, loading: apiLoading, error: apiError, refetch } = useApiData(
    () => trackerApi.list()
  );

  const [showAdd, setShowAdd]   = useState(false);
  const [selected, setSelected] = useState<ApiTracker | null>(null);
  const [adding, setAdding]     = useState(false);

  // Фоллбэк к пустому списку если нет авторизации
  const trackers = apiTrackers ?? [];

  // Форма нового трекера
  const [newForm, setNewForm] = useState({ nickname: "", drone_model: "", serial: "" });

  const handleAdd = async () => {
    if (!newForm.serial || !newForm.drone_model) { toast.error("Заполните все поля"); return; }
    setAdding(true);
    try {
      const created = await trackerApi.register({
        nickname: newForm.nickname || newForm.drone_model,
        drone_model: newForm.drone_model,
        serial_number: newForm.serial,
      });
      refetch();
      setAdding(false);
      setShowAdd(false);
      setNewForm({ nickname: "", drone_model: "", serial: "" });
      toast.success(`✅ Квазар-ID ${created.tracker_id} зарегистрирован! Трекер виден в ЕС ОрВД.`);
    } catch (err: unknown) {
      const e = err as { detail?: string };
      setAdding(false);
      toast.error(e.detail ?? "Ошибка регистрации");
    }
  };  // end handleAdd

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Скопировано");
  };


  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-violet-500/15 text-violet-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Satellite className="w-3.5 h-3.5 animate-pulse" /> Фаза 48 · IoT Инфраструктура
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Radio className="w-8 h-8 text-violet-400" />
          Квазар-ID — ОрВД Трекер
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Привяжите любой дрон к трекеру «Квазар-ID» — и он станет<br />
          <span className="text-violet-400 font-bold">видимым в ЕС ОрВД</span> без отдельного ADS-B транспондера.
          Телеметрия в реальном времени, NOTAM-интеграция.
        </p>
      </div>

      {/* How-it-works banner */}
      <div className="bg-gradient-to-r from-violet-900/20 to-indigo-900/15 border border-violet-500/15 rounded-2xl p-5 mb-6 flex flex-col md:flex-row items-center gap-5">
        <div className="grid grid-cols-4 gap-4 flex-1">
          {[
            { icon: <Radio className="w-5 h-5 text-violet-400" />, label: "Трекер 30g",        desc: "Крепится на любой дрон" },
            { icon: <Satellite className="w-5 h-5 text-blue-400" />, label: "ГЛОНАСС/GPS",    desc: "±0.5м точность" },
            { icon: <Link2 className="w-5 h-5 text-emerald-400" />, label: "ЕС ОрВД Live",    desc: "Виден диспетчерам" },
            { icon: <Shield className="w-5 h-5 text-amber-400" />,  label: "ФАП совместим",   desc: "Юридическая чистота" },
          ].map((s, i) => (
            <div key={i} className="text-center">
              <div className="flex justify-center mb-1.5">{s.icon}</div>
              <div className="text-xs font-black text-white">{s.label}</div>
              <div className="text-[10px] text-gray-500">{s.desc}</div>
            </div>
          ))}
        </div>
        <button className="shrink-0 px-5 py-3 bg-violet-600 hover:bg-violet-500 text-white font-black rounded-xl transition-all text-sm whitespace-nowrap">
          Заказать Трекер — 3 490 ₽
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tracker List */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-black text-white flex items-center gap-2">
              <Radio className="w-4 h-4 text-gray-400" /> Мои Устройства ({trackers.length})
            </h2>
            <button
              onClick={() => setShowAdd(v => !v)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-violet-600 hover:bg-violet-500 text-white text-xs font-black rounded-lg transition-all"
            >
              <Plus className="w-3.5 h-3.5" /> Подключить
            </button>
          </div>

          {/* Add Form */}
          {showAdd && (
            <div className="bg-[#0A0A0B] border border-violet-500/25 rounded-2xl p-5 space-y-3">
              <div className="text-sm font-black text-white flex items-center gap-2">
                <QrCode className="w-4 h-4 text-violet-400" /> Регистрация нового Квазар-ID
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Псевдоним</label>
                  <input value={newForm.nickname} onChange={e => setNewForm(p => ({ ...p, nickname: e.target.value }))}
                    placeholder='«Мой Матрис»' className="w-full bg-[#121214] border border-white/10 focus:border-violet-500/50 outline-none text-white rounded-lg px-3 py-2 text-sm transition-colors" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Модель БВС *</label>
                  <input value={newForm.drone_model} onChange={e => setNewForm(p => ({ ...p, drone_model: e.target.value }))}
                    placeholder='DJI Matrice 350 RTK' className="w-full bg-[#121214] border border-white/10 focus:border-violet-500/50 outline-none text-white rounded-lg px-3 py-2 text-sm transition-colors" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Серийный номер *</label>
                  <input value={newForm.serial} onChange={e => setNewForm(p => ({ ...p, serial: e.target.value }))}
                    placeholder='1ZNBJ5F00201XX' className="w-full bg-[#121214] border border-white/10 focus:border-violet-500/50 outline-none text-white rounded-lg px-3 py-2 text-sm font-mono transition-colors" />
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={handleAdd} disabled={adding}
                  className="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-black text-sm rounded-lg disabled:opacity-50 flex items-center justify-center gap-2 transition-all">
                  {adding ? <><Loader2 className="w-4 h-4 animate-spin" /> Регистрация...</> : <><CheckCircle className="w-4 h-4" /> Зарегистрировать</>}
                </button>
                <button onClick={() => setShowAdd(false)} className="px-4 py-2.5 bg-white/5 text-gray-400 font-bold rounded-lg text-sm hover:bg-white/10 transition-all">
                  Отмена
                </button>
              </div>
            </div>
          )}

          {apiLoading && (
            <div className="flex items-center justify-center h-32 text-gray-500">
              <Loader2 className="w-6 h-6 animate-spin mr-2" /> Загрузка...
            </div>
          )}
          {apiError && !apiLoading && trackers.length === 0 && (
            <div className="flex items-center gap-2 text-amber-400 text-sm p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              Нет авторизации — войдите через Inв и зарегистрируйте приложение.
            </div>
          )}

          {trackers.map(t => {
            const st = STATUS_CONFIG[resolveStatus(t)];
            const batt = t.last_battery_pct ?? 0;
            return (
              <div
                key={t.tracker_id}
                onClick={() => setSelected(selected?.tracker_id === t.tracker_id ? null : t)}
                className={`bg-[#0A0A0B] border rounded-2xl p-5 cursor-pointer transition-all ${selected?.tracker_id === t.tracker_id ? "border-violet-500/40 shadow-lg shadow-violet-500/10" : "border-white/5 hover:border-white/15"}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center">
                        <Radio className="w-5 h-5 text-violet-400" />
                      </div>
                      <span className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-[#0A0A0B] ${st.dot}`} />
                    </div>
                    <div>
                      <div className="font-black text-white">{t.nickname}</div>
                      <div className="text-xs text-gray-500">{t.drone_model}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {t.orvd_visible && (
                      <span className="text-[10px] font-black text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                        ЕС ОрВД ✓
                      </span>
                    )}
                    <span className={`text-xs font-black ${st.text}`}>{st.label}</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                  <span className="font-mono text-gray-600">{t.tracker_id}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" />
                    {t.last_seen_at ? new Date(t.last_seen_at).toLocaleString("ru") : "Никогда"}
                  </span>
                  <span className="flex items-center gap-1"><Battery className="w-3 h-3" /> {batt}%</span>
                  {resolveStatus(t) === "active" && (
                    <>
                      <span className="flex items-center gap-1 text-blue-400"><Activity className="w-3 h-3" /> {t.last_altitude_m ?? 0} м</span>
                      <span className="flex items-center gap-1 text-violet-400"><Zap className="w-3 h-3" /> {t.last_speed_kmh ?? 0} км/ч</span>
                    </>
                  )}
                </div>

                {/* Battery bar */}
                <div className="mt-3 h-1 bg-white/5 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${batt > 50 ? "bg-emerald-500" : batt > 20 ? "bg-amber-500" : "bg-red-500"}`}
                    style={{ width: `${batt}%` }} />
                </div>

                {/* Expanded */}
                {selected?.tracker_id === t.tracker_id && (
                  <div className="mt-4 pt-4 border-t border-white/5 grid grid-cols-2 gap-2">
                    {[
                      { label: "Серийный номер", val: t.serial_number },
                      { label: "Регистрация",    val: t.registered_at.slice(0, 10) },
                      { label: "Координаты",    val: t.last_lat ? `${t.last_lat.toFixed(4)}, ${t.last_lng?.toFixed(4)}` : "Нет данных" },
                      { label: "Квазар-ID",      val: t.tracker_id },
                    ].map((f, i) => (
                      <div key={i} className="bg-[#121214] rounded-xl p-3 flex items-start justify-between gap-2">
                        <div>
                          <div className="text-[10px] text-gray-600">{f.label}</div>
                          <div className="text-xs text-white font-mono mt-0.5">{f.val}</div>
                        </div>
                        <button onClick={() => handleCopy(f.val)} className="text-gray-600 hover:text-gray-300 transition-colors shrink-0">
                          <Copy className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Active summary */}
          <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5">
            <h3 className="font-black text-white text-sm mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 text-violet-400" /> Общий Статус
            </h3>
            {[
              { label: "Устройств всего",    val: trackers.length,                                          color: "text-white" },
              { label: "В полёте сейчас",  val: trackers.filter(t => resolveStatus(t) === "active").length, color: "text-emerald-400" },
              { label: "Видимы ЕС ОрВД",   val: trackers.filter(t => t.orvd_visible).length,              color: "text-blue-400" },
              { label: "Требуют внимания", val: trackers.filter(t => (t.last_battery_pct ?? 100) < 20).length, color: "text-amber-400" },
            ].map((s, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-white/[0.03]">
                <span className="text-xs text-gray-400">{s.label}</span>
                <span className={`font-black text-sm ${s.color}`}>{s.val}</span>
              </div>
            ))}
          </div>

          {/* Pricing */}
          <div className="bg-[#0A0A0B] border border-violet-500/15 rounded-2xl p-5">
            <div className="font-black text-white text-sm mb-3 flex items-center gap-2">
              <QrCode className="w-4 h-4 text-violet-400" /> Квазар-ID Трекер
            </div>
            <div className="text-3xl font-black text-white mb-0.5">3 490 ₽</div>
            <div className="text-xs text-gray-500 mb-3">одноразовая покупка + 490 ₽/мес подписка</div>
            <ul className="text-xs text-gray-400 space-y-1.5 mb-4">
              {["Вес 28г + IP67 (защита от дождя)", "ГЛОНАСС + GPS двойной приёмник", "LTE 4G + LoRa резерв", "Автотрансляция в ЕС ОрВД", "Юридически действителен по ФАП-69"].map(f => (
                <li key={f} className="flex items-start gap-1.5"><CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" /> {f}</li>
              ))}
            </ul>
            <button className="w-full py-3 bg-violet-600 hover:bg-violet-500 text-white font-black rounded-xl text-sm transition-all">
              Заказать на Горизонт.Маркет
            </button>
          </div>

          <div className="bg-amber-500/5 border border-amber-500/20 rounded-2xl p-4">
            <p className="text-xs text-gray-400 leading-relaxed">
              <span className="text-amber-400 font-bold">⚠ Требование ФАП-69:</span>{" "}
              с 01.07.2023 все БПЛА {">"}250г, работающие на коммерческих заказах, обязаны иметь
              идентификатор в ЕС ОрВД. Квазар-ID полностью закрывает это требование.

            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
