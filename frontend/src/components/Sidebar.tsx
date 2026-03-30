"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Home, 
  ShoppingCart, 
  Briefcase, 
  Map, 
  GraduationCap, 
  ShieldAlert, 
  FileText, 
  UserCircle,
  Scale,
  Settings,
  Target,
  Plane,
  HeartPulse,
  Wallet,
  Star
} from "lucide-react";

// Nav item type (Фаза 29.3 + 35)
type NavItem = {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  theme: "khokhloma" | "tricolor";
  pulse?: boolean;
  emergency?: boolean;
};

type NavGroup = { title: string; items: NavItem[] };

const NAV_GROUPS: NavGroup[] = [
  {
    title: "Коммерция (B2B)",
    items: [
      { name: "Радар Защиты & B2G", href: "/dashboard/radar", icon: Target, theme: "khokhloma" },
      { name: "Мои Тендеры", href: "/dashboard/tenders", icon: Briefcase, theme: "tricolor" },
      { name: "Маркетплейс Аренды", href: "/catalog", icon: ShoppingCart, theme: "khokhloma" },
      { name: "Франшиза 'Горизонт'", href: "/franchise", icon: Map, theme: "khokhloma" },
    ]
  },
  {
    title: "Авиа-Утилиты",
    items: [
      { name: "Центр Полетов (ОрВД)", href: "/dashboard/pilot/telemetry", icon: Plane, theme: "tricolor" },
      { name: "Кошелек & КАСКО", href: "/wallet", icon: Wallet, theme: "khokhloma", pulse: true },
      { name: "Реестр и Обучение", href: "/education", icon: GraduationCap, theme: "tricolor" },
    ]
  },
  {
    title: "Резерв МЧС 🚨",
    items: [
      { name: "Штаб Спасения (ПСО)", href: "/dashboard/radar?filter=emergency", icon: HeartPulse, theme: "khokhloma", emergency: true },
    ]
  },
  {
    title: "Управление",
    items: [
      { name: "Профиль Пилота", href: "/dashboard/pilot/profile", icon: Star, theme: "khokhloma" },
      { name: "Верификация Юр. Лица", href: "/dashboard/legal", icon: Scale, theme: "tricolor" },
      { name: "Панель Администратора", href: "https://45.12.5.177.nip.io/", icon: Settings, theme: "tricolor" },
      { name: "На Главную", href: "/", icon: Home, theme: "khokhloma" },
    ]
  }
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[280px] bg-[#0A0A0B]/95 border-r border-white/5 h-screen sticky top-0 flex flex-col hidden lg:flex shrink-0 z-50">
      
      {/* Логотип */}
      <div className="h-24 flex items-center px-6 border-b border-white/5 relative overflow-hidden group shrink-0">
        <div className="absolute top-0 right-0 w-24 h-full bg-khokhloma-red/30 blur-[40px] transition-all duration-700 group-hover:bg-khokhloma-gold/30 group-hover:w-32"></div>
        <div className="relative z-10 flex flex-col transform transition-transform duration-300">
          <Link href="/" className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-khokhloma-gold via-[#ffdd55] to-khokhloma-red flex items-center gap-2 tracking-tighter hover:scale-105 transition-transform">
            ГОРИЗОНТ <span className="drop-shadow-none text-xl">🇷🇺</span>
          </Link>
          <span className="text-[10px] font-bold tracking-[0.2em] text-gray-500 uppercase mt-1">
            Единое Окно БАС
          </span>
        </div>
      </div>

      {/* Навигация */}
      <nav className="flex-1 px-4 py-6 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        <div className="space-y-8">
          {NAV_GROUPS.map((group, groupIdx) => (
            <div key={groupIdx} className="space-y-3">
              <h3 className="text-[10px] font-black tracking-[0.15em] text-gray-500 uppercase px-2 mb-2 flex items-center gap-2">
                {group.title}
                <div className="h-[1px] flex-1 bg-white/5"></div>
              </h3>
              
              <div className="space-y-1.5 flex flex-col">
                {group.items.map((item) => {
                  const isActive = pathname === item.href || (item.href !== "/" && pathname.includes(item.href.split('?')[0]) && item.href !== "/dashboard");
                  const exactDashboard = item.href === "/dashboard" && pathname === "/dashboard";
                  const isItemActive = item.href === "/dashboard" ? exactDashboard : isActive;
                  const Icon = item.icon;
                  
                  let activeStyles = "";
                  let iconActiveStyles = "";
                  
                  if (isItemActive) {
                    if (item.emergency) {
                      activeStyles = "bg-red-500/10 text-white border border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.2)]";
                      iconActiveStyles = "text-red-400 drop-shadow-[0_0_5px_rgba(239,68,68,0.8)] animate-pulse";
                    } else if (item.theme === "khokhloma") {
                      activeStyles = "bg-khokhloma-gold/10 text-white border border-khokhloma-gold/30 shadow-[0_0_15px_rgba(255,215,0,0.1)] shadow-inner drop-shadow-md";
                      iconActiveStyles = "text-khokhloma-gold drop-shadow-[0_0_5px_rgba(255,204,0,0.5)]";
                    } else {
                      activeStyles = "bg-blue-500/10 text-white border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.15)]";
                      iconActiveStyles = "text-blue-400 drop-shadow-[0_0_5px_rgba(59,130,246,0.5)]";
                    }
                  } else {
                    activeStyles = "text-gray-400 hover:bg-white/5 hover:text-white border border-transparent hover:border-white/10 transition-colors";
                    iconActiveStyles = "text-gray-500 group-hover:text-gray-300";
                    
                    if (item.emergency) {
                       iconActiveStyles += " text-red-500/70";
                    }
                  }
                  
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`relative overflow-hidden flex items-center px-4 py-2.5 text-[13px] font-bold tracking-wide rounded-xl transition-all duration-300 group ${activeStyles}`}
                    >
                      <Icon className={`relative z-10 mr-3 h-4 w-4 ${iconActiveStyles}`} />
                      <span className="relative z-10">{item.name}</span>
                      
                      {/* Убираем яркую Хохлому на фон, оставляя техно-стиль */}
                      {isItemActive && !item.emergency && (
                         <div className="absolute right-0 top-0 w-1 h-full bg-gradient-to-b from-khokhloma-gold to-yellow-600 rounded-l-full"></div>
                      )}
                      {isItemActive && item.emergency && (
                         <div className="absolute right-0 top-0 w-1 h-full bg-gradient-to-b from-red-500 to-red-600 rounded-l-full"></div>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </nav>

      {/* Быстрая кнопка ОрВД (все равно нужна как призыв к действию) */}
      <div className="p-4 border-t border-white/5 relative overflow-hidden shrink-0 group bg-[#0D0D0F]">
        <div className="bg-gradient-to-tr from-blue-500/20 to-transparent border border-blue-500/30 rounded-xl p-4 text-center relative z-10 transition-all">
          <p className="text-[10px] text-gray-400 font-black mb-2 tracking-widest uppercase">Интеграция ЕС ОрВД</p>
          <Link href="/dashboard/legal" className="block w-full py-2.5 text-[12px] font-bold bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors border border-blue-400/50 flex items-center justify-center gap-2">
            <Plane className="w-4 h-4" /> Согласовать вылет
          </Link>
        </div>
      </div>
    </aside>
  );
}
