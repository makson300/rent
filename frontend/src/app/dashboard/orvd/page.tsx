"use client";

import { useState } from "react";
import { Copy, Navigation, CheckCircle2, ShieldAlert } from "lucide-react";

export default function OrvdGenerator() {
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

  const handleCopy = () => {
    navigator.clipboard.writeText(generateTemplate());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
          <Navigation className="w-8 h-8 text-indigo-400" />
          Генератор Плана Полета (ИВП)
        </h1>
        <p className="text-gray-400 max-w-2xl">
          Автоматическое формирование заявки на Местный Режим Исполнения Воздушного Пространства (ЕС ОрВД). 
          Сформированный код необходимо отправить в систему SPPI или региональный зональный центр.
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

          <div className="mt-8 pt-6 border-t border-white/10">
            <div className="flex items-start gap-4 p-4 rounded-2xl bg-indigo-900/20 border border-indigo-500/20">
              <ShieldAlert className="w-6 h-6 text-indigo-400 shrink-0" />
              <p className="text-sm text-indigo-200/80">
                Заявка на местный режим должна подаваться не позднее чем за 3 суток до планируемого полета (если иное не предусмотрено правилами ЗЦ).
              </p>
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

            <button 
              onClick={handleCopy}
              className={`mt-6 w-full flex justify-center items-center py-3 px-4 border rounded-xl font-medium transition-all relative z-10 ${
                copied 
                  ? 'bg-emerald-500 border-emerald-500 text-white shadow-lg shadow-emerald-500/20' 
                  : 'bg-indigo-600 border-indigo-500 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-500/20'
              }`}
            >
              {copied ? (
                <>
                  <CheckCircle2 className="w-5 h-5 mr-2" /> Скопировано
                </>
              ) : (
                <>
                  <Copy className="w-5 h-5 mr-2" /> Скопировать для SPPI
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
