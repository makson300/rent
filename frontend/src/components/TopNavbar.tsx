"use client";

import { Menu } from "lucide-react";
import TelegramLoginWidget from "@/components/TelegramLoginWidget";

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
      <div>
        <TelegramLoginWidget botName="SkyRentAIBot" />
      </div>
    </nav>
  );
}
