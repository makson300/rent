"use client";

import { Menu, Settings, FileText } from "lucide-react";
import dynamic from "next/dynamic";
import Link from "next/link";

const TelegramLoginWidget = dynamic(() => import("@/components/TelegramLoginWidget"), { ssr: false });

export default function TopNavbar() {
  return (
    <nav className="md:hidden sticky top-0 w-full z-50 bg-[#0A0A0B]/80 backdrop-blur-xl border-b border-white/5 py-4 px-6 flex justify-between items-center">
      <div className="flex items-center">
        <button className="mr-4 text-gray-300 hover:text-white">
          <Menu className="h-6 w-6" />
        </button>
        <span className="text-lg font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-khokhloma-gold to-khokhloma-red flex items-center gap-2">
          ГОРИЗОНТ
        </span>
      </div>
      <div className="flex items-center gap-3">
        <Link 
          href="/wallet" 
          className="hidden sm:flex items-center justify-center gap-2 px-3 py-1.5 bg-khokhloma-red/10 text-white border border-khokhloma-gold/30 hover:bg-khokhloma-red/20 shadow-[0_0_10px_rgba(204,0,0,0.3)] hover:shadow-[0_0_15px_rgba(255,204,0,0.5)] rounded-lg transition-all text-sm font-bold"
        >
          <FileText className="w-4 h-4 text-khokhloma-gold drop-shadow-md" />
          Мой Кошелёк
        </Link>
        <Link 
          href="https://45.12.5.177.nip.io/" 
          className="hidden md:flex items-center justify-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white rounded-lg transition-colors border border-white/10 text-sm font-medium hover:border-white/30"
        >
          Панель Управления
        </Link>
        <TelegramLoginWidget botName="SkyRentAIBot" />
      </div>
    </nav>
  );
}
