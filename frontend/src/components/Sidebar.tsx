"use client";

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
  Settings
} from "lucide-react";

const NAV_ITEMS = [
  { name: "Главная", href: "/", icon: Home, theme: "khokhloma" },
  { name: "Кошелек & Сделки (Escrow)", href: "/wallet", icon: FileText, theme: "khokhloma", pulse: true },
  { name: "Фриланс и Заказы", href: "/jobs", icon: Briefcase, theme: "tricolor" },
  { name: "B2B / B2G Тендеры", href: "/tenders", icon: FileText, theme: "tricolor" },
  { name: "Карта Полётов (NFZ)", href: "/map", icon: Map, theme: "khokhloma" },
  { name: "Центр ЧС (Радар)", href: "/map?filter=emergency", icon: ShieldAlert, theme: "khokhloma" },
  { name: "Интеграция ЕС ОрВД", href: "/dashboard/legal", icon: Scale, theme: "tricolor" },
  { name: "Академия БАС", href: "/education", icon: GraduationCap, theme: "tricolor" },
  { name: "Аренда оборудования", href: "/catalog", icon: ShoppingCart, theme: "khokhloma" },
  { name: "Личный Кабинет", href: "/dashboard", icon: UserCircle, theme: "khokhloma" },
  { name: "Панель Управления", href: "https://45.12.5.177.nip.io/", icon: Settings, theme: "tricolor" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#0A0A0B]/95 border-r border-white/5 h-screen sticky top-0 flex flex-col hidden md:flex shrink-0">
      <div className="h-20 flex items-center px-6 border-b border-white/5 relative overflow-hidden group">
        {/* Decorative background glow for the logo */}
        <div className="absolute top-0 right-0 w-24 h-full bg-khokhloma-red/40 blur-[30px] transition-all duration-700 group-hover:bg-khokhloma-gold/40 group-hover:w-32"></div>
        <div className="relative z-10 flex flex-col transform transition-transform duration-300 group-hover:scale-105 group-hover:translate-x-1">
          <span className="text-xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-khokhloma-gold via-[#ffdd55] to-khokhloma-red flex items-center gap-2 drop-shadow-[0_0_8px_rgba(255,204,0,0.5)]">
            ГОРИЗОНТ <span className="drop-shadow-none">🇷🇺</span>
          </span>
          <span className="text-[10px] font-bold tracking-widest text-gray-400 uppercase mt-0.5 group-hover:text-gray-200 transition-colors">
            НАЦИОНАЛЬНАЯ СИСТЕМА БАС
          </span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-8 space-y-2 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && item.href !== "/map?filter=emergency" && pathname.startsWith(item.href));
          const Icon = item.icon;
          
          let activeStyles = "";
          let iconActiveStyles = "";
          
          if (isActive) {
            if (item.theme === "khokhloma") {
              activeStyles = "bg-khokhloma-red/10 text-white border border-khokhloma-gold/40 shadow-[0_0_15px_rgba(204,0,0,0.3)] shadow-inner drop-shadow-md";
              iconActiveStyles = "text-khokhloma-gold drop-shadow-[0_0_5px_rgba(255,204,0,0.8)] animate-pulse";
            } else {
              activeStyles = "bg-tricolor-blue/15 text-white border border-tricolor-blue/50 shadow-[0_0_15px_rgba(0,102,204,0.3)]";
              iconActiveStyles = "text-[#66b3ff] drop-shadow-[0_0_5px_rgba(102,179,255,0.8)]";
            }
          } else {
            activeStyles = "text-gray-400 hover:bg-white/5 hover:text-white border border-transparent hover:border-white/10 hover:shadow-[0_4px_10px_rgba(0,0,0,0.5)] hover:-translate-y-0.5";
            iconActiveStyles = "text-gray-500 group-hover:text-gray-300";
          }
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`relative overflow-hidden flex items-center px-4 py-3 text-[13px] font-bold tracking-wide rounded-xl transition-all duration-300 group ${activeStyles} ${item.pulse && !isActive ? 'animate-pulse border-khokhloma-gold/20' : ''}`}
            >
              <div 
                className="absolute top-0 right-0 h-full w-[30%] bg-pattern-khokhloma opacity-10 pointer-events-none transition-opacity duration-300 group-hover:opacity-30" 
                style={{ 
                  maskImage: 'linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)', 
                  WebkitMaskImage: 'linear-gradient(to left, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)',
                  backgroundSize: "cover"
                }}
              />
              <Icon className={`relative z-10 mr-3 h-5 w-5 ${iconActiveStyles}`} />
              <span className="relative z-10">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/5 relative overflow-hidden shrink-0 group">
        <div className="absolute inset-0 bg-pattern-tricolor opacity-50 transition-opacity duration-500 group-hover:opacity-70"></div>
        <div className="bg-gradient-to-tr from-tricolor-blue/40 to-tricolor-blue/10 border border-tricolor-blue/40 rounded-xl p-4 text-center relative z-10 shadow-[0_0_15px_rgba(0,102,204,0.2)] group-hover:shadow-[0_0_25px_rgba(0,102,204,0.4)] transition-all">
          <p className="text-[11px] text-tricolor-white font-extrabold mb-2 tracking-widest uppercase drop-shadow-md">Интеграция ЕС ОрВД</p>
          <Link href="/dashboard/legal" className="block w-full py-2.5 text-[13px] font-bold bg-tricolor-blue hover:bg-blue-600 text-white rounded-lg transition-all shadow-[0_0_10px_rgba(0,102,204,0.5)] hover:shadow-[0_0_20px_rgba(102,179,255,0.8)] hover:-translate-y-0.5 border border-white/10">
            Согласовать полет
          </Link>
        </div>
      </div>
    </aside>
  );
}
