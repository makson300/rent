"use client";

import { useState } from "react";
import { Scale, Plane, BookOpen, ShieldCheck, Building2 } from "lucide-react";
import OrvdTab from "./OrvdTab";
import RosaviatsiyaTab from "./RosaviatsiyaTab";
import LawsTab from "./LawsTab";
import EgrulTab from "./EgrulTab";

type Tab = "rosaviatsiya" | "orvd" | "laws" | "egrul";

export default function LegalHub() {
  const [activeTab, setActiveTab] = useState<Tab>("rosaviatsiya");

  const TABS: { id: Tab; label: string; icon: React.ReactNode; badge?: string }[] = [
    { id: "rosaviatsiya", label: "Учет в Росавиации", icon: <ShieldCheck className="w-4 h-4" /> },
    { id: "orvd",         label: "Местный Режим (ОрВД)", icon: <Plane className="w-4 h-4" /> },
    { id: "laws",         label: "База Законов", icon: <BookOpen className="w-4 h-4" /> },
    { id: "egrul",        label: "ЕГРЮЛ / Госуслуги Бизнес", icon: <Building2 className="w-4 h-4" />, badge: "Ф38" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 transition-all">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
          <Scale className="w-8 h-8 text-indigo-400" />
          Правовой Хаб Пилота
        </h1>
        <p className="text-gray-400 max-w-2xl">
          Комплексный инструмент для обеспечения полностью легальных полетов БВС в РФ.
          Ставьте дроны на учет, верифицируйте юр. лицо для B2G и изучайте законы в одном окне.
        </p>
      </div>

      <div className="flex space-x-1 border-b border-white/10 mb-8 overflow-x-auto print:hidden">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 font-medium text-sm flex items-center gap-2 border-b-2 whitespace-nowrap transition-colors relative ${
              activeTab === tab.id
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-gray-400 hover:text-white hover:border-white/30"
            }`}
          >
            {tab.icon}
            {tab.label}
            {tab.badge && (
              <span className="ml-1 px-1.5 py-0.5 text-[9px] font-black bg-amber-500/20 text-amber-400 rounded-md border border-amber-500/30">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="bg-[#121214] border border-white/5 rounded-2xl p-6 relative">
        {activeTab === "rosaviatsiya" && <RosaviatsiyaTab />}
        {activeTab === "orvd"         && <OrvdTab />}
        {activeTab === "laws"         && <LawsTab />}
        {activeTab === "egrul"        && <EgrulTab />}
      </div>
    </div>
  );
}
