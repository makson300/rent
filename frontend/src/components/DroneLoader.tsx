"use client";

import React from "react";

interface DroneLoaderProps {
  text?: string;
  subtext?: string;
  size?: "sm" | "md" | "lg";
  color?: "blue" | "gold" | "red" | "white";
}

export default function DroneLoader({ 
    text = "Анализ данных...", 
    subtext = "Нейросеть обрабатывает запрос", 
    size = "md",
    color = "gold"
}: DroneLoaderProps) {
    
    // Size variants
    const sizeClasses = {
        sm: "w-8 h-8",
        md: "w-16 h-16",
        lg: "w-24 h-24"
    };

    // Color variants (Tailwind textual classes for SVG stroke/fill)
    const colorClasses = {
        blue: "text-blue-500 shadow-blue-500/50",
        gold: "text-khokhloma-gold shadow-khokhloma-gold/50",
        red: "text-red-500 shadow-red-500/50",
        white: "text-white shadow-white/50"
    };
    
    const hexColor = {
        blue: "#3b82f6",
        gold: "#FFCC00",
        red: "#ef4444",
        white: "#ffffff"
    }[color];

    return (
        <div className="flex flex-col items-center justify-center animate-in fade-in zoom-in duration-500">
            {/* Анимированный Дрон (SVG) */}
            <div className={`relative ${sizeClasses[size]} mb-6 flex items-center justify-center`}>
                {/* Пульсирующие круги под дроном (эффект винтов/ветра) */}
                <div className={`absolute inset-0 rounded-full border-2 border-t-transparent animate-spin border-${color === 'gold' ? 'khokhloma-gold' : color === 'white' ? 'white' : color+'-500'} opacity-30`} style={{ animationDuration: '3s' }}></div>
                <div className={`absolute inset-2 rounded-full border border-b-transparent animate-spin border-${color === 'gold' ? 'khokhloma-gold' : color === 'white' ? 'white' : color+'-500'} opacity-50`} style={{ animationDuration: '1.5s', animationDirection: 'reverse' }}></div>
                
                {/* Само тело дрона с легкой анимацией зависания (hovering) */}
                <div className="absolute z-10 animate-bounce" style={{ animationDuration: '2s' }}>
                    <svg 
                        viewBox="0 0 24 24" 
                        fill="none" 
                        stroke="currentColor" 
                        strokeWidth="1.5" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                        className={`w-full h-full ${colorClasses[color].split(' ')[0]}`}
                    >
                        {/* Корпус Квадрокоптера */}
                        <rect x="9" y="10" width="6" height="4" rx="1" fill="currentColor" fillOpacity="0.2" />
                        {/* Лучи */}
                        <path d="M4 8l5 3M20 8l-5 3M4 16l5-3M20 16l-5-3" />
                        {/* Моторы / Пропеллеры */}
                        <circle cx="4" cy="8" r="1.5" className="animate-spin" style={{ transformOrigin: '4px 8px', animationDuration: '0.2s' }} />
                        <circle cx="20" cy="8" r="1.5" className="animate-spin" style={{ transformOrigin: '20px 8px', animationDuration: '0.2s', animationDirection: 'reverse' }} />
                        <circle cx="4" cy="16" r="1.5" className="animate-spin" style={{ transformOrigin: '4px 16px', animationDuration: '0.2s', animationDirection: 'reverse' }} />
                        <circle cx="20" cy="16" r="1.5" className="animate-spin" style={{ transformOrigin: '20px 16px', animationDuration: '0.2s' }} />
                    </svg>
                </div>

                {/* Инверсионный след / свечение */}
                <div className={`absolute -bottom-4 w-12 h-2 ${colorClasses[color].split(' ')[1]} blur-md rounded-full opacity-60 animate-pulse`}></div>
            </div>

            {/* Текстовка */}
            {text && (
                <h3 className={`font-black text-lg tracking-wide uppercase bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500 animate-pulse text-center mb-1`}>
                    {text}
                </h3>
            )}
            {subtext && (
                <p className="text-gray-500 text-xs font-medium text-center max-w-[200px] leading-tight">
                    {subtext}
                </p>
            )}
        </div>
    );
}
