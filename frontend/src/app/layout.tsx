import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import TopNavbar from "@/components/TopNavbar";
import { AuthProvider } from "@/components/AuthProvider";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = {
  title: "Sky Rent AI - Экосистема БПЛА",
  description: "Единая платформа для беспилотной индустрии: аренда дронов, биржа пилотов, обучение и интерактивные карты.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className="dark scroll-smooth">
      <body className={`${inter.className} bg-[#0A0A0B] text-white selection:bg-blue-500/30 overflow-hidden`}>
        <AuthProvider>
          <div className="flex h-screen bg-[#0A0A0B]">
          {/* Desktop Sidebar */}
          <Sidebar />

          {/* Main Workspace */}
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            {/* Mobile Header */}
            <TopNavbar />

            {/* Scrollable Content Area */}
            <main className="flex-1 overflow-y-auto w-full">
              {children}
              
              {/* Footer */}
              <footer className="border-t border-white/5 bg-[#0A0A0B] py-8 mt-20">
                <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
                  <p>© 2026 Sky Rent. Национальная Платформа БПЛА.</p>
                </div>
              </footer>
            </main>
          </div>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
