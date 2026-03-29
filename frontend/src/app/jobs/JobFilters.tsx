"use client";

import { useRouter } from "next/navigation";
import { useState, FormEvent } from "react";
import { Search, MapPin, Filter, X } from "lucide-react";

export default function JobFilters({ currentParams }: { currentParams: Record<string, any> }) {
  const router = useRouter();
  
  const [q, setQ] = useState(currentParams.q || "");
  const [city, setCity] = useState(currentParams.city || "");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (city) params.set("city", city);
    
    router.push(`/jobs?${params.toString()}`);
  };

  const handleReset = () => {
    setQ("");
    setCity("");
    router.push("/jobs");
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 sticky top-24">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Filter className="w-5 h-5 text-emerald-400" />
          Фильтры
        </h2>
        {(q || city) && (
          <button onClick={handleReset} className="text-xs text-gray-400 hover:text-white transition-colors flex items-center">
            <X className="w-3 h-3 mr-1" /> Сбросить
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        
        {/* Search by keyword */}
        <div>
          <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Ключевое слово</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-500" />
            </div>
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Например: Аэрофотосъемка"
              className="block w-full pl-10 pr-3 py-2.5 border border-white/10 rounded-xl leading-5 bg-[#0A0A0B] text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm transition-all shadow-inner"
            />
          </div>
        </div>

        {/* City Filter */}
        <div>
          <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Город</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MapPin className="h-4 w-4 text-gray-500" />
            </div>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Например: Москва"
              className="block w-full pl-10 pr-3 py-2.5 border border-white/10 rounded-xl leading-5 bg-[#0A0A0B] text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm transition-all shadow-inner"
            />
          </div>
        </div>

        <div className="pt-2">
          <button
            type="submit"
            className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-sm shadow-emerald-500/20 text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0A0A0B] focus:ring-emerald-500 transition-all hover:-translate-y-0.5"
          >
            Найти заказы
          </button>
        </div>
      </form>
    </div>
  );
}
