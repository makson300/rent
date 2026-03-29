"use client";

import { useState } from "react";
import { Scale, Plane, BookOpen, ShieldCheck } from "lucide-react";
import OrvdTab from "./OrvdTab";
import RosaviatsiyaTab from "./RosaviatsiyaTab";
import LawsTab from "./LawsTab";

export default function LegalHub() {
  const [activeTab, setActiveTab] = useState<"rosaviatsiya" | "orvd" | "laws">("rosaviatsiya");

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 transition-all">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
          <Scale className="w-8 h-8 text-indigo-400" />
          Правовой Хаб Пилота
        </h1>
        <p className="text-gray-400 max-w-2xl">
          Комплексный инструмент для обеспечения полностью легальных полетов БВС в РФ. 
          Ставьте дроны на учет, получайте разрешения на полеты и изучайте законы в одном окне.
        </p>
      </div>

      <div className="flex space-x-2 border-b border-white/10 mb-8 overflow-x-auto print:hidden">
        <button
          onClick={() => setActiveTab("rosaviatsiya")}
          className={`px-4 py-3 font-medium text-sm flex items-center gap-2 border-b-2 whitespace-nowrap transition-colors ${
            activeTab === "rosaviatsiya"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-gray-400 hover:text-white hover:border-white/30"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Учет в Росавиации
        </button>
        <button
          onClick={() => setActiveTab("orvd")}
          className={`px-4 py-3 font-medium text-sm flex items-center gap-2 border-b-2 whitespace-nowrap transition-colors ${
            activeTab === "orvd"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-gray-400 hover:text-white hover:border-white/30"
          }`}
        >
          <Plane className="w-4 h-4" />
          Местный Режим (ОрВД)
        </button>
        <button
          onClick={() => setActiveTab("laws")}
          className={`px-4 py-3 font-medium text-sm flex items-center gap-2 border-b-2 whitespace-nowrap transition-colors ${
            activeTab === "laws"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-gray-400 hover:text-white hover:border-white/30"
          }`}
        >
          <BookOpen className="w-4 h-4" />
          База Законов
        </button>
      </div>

      <div className="bg-[#121214] border border-white/5 rounded-2xl p-6 relative">
        {activeTab === "rosaviatsiya" && <RosaviatsiyaTab />}
        {activeTab === "orvd" && <OrvdTab />}
        {activeTab === "laws" && <LawsTab />}
      </div>
    </div>
  );
}
