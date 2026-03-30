"use client";

import Link from "next/link";
import BenefitsCarousel from "@/components/Carousel";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function Home() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
      target: ref,
      offset: ["start start", "end start"]
  });
  
  // Parallax effects
  const yBg = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const opacityText = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <div ref={ref} className="relative overflow-hidden bg-[#050505] min-h-screen">
      {/* Parallax Background Glow */}
      <motion.div style={{ y: yBg }} className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-khokhloma-red rounded-full mix-blend-screen filter blur-[150px] opacity-10 animate-blob"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-khokhloma-gold rounded-full mix-blend-screen filter blur-[150px] opacity-10 animate-blob animation-delay-2000"></div>
        <div className="absolute inset-0 bg-pattern-khokhloma opacity-5 z-0"></div>
      </motion.div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-8">
        <motion.div 
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            style={{ opacity: opacityText }}
            className="text-center"
        >
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 uppercase">
            <span className="block text-white">Национальная Экосистема</span>
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-khokhloma-gold to-khokhloma-red drop-shadow-lg">
              Инфраструктуры БАС
            </span>
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-400 leading-relaxed font-light">
            Единая государственная платформа «Горизонт»: интеллектуальный маркетплейс, биржа B2G тендеров, реестр коммерческих операторов и моментальное согласование полётов через ОрВД.
          </p>

          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="mt-12 flex flex-col sm:flex-row gap-6 justify-center items-center"
          >
            <Link href="/catalog" className="w-full sm:w-auto text-center px-10 py-4 border border-transparent text-lg font-bold rounded-xl text-black bg-gradient-to-r from-khokhloma-gold via-yellow-400 to-khokhloma-gold bg-size-200 animate-gradient shadow-[0_0_30px_rgba(245,176,65,0.4)] hover:shadow-[0_0_50px_rgba(245,176,65,0.6)] transition-all hover:-translate-y-1">
              Перейти к сервисам
            </Link>
            <Link href="/map" className="w-full sm:w-auto text-center px-8 py-4 border border-white/10 text-lg font-medium rounded-xl text-white bg-white/5 hover:bg-white/10 backdrop-blur-md transition-all hover:-translate-y-1 flex items-center justify-center gap-2">
              <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Интерактивный Радар
            </Link>
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll-triggered reveal for Carousel using Framer Motion */}
      <motion.div
        initial={{ opacity: 0, y: 100 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.7 }}
        className="relative z-20"
      >
        <BenefitsCarousel />
      </motion.div>

    </div>
  );
}
