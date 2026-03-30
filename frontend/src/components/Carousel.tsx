"use client";

import { useState, useEffect } from "react";
import { Target, MapPin, ShieldCheck, HeartPulse, ChevronLeft, ChevronRight, Zap } from "lucide-react";
import Link from "next/link";

const CAROUSEL_SLIDES = [
    {
        id: "b2g-radar",
        title: "Радар B2G Заказов",
        highlight: "С ИИ-анализом",
        description: "Первая в СНГ система умного трекинга авиа-тендеров. Нейросеть автоматически рассчитает, хватит ли вашему дрону заряда батареи для выполнения контракта.",
        icon: Target,
        color: "text-khokhloma-gold",
        bgGlow: "bg-yellow-500/10",
        borderGlow: "border-khokhloma-gold/30",
        link: "/dashboard/radar",
        buttonText: "Открыть Радар"
    },
    {
        id: "orvd",
        title: "Согласование ОрВД",
        highlight: "За 5 минут",
        description: "Забудьте про бюрократию. Генератор формализованных заявок (ТШС) для Росавиации. Скопировал, отправил, получил зеленый свет на вылет.",
        icon: MapPin,
        color: "text-blue-400",
        bgGlow: "bg-blue-500/10",
        borderGlow: "border-blue-500/30",
        link: "/dashboard/legal",
        buttonText: "План Полета"
    },
    {
        id: "escrow",
        title: "Защита (Эскроу)",
        highlight: "Анти-Демпинг",
        description: "Безопасное проведение платежей между заказчиком и пилотом. Наша система AI-модерации штрафует за демпинг, защищая рыночную стоимость услуг.",
        icon: ShieldCheck,
        color: "text-emerald-400",
        bgGlow: "bg-emerald-500/10",
        borderGlow: "border-emerald-500/30",
        link: "/wallet",
        buttonText: "Фриланс Биржа"
    },
    {
        id: "mchs",
        title: "Резерв МЧС 🇷🇺",
        highlight: "ПСО Доброволец",
        description: "Подтвердите статус волонтера в один клик. В случае ЧС или пропажи людей в вашем регионе, штаб выдаст прямой допуск и зеленый коридор на спасательные полеты.",
        icon: HeartPulse,
        color: "text-red-400",
        bgGlow: "bg-red-500/10",
        borderGlow: "border-red-500/30",
        link: "/dashboard/radar?filter=emergency",
        buttonText: "Штаб Спасения"
    }
];

export default function BenefitsCarousel() {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isHovered, setIsHovered] = useState(false);

    // Auto-scroll logic
    useEffect(() => {
        if (isHovered) return;
        
        const timer = setInterval(() => {
            setCurrentIndex((prev) => (prev + 1) % CAROUSEL_SLIDES.length);
        }, 6000); // 6 seconds per slide
        
        return () => clearInterval(timer);
    }, [isHovered]);

    const handlePrev = () => setCurrentIndex((prev) => (prev - 1 + CAROUSEL_SLIDES.length) % CAROUSEL_SLIDES.length);
    const handleNext = () => setCurrentIndex((prev) => (prev + 1) % CAROUSEL_SLIDES.length);

    return (
        <div 
            className="w-full max-w-5xl mx-auto py-12 px-4 relative"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <div className="flex items-center justify-between mb-8 px-4">
                <div className="flex items-center gap-3">
                    <Zap className="w-6 h-6 text-khokhloma-gold animate-pulse" />
                    <h2 className="text-2xl md:text-3xl font-black text-white tracking-widest uppercase items-center gap-2">
                        Экосистема <span className="text-gray-500 block text-xs mt-1">Один экран — все инструменты пилота</span>
                    </h2>
                </div>
                
                {/* Navigation Controls */}
                <div className="hidden sm:flex items-center gap-2">
                    <button 
                        onClick={handlePrev}
                        className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center bg-[#121214] hover:bg-white/10 transition-colors"
                    >
                        <ChevronLeft className="w-6 h-6 text-white" />
                    </button>
                    <button 
                        onClick={handleNext}
                        className="w-12 h-12 rounded-full border border-white/10 flex items-center justify-center bg-[#121214] hover:bg-white/10 transition-colors"
                    >
                        <ChevronRight className="w-6 h-6 text-white" />
                    </button>
                </div>
            </div>

            {/* Carousel Track Container */}
            <div className="relative overflow-hidden rounded-[2rem] h-[400px] sm:h-[350px]">
                <div 
                    className="absolute top-0 left-0 w-full h-full flex transition-transform duration-700 ease-in-out"
                    style={{ transform: `translateX(-${currentIndex * 100}%)` }}
                >
                    {CAROUSEL_SLIDES.map((slide, idx) => {
                        const Icon = slide.icon;
                        return (
                            <div key={slide.id} className="min-w-full h-full p-2 sm:p-4">
                                <div className={`w-full h-full border ${slide.borderGlow} rounded-[1.5rem] p-8 md:p-12 relative overflow-hidden bg-[#0A0A0B]/80 backdrop-blur-3xl shadow-[0_20px_50px_-12px_rgba(0,0,0,1)]`}>
                                    
                                    {/* Glass Morphism Glow Background */}
                                    <div className={`absolute -right-20 -top-20 w-80 h-80 rounded-full blur-[100px] pointer-events-none opacity-50 ${slide.bgGlow}`} />
                                    
                                    <div className="relative z-10 flex flex-col md:flex-row h-full gap-8 md:items-center">
                                        <div className="flex-1 flex flex-col justify-center">
                                            <div className="inline-flex py-1 px-3 rounded-md bg-white/5 border border-white/10 w-max mb-4">
                                                <span className={`text-xs font-black uppercase tracking-widest ${slide.color}`}>
                                                    {slide.highlight}
                                                </span>
                                            </div>
                                            <h3 className="text-3xl md:text-5xl font-black text-white mb-6 leading-tight">
                                                {slide.title}
                                            </h3>
                                            <p className="text-gray-400 text-lg mb-8 max-w-xl leading-relaxed">
                                                {slide.description}
                                            </p>
                                            <div>
                                                <Link 
                                                    href={slide.link}
                                                    className={`px-8 py-4 rounded-xl font-bold transition-all inline-flex items-center gap-2 ${idx === 0 ? "bg-khokhloma-gold hover:bg-yellow-600 text-black shadow-[0_0_20px_rgba(255,215,0,0.3)]" : "bg-white/10 hover:bg-white/20 text-white border border-white/10"}`}
                                                >
                                                    {slide.buttonText}
                                                </Link>
                                            </div>
                                        </div>
                                        
                                        <div className="hidden md:flex flex-1 justify-center items-center h-full">
                                            <div className={`w-40 h-40 rounded-full flex items-center justify-center border-4 border-white/5 backdrop-blur-xl ${slide.bgGlow}`}>
                                                <Icon className={`w-20 h-20 ${slide.color}`} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Pagination Indicators */}
            <div className="flex justify-center mt-6 gap-3">
                {CAROUSEL_SLIDES.map((_, idx) => (
                    <button
                        key={idx}
                        onClick={() => setCurrentIndex(idx)}
                        className={`transition-all duration-300 rounded-full ${
                            currentIndex === idx 
                            ? "w-10 h-2 bg-khokhloma-gold" 
                            : "w-2 h-2 bg-white/20 hover:bg-white/40"
                        }`}
                        aria-label={`Go to slide ${idx + 1}`}
                    />
                ))}
            </div>
        </div>
    );
}
