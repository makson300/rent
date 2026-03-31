"use client";

import React, { useEffect, useState } from "react";
import { Shield, Clock, Target, Award, Activity, Search, BrainCircuit } from "lucide-react";

interface PilotTwin {
  id: number;
  user_id: number;
  total_flight_hours: number;
  total_missions: number;
  safety_score: number;
  success_rate: number;
  momoa_grade: string;
  skills_json?: string;
}

export default function PilotTwinsPage() {
  const [twins, setTwins] = useState<PilotTwin[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // В реальности здесь фетч данных API:
    // fetch('/api/v1/twins', { headers: { 'X-Telegram-Id': user.id } })
    // А пока для демо/MVP просто генерируем моковые данные (Цифровые Двойники)
    
    setTimeout(() => {
        setTwins([
            { id: 1, user_id: 101, total_flight_hours: 450.5, total_missions: 124, safety_score: 99.8, success_rate: 98.5, momoa_grade: "A+" },
            { id: 2, user_id: 105, total_flight_hours: 120.0, total_missions: 30, safety_score: 95.0, success_rate: 90.0, momoa_grade: "B" },
            { id: 3, user_id: 112, total_flight_hours: 890.2, total_missions: 310, safety_score: 100.0, success_rate: 99.9, momoa_grade: "S" },
            { id: 4, user_id: 119, total_flight_hours: 45.0, total_missions: 12, safety_score: 88.0, success_rate: 85.0, momoa_grade: "C" },
        ]);
        setLoading(false);
    }, 800);
  }, []);

  const getGradeColor = (grade: string) => {
    switch(grade) {
        case 'S': return 'text-purple-400 border-purple-400 drop-shadow-[0_0_8px_rgba(168,85,247,0.8)]';
        case 'A+': return 'text-khokhloma-gold border-khokhloma-gold drop-shadow-[0_0_8px_rgba(255,215,0,0.8)]';
        case 'B': return 'text-blue-400 border-blue-400';
        case 'C': return 'text-orange-400 border-orange-400';
        default: return 'text-gray-400 border-gray-400';
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in pb-32">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <h1 className="text-3xl font-black flex items-center gap-3">
                    <Shield className="w-8 h-8 text-khokhloma-gold" />
                    Цифровые Двойники Пилотов
                </h1>
                <p className="text-gray-400 mt-2 max-w-2xl">
                    Инструмент для B2B/B2G заказчиков: база верифицированных пилотов с детальной AI-аналитикой (MoMoA) их работы, статистики полётов и рейтинга безопасности.
                </p>
            </div>
            
            <div className="flex bg-[#121214] border border-white/10 rounded-xl px-4 py-2 items-center w-full md:w-auto">
                <Search className="w-5 h-5 text-gray-500 mr-2" />
                <input 
                    type="text" 
                    placeholder="Поиск по ID двойника..." 
                    className="bg-transparent border-none outline-none text-white w-full md:w-64"
                />
            </div>
        </header>

        {loading ? (
            <div className="flex justify-center items-center py-20">
                <div className="w-10 h-10 border-4 border-khokhloma-gold border-t-transparent rounded-full animate-spin"></div>
            </div>
        ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {twins.map((twin) => (
                    <div key={twin.id} className="bg-[#121214] rounded-2xl border border-white/5 overflow-hidden hover:border-khokhloma-gold/30 transition-colors group">
                        
                        {/* Header Box */}
                        <div className="p-5 border-b border-white/5 flex justify-between items-start bg-gradient-to-br from-white/[0.02] to-transparent">
                            <div>
                                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                    Пилот #{twin.user_id}
                                    <div className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-500/20 text-green-400 border border-green-500/30">
                                        Верифицирован
                                    </div>
                                </h3>
                                <p className="text-sm text-gray-500 mt-1">Twin ID: {twin.id}</p>
                            </div>
                            
                            <div className={`flex flex-col items-center justify-center w-12 h-12 rounded-xl border-2 font-black text-xl bg-black/50 ${getGradeColor(twin.momoa_grade)}`}>
                                {twin.momoa_grade}
                            </div>
                        </div>

                        {/* Stats Box */}
                        <div className="p-5 space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-black/30 p-3 rounded-xl border border-white/5">
                                    <div className="flex items-center text-gray-400 text-xs mb-1">
                                        <Clock className="w-3 h-3 mr-1" /> Налёт
                                    </div>
                                    <div className="text-lg font-bold text-white">{twin.total_flight_hours} <span className="text-sm font-normal text-gray-500">ч</span></div>
                                </div>
                                <div className="bg-black/30 p-3 rounded-xl border border-white/5">
                                    <div className="flex items-center text-gray-400 text-xs mb-1">
                                        <Target className="w-3 h-3 mr-1" /> Миссии
                                    </div>
                                    <div className="text-lg font-bold text-white">{twin.total_missions}</div>
                                </div>
                            </div>
                            
                            <div className="space-y-3 pt-2">
                                <div>
                                    <div className="flex justify-between text-xs mb-1">
                                        <span className="text-gray-400 flex items-center gap-1"><Activity className="w-3 h-3" /> Индекс безопасности</span>
                                        <span className="text-white font-bold">{twin.safety_score}%</span>
                                    </div>
                                    <div className="w-full bg-black/50 rounded-full h-1.5 overflow-hidden">
                                        <div className="bg-gradient-to-r from-khokhloma-red to-khokhloma-gold h-1.5 rounded-full" style={{ width: `${twin.safety_score}%` }}></div>
                                    </div>
                                </div>

                                <div>
                                    <div className="flex justify-between text-xs mb-1">
                                        <span className="text-gray-400 flex items-center gap-1"><Award className="w-3 h-3" /> Успешность контрактов</span>
                                        <span className="text-white font-bold">{twin.success_rate}%</span>
                                    </div>
                                    <div className="w-full bg-black/50 rounded-full h-1.5 overflow-hidden">
                                        <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${twin.success_rate}%` }}></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div className="p-4 border-t border-white/5 bg-black/30 flex gap-3">
                            <button className="flex-1 bg-white/5 hover:bg-white/10 text-white text-sm font-bold py-2 rounded-xl transition-colors">
                                Профиль
                            </button>
                            <button className="flex-1 bg-khokhloma-red hover:bg-red-600 text-white text-sm font-bold py-2 rounded-xl transition-colors shadow-lg shadow-red-500/20 flex items-center justify-center gap-2">
                                <BrainCircuit className="w-4 h-4" /> Утвердить
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        )}
    </div>
  );
}
