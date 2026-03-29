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
  UserCircle 
} from "lucide-react";

const NAV_ITEMS = [
  { name: "Главная", href: "/", icon: Home },
  { name: "Каталог & Магазин", href: "/catalog", icon: ShoppingCart },
  { name: "Биржа услуг", href: "/jobs", icon: Briefcase },
  { name: "Мои Задачи", href: "/dashboard/tasks", icon: FileText },
  { name: "Карта (Зоны)", href: "/map", icon: Map },
  { name: "Радар ЧП", href: "/radar", icon: ShieldAlert },
  { name: "Обучение", href: "/education", icon: GraduationCap },
  { name: "Профиль", href: "/dashboard", icon: UserCircle },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#0A0A0B]/95 border-r border-white/5 h-screen sticky top-0 flex flex-col hidden md:flex">
      <div className="h-16 flex items-center px-6 border-b border-white/5">
        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-400">
          Sky Rent
        </span>
        <span className="ml-2 text-xs font-medium px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
          SUPER-APP
        </span>
      </div>

      <nav className="flex-1 px-4 py-8 space-y-2 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all ${
                isActive
                  ? "bg-blue-500/10 text-blue-400"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              <Icon className={`mr-3 h-5 w-5 ${isActive ? "text-blue-400" : "text-gray-500"}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/5">
        <div className="bg-gradient-to-tr from-blue-900/40 to-cyan-900/40 border border-blue-500/20 rounded-xl p-4 text-center">
          <p className="text-xs text-blue-300 font-medium mb-1">Генерация ИВП</p>
          <Link href="/dashboard/orvd" className="block w-full py-2 text-xs font-semibold bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors">
            Согласовать полет
          </Link>
        </div>
      </div>
    </aside>
  );
}
