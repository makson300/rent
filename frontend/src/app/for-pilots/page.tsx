"use client";

import { Box, MapPin, Briefcase, FileCheck, ShieldCheck, Heart, ArrowRight, BookOpen, Banknote, Rocket, Lightbulb } from "lucide-react";
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

            {/* Engineer & Startup Showcase (Phase 33.3) */}
            <div className="border-t border-white/5 bg-[#0D0D12] py-24 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[150px] pointer-events-none"></div>
                <div className="max-w-7xl mx-auto px-4 relative z-10">
                    <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
                        <div>
                            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-bold text-blue-400 mb-4 uppercase tracking-widest">
                                <Rocket className="w-4 h-4" /> Хаб Инженеров
                            </div>
                            <h2 className="text-3xl md:text-5xl font-black mb-4">Витрина <span className="text-blue-500">Стартапов</span></h2>
                            <p className="text-gray-400 text-lg max-w-2xl">
                                Платформа "Горизонт" поддерживает не только пилотов, но и конструкторов. Мы связываем прорывные идеи с инвесторами и государственными фондами.
                            </p>
                        </div>
                        <button className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] flex items-center gap-2">
                            <Lightbulb className="w-5 h-5" /> Предложить Идею
                        </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Startup Card 1 */}
                        <div className="bg-[#15151A] border border-white/5 rounded-3xl p-6 hover:border-white/20 transition-all group">
                            <div className="h-40 bg-zinc-900 rounded-2xl mb-6 relative overflow-hidden flex items-center justify-center border border-white/5 text-gray-700 font-bold">
                                [Рендер Проекта Агро-Дрона]
                            </div>
                            <div className="flex items-center gap-2 text-xs font-bold text-khokhloma-gold bg-khokhloma-gold/10 px-2 py-1 rounded w-max mb-3 uppercase tracking-wide">
                                Ищем Инвестиции
                            </div>
                            <h3 className="text-xl font-bold mb-2 text-white group-hover:text-blue-400 transition-colors">SkyNet Agro T-X</h3>
                            <p className="text-sm text-gray-400">Тяжелый агродрон с полезной нагрузкой 60кг и локализацией 90% производства в РФ.</p>
                        </div>
                        {/* Startup Card 2 */}
                        <div className="bg-[#15151A] border border-white/5 rounded-3xl p-6 hover:border-white/20 transition-all group">
                            <div className="h-40 bg-zinc-900 rounded-2xl mb-6 relative overflow-hidden flex items-center justify-center border border-white/5 text-gray-700 font-bold">
                                [Рендер Видеолинка]
                            </div>
                            <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded w-max mb-3 uppercase tracking-wide">
                                Грант Получен
                            </div>
                            <h3 className="text-xl font-bold mb-2 text-white group-hover:text-blue-400 transition-colors">Horizon Link Pro</h3>
                            <p className="text-sm text-gray-400">Защищенный цифровой видеолинк для инспекционных дронов, невосприимчивый к РЭБ помехам.</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Legal Archive & Subsidies (Phase 33.1 & 33.2) */}
            <div className="border-t border-white/5 py-24 px-4 bg-[#0A0A0B]">
                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Subsidies */}
                    <div className="bg-gradient-to-br from-[#121214] to-[#1A1A1D] border border-white/10 rounded-[2rem] p-10 relative overflow-hidden group">
                        <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center mb-8 border border-emerald-500/20">
                            <Banknote className="w-8 h-8 text-emerald-400" />
                        </div>
                        <h3 className="text-3xl font-black text-white mb-4">Государственные <span className="text-emerald-400">Субсидии</span></h3>
                        <p className="text-gray-400 mb-8 leading-relaxed">
                            Узнайте, как получить дотации от Минпромторга на закупку отечественных беспилотников и компенсацию части затрат на сертификацию инженеров.
                        </p>
                        <button className="flex items-center gap-2 text-emerald-400 font-bold hover:text-emerald-300 transition-colors">
                            Открыть базу программ поддержки <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                        </button>
                    </div>

                    {/* Legal Archive */}
                    <div className="bg-gradient-to-br from-[#121214] to-[#1A1A1D] border border-white/10 rounded-[2rem] p-10 relative overflow-hidden group">
                         <div className="w-16 h-16 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-8 border border-purple-500/20">
                            <BookOpen className="w-8 h-8 text-purple-400" />
                        </div>
                        <h3 className="text-3xl font-black text-white mb-4">Правовой <span className="text-purple-400">Архив</span></h3>
                        <p className="text-gray-400 mb-8 leading-relaxed">
                            Актуальный Воздушный Кодекс, постановления о зонировании (ЭПР) и правила регистрации БАС. ИИ-парсер ежедневно обновляет базу законов.
                        </p>
                        <button className="flex items-center gap-2 text-purple-400 font-bold hover:text-purple-300 transition-colors">
                            Изучить нормативную базу <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                        </button>
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
