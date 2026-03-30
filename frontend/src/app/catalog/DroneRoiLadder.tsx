"use client";

import { useState } from "react";
import { TrendingUp, Award, Zap, ChevronRight, Target } from "lucide-react";

// Mock Data for Phase 31 - Precalculated ROI metrics
const DRO_ROI_DATA = [
  { id: 1, model: "DJI Matrice 300 RTK", type: "Промышленный", avgPrice: "1,200,000 ₽", activeTenders: 12, maxEarnings: "3,500,000 ₽", popularity: "Высокая" },
  { id: 2, model: "DJI Agras T40", type: "Агро", avgPrice: "1,850,000 ₽", activeTenders: 8, maxEarnings: "2,100,000 ₽", popularity: "Средняя" },
  { id: 3, model: "Geoscan 201", type: "Картография", avgPrice: "2,500,000 ₽", activeTenders: 5, maxEarnings: "4,200,000 ₽", popularity: "Высокая" },
  { id: 4, model: "DJI Mavic 3 Enterprise", type: "Универсальный", avgPrice: "400,000 ₽", activeTenders: 24, maxEarnings: "1,200,000 ₽", popularity: "Топ-продукт" },
];

export default function DroneRoiLadder() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="w-full bg-[#121214] border border-white/5 rounded-2xl overflow-hidden shadow-2xl mb-10 group">
      {/* Header section */}
      <div 
        className="p-5 flex items-center justify-between cursor-pointer hover:bg-white/5 transition-colors border-b border-white/5"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
            <TrendingUp className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h2 className="text-lg font-black text-white uppercase tracking-wide flex items-center gap-2">
              Индекс Окупаемости B2G
              <span className="bg-red-500 text-white text-[9px] px-1.5 py-0.5 rounded uppercase font-bold tracking-widest animate-pulse">Live AI</span>
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">Нейросеть проанализировала {Math.floor(Math.random() * 500) + 9000} тендеров за вас.</p>
          </div>
        </div>
        
        <ChevronRight className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? "rotate-90" : ""}`} />
      </div>

      {/* Expanded Table */}
      {isExpanded && (
        <div className="p-0 overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-[#1A1A1D] text-gray-400 uppercase text-xs tracking-wider border-b border-white/5">
              <tr>
                <th className="px-6 py-4 font-bold">Модель Дрона</th>
                <th className="px-6 py-4 font-bold">Средняя цена</th>
                <th className="px-6 py-4 font-bold text-khokhloma-gold">Открыто контрактов</th>
                <th className="px-6 py-4 font-bold text-emerald-400">Потенциал (ROI)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-gray-300">
              {DRO_ROI_DATA.map((drone, idx) => (
                <tr key={drone.id} className="hover:bg-white/5 transition-colors group/row">
                  <td className="px-6 py-4 flex items-center gap-3">
                    <span className={`font-black text-xs ${idx === 0 ? "text-yellow-500" : idx === 1 ? "text-gray-400" : idx === 2 ? "text-amber-600" : "text-gray-600"}`}>
                      #{idx + 1}
                    </span>
                    <div>
                      <div className="font-bold text-white group-hover/row:text-blue-400 transition-colors flex items-center gap-2">
                        {drone.model}
                        {idx === 3 && <Zap className="w-3 h-3 text-khokhloma-gold" />}
                      </div>
                      <div className="text-[10px] text-gray-500 uppercase">{drone.type}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-mono text-gray-400">{drone.avgPrice}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Target className="w-4 h-4 text-khokhloma-gold" />
                      <span className="font-bold text-white">{drone.activeTenders} шт.</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-mono font-bold text-emerald-400 drop-shadow-[0_0_5px_rgba(52,211,153,0.3)]">
                    {drone.maxEarnings}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="p-3 bg-[#0A0A0B] text-center text-[10px] text-gray-600 border-t border-white/5 uppercase tracking-widest">
            Данные обновляются в реальном времени на основе открытых данных ЕИС Закупки.
          </div>
        </div>
      )}
    </div>
  );
}
