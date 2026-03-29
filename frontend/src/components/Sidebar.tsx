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
  Scale
} from "lucide-react";

const NAV_ITEMS = [
  { name: "Главная", href: "/", icon: Home, theme: "khokhloma" },
  { name: "Биржа работ", href: "/jobs", icon: Briefcase, theme: "tricolor" },
  { name: "Тендеры", href: "/tenders", icon: FileText, theme: "tricolor" },
  { name: "Аэронавигация", href: "/map", icon: Map, theme: "khokhloma" },
  { name: "ЧС Радар", href: "/map?filter=emergency", icon: ShieldAlert, theme: "khokhloma" },
  { name: "Гос. Услуги", href: "/dashboard/legal", icon: Scale, theme: "tricolor" },
  { name: "Академия БАС", href: "/education", icon: GraduationCap, theme: "tricolor" },
  { name: "Маркетплейс", href: "/catalog", icon: ShoppingCart, theme: "khokhloma" },
  { name: "Личный Кабинет", href: "/dashboard", icon: UserCircle, theme: "khokhloma" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#0A0A0B]/95 border-r border-white/5 h-screen sticky top-0 flex flex-col hidden md:flex">
      <div className="h-20 flex items-center px-6 border-b border-white/5 relative overflow-hidden">
        {/* Decorative background glow for the logo */}
        <div className="absolute top-0 right-0 w-24 h-full bg-khokhloma-red/20 blur-2xl"></div>
        <div className="relative z-10 flex flex-col">
          <span className="text-xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-khokhloma-gold to-khokhloma-red flex items-center gap-2">
            ГОРИЗОНТ 🇷🇺
          </span>
          <span className="text-[10px] font-bold tracking-widest text-gray-400 uppercase mt-0.5">
            НАЦИОНАЛЬНАЯ ЭКОСИСТЕМА БАС
          </span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-8 space-y-2 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.icon;
          
          let activeStyles = "";
          let iconActiveStyles = "";
          
          if (isActive) {
            if (item.theme === "khokhloma") {
              activeStyles = "bg-khokhloma-red/10 text-khokhloma-gold border border-khokhloma-red/20";
              iconActiveStyles = "text-khokhloma-gold";
            } else {
              activeStyles = "bg-tricolor-blue/10 text-tricolor-white border border-tricolor-blue/30";
              iconActiveStyles = "text-tricolor-blue";
            }
          } else {
            activeStyles = "text-gray-400 hover:bg-white/5 hover:text-white border border-transparent";
            iconActiveStyles = "text-gray-500";
          }
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all ${activeStyles}`}
            >
              <Icon className={`mr-3 h-5 w-5 ${iconActiveStyles}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/5 relative overflow-hidden">
        <div className="absolute inset-0 bg-pattern-tricolor opacity-50"></div>
        <div className="bg-gradient-to-tr from-tricolor-blue/30 to-tricolor-blue/10 border border-tricolor-blue/30 rounded-xl p-4 text-center relative z-10">
          <p className="text-xs text-tricolor-white font-medium mb-1 tracking-wide uppercase">ЕС ОрВД России</p>
          <Link href="/dashboard/legal" className="block w-full py-2.5 text-xs font-bold bg-tricolor-blue hover:bg-blue-800 text-white rounded-lg transition-colors shadow-lg shadow-tricolor-blue/20">
            Согласовать полет
          </Link>
        </div>
      </div>
    </aside>
  );
}
