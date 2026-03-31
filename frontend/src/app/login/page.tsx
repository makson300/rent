"use client";

import { useState } from "react";
import { ShieldCheck, MessageSquare, Briefcase, FileCheck, Info, Loader2 } from "lucide-react";
import { toast } from "react-hot-toast";

export default function LoginPage() {
    const [loading, setLoading] = useState<string | null>(null);

    const handleSSOLogin = (provider: string) => {
        setLoading(provider);
        // Эмуляция задержки редиректа на сервер OAuth
        setTimeout(() => {
            toast.success(`Успешный вход через ${provider}!`);
            setLoading(null);
            
            // Mock: Auto-login success for demo
            const authProvider = provider.includes("Госуслуги") ? "gosuslugi" : provider.includes("VK") ? "vk_id" : "max_id";
            
            localStorage.setItem("skyrent_user", JSON.stringify({ 
                id: 0, 
                telegram_id: 0, 
                user_type: "b2b",
                auth_method: authProvider,
                auth_name: provider,
                first_name: "Иван",
                last_name: "Иванов"
            }));
            
            // Redirect based on provider (B2G/B2B vs Private)
            if (authProvider === "gosuslugi") {
                window.location.href = "/dashboard/radar";
            } else {
                window.location.href = "/wallet";
            }
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-[#0A0A0B] flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Background elements */}
            <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-blue-600/10 rounded-full blur-[150px] pointer-events-none" />
            <div className="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />
            
            <div className="max-w-md w-full relative z-10">
                {/* Logo Area */}
                <div className="text-center mb-10">
                   <div className="w-20 h-20 bg-[#1A1A1D] border border-white/10 rounded-3xl mx-auto mb-6 flex items-center justify-center shadow-2xl">
                       <ShieldCheck className="w-10 h-10 text-white" />
                   </div>
                   <h1 className="text-3xl font-black text-white mb-2 tracking-tight">Единая Система</h1>
                   <p className="text-gray-400 text-sm px-4">
                       Вход для пилотов, арендаторов и участников государственных контрактов (ОрВД / Тендеры)
                   </p>
                </div>

                {/* Login Options Card */}
                <div className="bg-[#121214]/80 backdrop-blur-2xl border border-white/10 rounded-[2rem] p-8 shadow-2xl flex flex-col gap-4 relative">
                    
                    {/* GOSUSLUGI (ЕСИА) */}
                    <button 
                        onClick={() => handleSSOLogin("Госуслуги (ЕСИА)")}
                        disabled={loading !== null}
                        className="w-full relative group overflow-hidden bg-[#0D4C91] hover:bg-[#0A3D73] border border-blue-400/20 text-white font-bold py-4 px-6 rounded-2xl transition-all shadow-lg shadow-blue-900/40 flex items-center justify-between"
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                                <FileCheck className="w-4 h-4 text-white" />
                            </div>
                            <div className="text-left">
                                <div className="leading-tight">Госуслуги (ЕСИА)</div>
                                <div className="text-[10px] text-blue-200 font-normal">ЭП, Тендеры B2G и ОрВД</div>
                            </div>
                        </div>
                        {loading === "Госуслуги (ЕСИА)" && <Loader2 className="w-5 h-5 animate-spin" />}
                    </button>

                    {/* VK ID */}
                    <button 
                        onClick={() => handleSSOLogin("VK ID")}
                        disabled={loading !== null}
                        className="w-full bg-[#0077FF] hover:bg-[#005FCB] border border-blue-500/20 text-white font-bold py-4 px-6 rounded-2xl transition-all flex items-center justify-between shadow-lg shadow-blue-500/20"
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                                <span className="font-black font-sans">VK</span>
                            </div>
                            <div className="text-left">
                                <div className="leading-tight">Вход через VK ID</div>
                                <div className="text-[10px] text-blue-200 font-normal">Быстрый старт для пилотов</div>
                            </div>
                        </div>
                        {loading === "VK ID" && <Loader2 className="w-5 h-5 animate-spin" />}
                    </button>

                    <div className="h-[1px] w-full bg-white/5 my-2"></div>

                    {/* MAX MESSENGER (Корпоративный) */}
                    <button 
                        onClick={() => handleSSOLogin("Max ID")}
                        disabled={loading !== null}
                        className="w-full bg-[#1A1A1D] hover:bg-[#252529] border border-white/10 text-white font-bold py-4 px-6 rounded-2xl transition-all flex items-center justify-between"
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-[#3B82F6]/20 flex items-center justify-center shrink-0">
                                <MessageSquare className="w-4 h-4 text-[#3B82F6]" />
                            </div>
                            <div className="text-left">
                                <div className="leading-tight">Войти через MAX</div>
                                <div className="text-[10px] text-gray-400 font-normal">Корпоративный доступ (Резерв)</div>
                            </div>
                        </div>
                        {loading === "Max ID" && <Loader2 className="w-5 h-5 animate-spin text-gray-400" />}
                    </button>

                    <p className="text-[10px] text-gray-500 text-center mt-6 px-4">
                        Продолжая, вы соглашаетесь с политикой конфиденциальности и Регламентом Воздушного Кодекса.
                    </p>
                </div>
                
                <div className="mt-8 text-center">
                    <a href="/for-pilots" className="text-sm font-bold text-gray-400 hover:text-white flex items-center justify-center gap-1 transition-colors">
                        <Info className="w-4 h-4" /> Зачем пилоту регистрироваться?
                    </a>
                </div>
            </div>
        </div>
    );
}
