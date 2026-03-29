"use client";

import { useState, useEffect } from "react";
import { Copy, Navigation, CheckCircle2, ShieldAlert, Save } from "lucide-react";

export default function OrvdTab() {
  const [copied, setCopied] = useState(false);
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

  const generateTemplate = () => {
    return `(SHR-UAS
-${formData.coords}0000
-${formData.altMin}/${formData.altMax}
-Z РАДИУС ${formData.radius} КМ
-${formData.timeStart}/${formData.timeEnd}
-ПОЛЕТЫ БПЛА ДЛЯ ${formData.task.toUpperCase()}
В ВЫДЕЛЕННОМ ВОЗДУШНОМ ПРОСТРАНСТВЕ.
ОПЕРАТОР: ${formData.operatorName.toUpperCase()}
ТЕЛ: ${formData.phone})`;
  };

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    // Get user id from localStorage session if possible
    const userStr = localStorage.getItem("skyrent_user");
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        setUserId(u.id);
      } catch (e) {}
    }
  }, []);

  const handleCopyAndSave = async () => {
    const shr_code = generateTemplate();
    navigator.clipboard.writeText(shr_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);

    if (userId) {
      setIsSubmitting(true);
      try {
        await fetch("http://127.0.0.1:8000/api/v1/flight_plans", {
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
            shr_code: shr_code,
            is_emergency: false,
          })
        });
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      } catch (e) {
        console.error("Failed to save plan", e);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <Navigation className="w-6 h-6 text-indigo-400" />
          Генератор Плана Полета (ИВП)
        </h2>
        <p className="text-gray-400 max-w-2xl text-sm">
          Автоматическое формирование заявки на Местный Режим Исполнения Воздушного Пространства (ЕС ОрВД). 
          Сформированный код необходимо отправить в систему SPPI или региональный зональный центр (не позднее чем за 3 суток).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Form Settings */}
        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl">
          <h2 className="text-xl font-bold text-white mb-6">Параметры полета</h2>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Координаты / Зона</label>
                <input
                  type="text"
                  value={formData.coords}
                  onChange={(e) => setFormData({...formData, coords: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-1 focus:ring-indigo-500 font-mono focus:outline-none"
                  placeholder="ZZZZ"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Радиус (КМ)</label>
                <input
                  type="number"
                  value={formData.radius}
                  onChange={(e) => setFormData({...formData, radius: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Высота Мин (М)</label>
                <input
                  type="text"
                  value={formData.altMin}
                  onChange={(e) => setFormData({...formData, altMin: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-1 focus:ring-indigo-500 font-mono focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Высота Макс (М)</label>
                <input
                  type="text"
                  value={formData.altMax}
                  onChange={(e) => setFormData({...formData, altMax: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-1 focus:ring-indigo-500 font-mono focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Время начала (UTC)</label>
                <input
                  type="text"
                  value={formData.timeStart}
                  onChange={(e) => setFormData({...formData, timeStart: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-1 focus:ring-indigo-500 font-mono focus:outline-none"
                  placeholder="0000"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Время окончания (UTC)</label>
                <input
                  type="text"
                  value={formData.timeEnd}
                  onChange={(e) => setFormData({...formData, timeEnd: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-1 focus:ring-indigo-500 font-mono focus:outline-none"
                  placeholder="0000"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Цель полета</label>
              <input
                type="text"
                value={formData.task}
                onChange={(e) => setFormData({...formData, task: e.target.value})}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-indigo-500 focus:outline-none uppercase"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">ФИО Оператора</label>
                <input
                  type="text"
                  value={formData.operatorName}
                  onChange={(e) => setFormData({...formData, operatorName: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Контактный телефон</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Live Preview */}
        <div>
          <h2 className="text-xl font-bold text-white mb-6">Код заявки SHR</h2>
          <div className="bg-[#0A0A0B] border border-white/10 rounded-3xl p-6 relative group overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full mix-blend-screen filter blur-3xl" />
            
            <pre className="font-mono text-indigo-300 text-sm whitespace-pre-wrap leading-relaxed relative z-10">
              {generateTemplate()}
            </pre>

            <div className="flex flex-col gap-3 mt-6">
              <button 
                onClick={handleCopyAndSave}
                disabled={isSubmitting}
                className={`w-full flex justify-center items-center py-3 px-4 rounded-xl font-medium transition-all ${
                  copied 
                    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' 
                    : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-500/20'
                } relative z-10 disabled:opacity-50`}
              >
                {copied ? (
                  <>
                    <CheckCircle2 className="w-5 h-5 mr-2" /> Скопировано и Сохранено
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5 mr-2" /> Отправить в ОрВД
                  </>
                )}
              </button>
              
              {saveSuccess && (
                <p className="text-emerald-400 text-sm text-center font-medium">✅ Заявка сохранена в базе (Статус: Ожидание)</p>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
