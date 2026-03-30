"use client";

import { Box, MapPin, Briefcase, FileCheck, ShieldCheck, Heart, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function ForPilotsPage() {
    return (
        <div className="min-h-screen bg-[#0A0A0B] text-white">
            
            {/* Header section with drone silhouette background */}
            <div className="relative pt-32 pb-20 px-4 overflow-hidden border-b border-white/5">
                <div className="absolute inset-0 z-0 flex items-center justify-center opacity-[0.03]">
                    {/* SVG Drone Silhouette Watermark */}
                    <svg viewBox="0 0 24 24" width="800" height="800" fill="none" stroke="currentColor" strokeWidth="0.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6 M2 12h20" />
                        <circle cx="12" cy="12" r="10" />
                        <path d="M7 7l10 10M17 7L7 17" />
                    </svg>
                </div>
                
                <div className="max-w-5xl mx-auto relative z-10 text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-sm font-bold text-blue-400 mb-8 uppercase tracking-widest">
                        <ShieldCheck className="w-4 h-4" /> Единое Окно Пилота БАС
                    </div>
                    <h1 className="text-5xl md:text-7xl font-black mb-6 tracking-tight">
                        Зарабатывай. Летай. <br/>
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-khokhloma-gold to-yellow-500">
                            Легально.
                        </span>
                    </h1>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
                        Регистрируй свой дрон в системе "Горизонт Хаб". Получай доступ к государственным тендерам B2G, страхуй оборудование и участвуй в спасательных операциях МЧС.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link href="/login" className="px-8 py-4 bg-khokhloma-gold hover:bg-yellow-600 text-black font-black uppercase tracking-wider rounded-xl transition-all shadow-[0_0_30px_rgba(255,215,0,0.2)] flex items-center gap-2">
                            Регистрация через ЕСИА <ArrowRight className="w-5 h-5" />
                        </Link>
                        <Link href="/login" className="px-8 py-4 bg-[#1A1A1D] hover:bg-[#252529] border border-white/10 text-white font-bold rounded-xl transition-all shadow-lg">
                            Вход через VK ID
                        </Link>
                    </div>
                </div>
            </div>

            {/* Value Proposition Grid */}
            <div className="max-w-7xl mx-auto px-4 py-24">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-black mb-4">Почему пилоты выбирают <span className="text-khokhloma-gold">Горизонт</span>?</h2>
                    <p className="text-gray-400 text-lg">Мы сняли с вас бюрократию, чтобы вы могли сфокусироваться на полетах.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* B2G Радар */}
                    <div className="bg-[#121214] border border-white/5 hover:border-khokhloma-gold/30 transition-colors rounded-3xl p-8 group">
                        <div className="w-14 h-14 bg-khokhloma-gold/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <Briefcase className="w-7 h-7 text-khokhloma-gold" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Заказы B2B и B2G</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            Доступ к закрытому Радару тендеров. Система сама рассчитает, хватит ли вашему дрону батареи для выполнения контракта.
                        </p>
                    </div>

                    {/* Росавиация / ОрВД */}
                    <div className="bg-[#121214] border border-white/5 hover:border-blue-500/30 transition-colors rounded-3xl p-8 group">
                        <div className="w-14 h-14 bg-blue-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <MapPin className="w-7 h-7 text-blue-400" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">ОрВД в 2 клика</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            Встроенный генератор формализованной заявки (ТШС) для Росавиации. Скопировал, отправил, получил разрешение на ИВП.
                        </p>
                    </div>

                    {/* Страховка КАСКО */}
                    <div className="bg-[#121214] border border-white/5 hover:border-emerald-500/30 transition-colors rounded-3xl p-8 group">
                        <div className="w-14 h-14 bg-emerald-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <ShieldCheck className="w-7 h-7 text-emerald-400" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Льготное КАСКО</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            Страхуем даже самосборы. Оценка состояния по лог-файлам (TXT). Юридический щит от претензий третьих лиц.
                        </p>
                    </div>

                    {/* МЧС Волонтер */}
                    <div className="bg-[#121214] border border-white/5 hover:border-red-500/30 transition-colors rounded-3xl p-8 group md:col-span-2 lg:col-span-1">
                        <div className="w-14 h-14 bg-red-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <Heart className="w-7 h-7 text-red-400" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Резерв МЧС (ПСО)</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            Стасуйте статус добровольца. В случае ЧС или пропажи людей в вашем регионе — штаб выдаст вам бесплатный зеленый коридор на полеты.
                        </p>
                    </div>

                    {/* Документооборот */}
                    <div className="bg-[#121214] border border-white/5 hover:border-purple-500/30 transition-colors rounded-3xl p-8 group lg:col-span-2">
                        <div className="w-14 h-14 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <FileCheck className="w-7 h-7 text-purple-400" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Единый Реестр Лицензий</h3>
                        <p className="text-gray-400 text-sm leading-relaxed max-w-xl">
                            Храните все сертификаты внешнего пилота в одном профиле. Система автоматически верифицирует их через Минтранс и повышает ваш траст-фактор в глазах заказчиков (B2B). Бесплатное обучение для новичков.
                        </p>
                    </div>
                </div>
            </div>

            {/* CTA Footer */}
            <div className="border-t border-white/5 bg-[#0D0D0F] py-16 text-center">
                <h2 className="text-3xl font-black mb-6">Готовы стать частью Авиации Будущего?</h2>
                <Link href="/login" className="inline-block px-8 py-4 bg-white hover:bg-gray-200 text-black font-black uppercase tracking-wider rounded-xl transition-all shadow-xl">
                    Зарегистрировать Дрон
                </Link>
            </div>
            
        </div>
    );
}
