import Link from "next/link";

export default function Home() {
  return (
    <div className="relative overflow-hidden">
      {/* Background Glow - Khokhloma Theme */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-khokhloma-red rounded-full mix-blend-screen filter blur-[128px] opacity-20 animate-blob"></div>
      <div className="absolute top-0 -right-4 w-72 h-72 bg-khokhloma-gold rounded-full mix-blend-screen filter blur-[128px] opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-tricolor-blue rounded-full mix-blend-screen filter blur-[128px] opacity-10 animate-blob animation-delay-4000"></div>
      
      {/* Subtle overlay pattern */}
      <div className="absolute inset-0 bg-pattern-khokhloma opacity-20 z-0"></div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-24 pb-12">
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 uppercase">
            <span className="block text-white">Национальная Экосистема</span>
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-khokhloma-gold to-khokhloma-red drop-shadow-lg">
              Инфраструктуры БАС
            </span>
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-300 leading-relaxed font-light">
            Единая государственная платформа «Горизонт»: маркетплейс, биржа тендеров, реестр коммерческих операторов и моментальное согласование полётов через ЕС ОрВД.
          </p>

          <div className="mt-12 flex flex-col sm:flex-row gap-6 justify-center items-center">
            <Link href="/catalog" className="w-full sm:w-auto text-center px-10 py-4 border border-transparent text-lg font-bold rounded-xl text-black bg-gradient-to-r from-khokhloma-gold via-yellow-400 to-khokhloma-gold bg-size-200 animate-gradient shadow-[0_0_30px_rgba(245,176,65,0.4)] hover:shadow-[0_0_50px_rgba(245,176,65,0.6)] transition-all hover:-translate-y-1">
              Перейти к сервисам
            </Link>
            <Link href="/map" className="w-full sm:w-auto text-center px-8 py-4 border border-white/10 text-lg font-medium rounded-xl text-white bg-white/5 hover:bg-white/10 backdrop-blur-md transition-all hover:-translate-y-1 flex items-center justify-center gap-2">
              <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Интерактивный Радар
            </Link>
          </div>
        </div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 mt-20 mb-32 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-[#111111]/80 border border-white/5 p-8 rounded-2xl backdrop-blur-xl hover:bg-white/5 hover:border-khokhloma-gold/30 transition-all group shadow-2xl">
          <div className="h-14 w-14 rounded-xl bg-khokhloma-gold/10 text-khokhloma-gold flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Национальный реестр</h3>
          <p className="text-gray-400 leading-relaxed">Безопасные контракты и прозрачная система верификации подрядчиков и исполнителей авиационных работ.</p>
        </div>
        <div className="bg-[#111111]/80 border border-white/5 p-8 rounded-2xl backdrop-blur-xl hover:bg-white/5 hover:border-tricolor-blue/30 transition-all group shadow-2xl">
          <div className="h-14 w-14 rounded-xl bg-tricolor-blue/10 text-tricolor-blue flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Академия БАС</h3>
          <p className="text-gray-400 leading-relaxed">Система подготовки и повышения квалификации специалистов с выдачей сертификатов гос. образца.</p>
        </div>
        <div className="bg-[#111111]/80 border border-white/5 p-8 rounded-2xl backdrop-blur-xl hover:bg-white/5 hover:border-khokhloma-red/30 transition-all group shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-khokhloma-red/5 rounded-bl-[100px] pointer-events-none"></div>
          <div className="h-14 w-14 rounded-xl bg-khokhloma-red/10 text-khokhloma-red flex items-center justify-center mb-6 group-hover:scale-110 transition-transform relative z-10">
            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-white mb-2 relative z-10">Легальные Полеты</h3>
          <p className="text-gray-400 leading-relaxed relative z-10">Полная интеграция с ЕС ОрВД для автоматической отправки планов полета и согласования местных режимов.</p>
        </div>
      </div>
    </div>
  );
}
