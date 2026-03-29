"use client";

import { useState, useEffect } from "react";
import { Copy, Navigation, CheckCircle2, Save, MapPin, Clock, RefreshCw } from "lucide-react";
import { toast } from "react-hot-toast";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

const STATUS_LABELS: Record<string, { text: string; color: string }> = {
  pending:  { text: "⏳ Ожидание",  color: "text-yellow-400" },
  approved: { text: "✅ Одобрено",   color: "text-emerald-400" },
  rejected: { text: "❌ Отклонено",  color: "text-red-400" },
  draft:    { text: "📝 Черновик",   color: "text-gray-400" },
};

interface FlightPlan {
  id: number;
  coords: string;
  radius: string;
  task_desc: string;
  status: string;
  created_at: string;
  is_emergency: boolean;
}

export default function OrvdTab() {
  const [formData, setFormData] = useState({
    coords: "ZZZZ",
    radius: "1",
    altMin: "M0000",
    altMax: "M0015",
    timeStart: "0000",
    timeEnd: "0000",
    task: "АЭРОФОТОСЪЕМКА",
    operatorName: "ИВАНОВ И.И.",
    phone: "+79990000000",
  });

  const [geoStatus, setGeoStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [latLng, setLatLng] = useState<{ lat: number; lng: number } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [myPlans, setMyPlans] = useState<FlightPlan[]>([]);
  const [userId, setUserId] = useState<number | null>(null);
  const [loadingPlans, setLoadingPlans] = useState(false);

  const generateTemplate = () => `(SHR-UAS
-${formData.coords}0000
-${formData.altMin}/${formData.altMax}
-Z РАДИУС ${formData.radius} КМ
-${formData.timeStart}/${formData.timeEnd}
-ПОЛЕТЫ БПЛА ДЛЯ ${formData.task.toUpperCase()}
В ВЫДЕЛЕННОМ ВОЗДУШНОМ ПРОСТРАНСТВЕ.
ОПЕРАТОР: ${formData.operatorName.toUpperCase()}
ТЕЛ: ${formData.phone})`;

  useEffect(() => {
    const userStr = localStorage.getItem("skyrent_user");
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        setUserId(u.telegram_id || u.id);
      } catch {}
    }
  }, []);

  useEffect(() => {
    if (userId) fetchMyPlans();
  }, [userId]);

  const fetchMyPlans = async () => {
    if (!userId) return;
    setLoadingPlans(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/my_flight_plans/${userId}`);
      if (res.ok) setMyPlans(await res.json());
    } catch {
      // Silent fail — user may be offline
    } finally {
      setLoadingPlans(false);
    }
  };

  const requestGeolocation = () => {
    if (!navigator.geolocation) {
      toast.error("Браузер не поддерживает геолокацию");
      return;
    }
    setGeoStatus("loading");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setLatLng({ lat, lng });
        // Convert to ICAO-style coords for the SHR code field
        const latStr = `${Math.abs(lat).toFixed(4)}${lat >= 0 ? "N" : "S"}`;
        const lngStr = `${Math.abs(lng).toFixed(4)}${lng >= 0 ? "E" : "W"}`;
        setFormData(f => ({ ...f, coords: `${latStr}${lngStr}` }));
        setGeoStatus("done");
        toast.success("Координаты определены!");
      },
      () => {
        setGeoStatus("error");
        toast.error("Не удалось определить геолокацию. Введите координаты вручную.");
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const handleSubmit = async () => {
    const shr_code = generateTemplate();

    // Copy to clipboard
    try { navigator.clipboard.writeText(shr_code); } catch {}

    if (!userId) {
      toast.error("Войдите через бота, чтобы сохранить заявку");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/flight_plans`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          coords: formData.coords,
          radius: formData.radius,
          alt_min: formData.altMin,
          alt_max: formData.altMax,
          time_start: formData.timeStart,
          time_end: formData.timeEnd,
          task_desc: formData.task,
          operator_name: formData.operatorName,
          phone: formData.phone,
          shr_code,
          is_emergency: false,
          lat: latLng?.lat ?? null,
          lng: latLng?.lng ?? null,
        }),
      });

      if (res.ok) {
        toast.success("✅ Заявка отправлена на проверку! Ожидайте подтверждения.");
        await fetchMyPlans();
      } else {
        const err = await res.json();
        toast.error(`Ошибка: ${err.error || "Не удалось сохранить"}`);
      }
    } catch (e) {
      toast.error("Сервер недоступен. Проверьте подключение.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <Navigation className="w-6 h-6 text-indigo-400" />
          Генератор Плана Полета (ИВП)
        </h2>
        <p className="text-gray-400 max-w-2xl text-sm">
          Автоматическое формирование заявки на Местный Режим ИВП (ЕС ОрВД).
          После отправки администратор проверит заявку и уведомит вас.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl space-y-4">
          <h3 className="text-lg font-bold text-white">Параметры полета</h3>

          {/* Geolocation button */}
          <button
            onClick={requestGeolocation}
            disabled={geoStatus === "loading"}
            className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition-all border ${
              geoStatus === "done"
                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                : geoStatus === "error"
                ? "bg-red-500/10 border-red-500/30 text-red-400"
                : "bg-indigo-500/10 border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/20"
            }`}
          >
            <MapPin className="w-4 h-4" />
            {geoStatus === "loading" ? "Определяем..." :
             geoStatus === "done" ? `📍 ${latLng?.lat.toFixed(4)}, ${latLng?.lng.toFixed(4)}` :
             geoStatus === "error" ? "Ошибка геолокации" :
             "Определить местоположение"}
          </button>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Координаты / Зона</label>
              <input type="text" value={formData.coords}
                onChange={e => setFormData({ ...formData, coords: e.target.value })}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white font-mono focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Радиус (КМ)</label>
              <input type="number" value={formData.radius}
                onChange={e => setFormData({ ...formData, radius: e.target.value })}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Высота Мин (М)</label>
              <input type="text" value={formData.altMin}
                onChange={e => setFormData({ ...formData, altMin: e.target.value })}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white font-mono focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Высота Макс (М)</label>
              <input type="text" value={formData.altMax}
                onChange={e => setFormData({ ...formData, altMax: e.target.value })}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white font-mono focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Время начала (UTC)</label>
              <input type="text" value={formData.timeStart} placeholder="0000"
                onChange={e => setFormData({ ...formData, timeStart: e.target.value })}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white font-mono focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Время окончания (UTC)</label>
              <input type="text" value={formData.timeEnd} placeholder="0000"
                onChange={e => setFormData({ ...formData, timeEnd: e.target.value })}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white font-mono focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Цель полета</label>
            <input type="text" value={formData.task}
              onChange={e => setFormData({ ...formData, task: e.target.value })}
              className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white uppercase focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">ФИО Оператора</label>
              <input type="text" value={formData.operatorName}
                onChange={e => setFormData({ ...formData, operatorName: e.target.value })}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Контактный телефон</label>
              <input type="text" value={formData.phone}
                onChange={e => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
            </div>
          </div>
        </div>

        {/* Preview + Submit */}
        <div className="space-y-6">
          <div className="bg-[#0A0A0B] border border-white/10 rounded-3xl p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full mix-blend-screen filter blur-3xl" />
            <h3 className="text-lg font-bold text-white mb-4">Код заявки SHR</h3>
            <pre className="font-mono text-indigo-300 text-sm whitespace-pre-wrap leading-relaxed relative z-10">
              {generateTemplate()}
            </pre>

            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="w-full mt-6 flex justify-center items-center py-3 px-4 rounded-xl font-medium transition-all bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/20 disabled:opacity-50 relative z-10"
            >
              {isSubmitting
                ? <><RefreshCw className="w-4 h-4 mr-2 animate-spin" /> Отправляем...</>
                : <><Save className="w-5 h-5 mr-2" /> Отправить заявку в ОрВД</>
              }
            </button>
          </div>

          {/* My Plans */}
          <div className="bg-white/5 border border-white/10 rounded-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-indigo-400" /> Мои заявки
              </h3>
              <button onClick={fetchMyPlans} className="text-gray-500 hover:text-white transition-colors">
                <RefreshCw className={`w-4 h-4 ${loadingPlans ? "animate-spin" : ""}`} />
              </button>
            </div>

            {myPlans.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-4">
                {userId ? "Заявок пока нет" : "Войдите через бота для просмотра"}
              </p>
            ) : (
              <div className="space-y-3">
                {myPlans.map(p => (
                  <div key={p.id} className="bg-[#0A0A0B] border border-white/5 rounded-xl p-4">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-white text-sm font-medium">ИВП #{p.id} — {p.coords}</span>
                      <span className={`text-xs font-semibold ${STATUS_LABELS[p.status]?.color || "text-gray-400"}`}>
                        {STATUS_LABELS[p.status]?.text || p.status}
                      </span>
                    </div>
                    <p className="text-gray-500 text-xs">{p.task_desc} · R={p.radius}км</p>
                    <p className="text-gray-600 text-xs mt-1">
                      {new Date(p.created_at).toLocaleDateString("ru-RU")}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
