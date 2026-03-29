"use client";

import { useRouter } from "next/navigation";
import { useState, FormEvent } from "react";
import { Search, MapPin, Filter, X } from "lucide-react";

export default function CatalogFilters({ currentParams }: { currentParams: Record<string, any> }) {
  const router = useRouter();
  
  const [q, setQ] = useState(currentParams.q || "");
  const [city, setCity] = useState(currentParams.city || "");
  const [categoryId, setCategoryId] = useState(currentParams.category_id || "");

  const categories = [
    { id: "", name: "Все категории" },
    { id: "1", name: "Аренда Дронов" },
    { id: "2", name: "Продажа БПЛА" },
    { id: "6", name: "Услуги Пилотов" },
    { id: "3", name: "Услуги Производств" }
  ];

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (city) params.set("city", city);
    if (categoryId) params.set("category_id", categoryId);
    
    router.push(`/catalog?${params.toString()}`);
  };

  const handleReset = () => {
    setQ("");
    setCity("");
    setCategoryId("");
    router.push("/catalog");
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 sticky top-24">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Filter className="w-5 h-5 text-blue-400" />
          Фильтры
        </h2>
        {(q || city || categoryId) && (
          <button onClick={handleReset} className="text-xs text-gray-400 hover:text-white transition-colors flex items-center">
            <X className="w-3 h-3 mr-1" /> Сбросить
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        
        {/* Search by name/desc */}
        <div>
          <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Поиск</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-500" />
            </div>
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Название или ключевое слово..."
              className="block w-full pl-10 pr-3 py-2.5 border border-white/10 rounded-xl leading-5 bg-[#0A0A0B] text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all shadow-inner"
            />
          </div>
        </div>

        {/* Category Radio Buttons */}
        <div>
          <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Направление</label>
          <div className="flex flex-col space-y-2">
            {categories.map((cat) => (
              <label key={cat.id} className="flex items-center group cursor-pointer">
                <div className="relative flex items-center justify-center w-5 h-5">
                  <input
                    type="radio"
                    name="category"
                    value={cat.id}
                    checked={categoryId === cat.id}
                    onChange={(e) => setCategoryId(e.target.value)}
                    className="peer sr-only"
                  />
                  <div className="w-4 h-4 rounded-full border border-gray-500 group-hover:border-blue-400 peer-checked:border-blue-500 transition-colors"></div>
                  <div className="absolute w-2 h-2 rounded-full bg-blue-500 scale-0 peer-checked:scale-100 transition-transform duration-200"></div>
                </div>
                <span className={`ml-3 text-sm transition-colors ${categoryId === cat.id ? "text-white font-medium" : "text-gray-400 group-hover:text-gray-300"}`}>
                  {cat.name}
                </span>
              </label>
            ))}
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
              className="block w-full pl-10 pr-3 py-2.5 border border-white/10 rounded-xl leading-5 bg-[#0A0A0B] text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all shadow-inner"
            />
          </div>
        </div>

        <div className="pt-2">
          <button
            type="submit"
            className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-sm shadow-blue-500/20 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0A0A0B] focus:ring-blue-500 transition-all hover:-translate-y-0.5"
          >
            Применить фильтры
          </button>
        </div>
      </form>
    </div>
  );
}
