"use client";

import { useState, useEffect } from "react";
import { Briefcase, Building2, MapPin, Calendar, Banknote, ShieldCheck, FileCheck, ArrowRight, Loader2 } from "lucide-react";
import { toast } from "react-hot-toast";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

interface Tender {
  id: number;
  employer_id: number;
  title: string;
  description: string;
  category: string;
  budget: number;
  deadline: string;
  status: string;
  region: string;
  created_at: string;
}

export default function TendersPage() {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);
  const [biddingId, setBiddingId] = useState<number | null>(null);
  const [userId, setUserId] = useState<number | null>(null);

  const [priceOffers, setPriceOffers] = useState<Record<number, number>>({});

  useEffect(() => {
    // Get logged in user telegram ID
    const userStr = localStorage.getItem("skyrent_user");
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        setUserId(u.telegram_id || u.id);
      } catch {}
    } else {
        // Fallback to system mock for testing
        setUserId(0);
    }

    fetchTenders();
  }, []);

  const fetchTenders = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/tenders`);
      if (res.ok) {
        const data = await res.json();
        setTenders(data.tenders || []);
      }
    } catch {
      toast.error("Ошибка при загрузке тендеров");
    } finally {
      setLoading(false);
    }
  };

  const setTenderPrice = (id: number, val: number) => {
    setPriceOffers(prev => ({ ...prev, [id]: val }));
  };

  const handleBid = async (tender: Tender) => {
    if (!userId) {
      toast.error("Пожалуйста, войдите в систему");
      return;
    }

    const offer = priceOffers[tender.id] || tender.budget;

    setBiddingId(tender.id);
    try {
      const res = await fetch(`${API_BASE}/api/v1/tenders/bid`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tender_id: tender.id,
          contractor_id: userId,
          price_offer: offer, 
          comment: "Отклик с платформы 'Горизонт Хаб'. Техника готова.",
        }),
      });

      const json = await res.json();
      if (res.ok && json.ok) {
        toast.success("Ваша заявка успешно подана! Средства холдированы.");
      } else {
        if (json.ai_reason) {
          toast.error(`⚠️ Блокировка AI Анти-Демпинг: ${json.ai_reason}`, { duration: 6000 });
        } else {
          toast.error(json.error || "Ошибка при подаче заявки. Проверьте баланс.");
        }
      }
    } catch (e) {
      toast.error("Не удалось связаться с сервером");
    } finally {
      setBiddingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 transition-all">
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <span className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-3 inline-block">
            Национальная Экосистема БАС
          </span>
          <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
            <Briefcase className="w-8 h-8 text-indigo-400" />
            Госконтракты и B2B
          </h1>
          <p className="text-gray-400 max-w-2xl text-lg">
             Участвуйте в крупных тендерах по выполнению авиационных работ. 
             Защита от демпинга контролируется нейросетью. Обеспечение 5%.
          </p>
        </div>
        <div className="flex bg-[#121214] p-1 rounded-xl border border-white/5">
            <button className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-500 text-white shadow-lg">
                Все заказы
            </button>
            <button className="px-4 py-2 text-sm font-medium rounded-lg text-gray-400 hover:text-white transition-colors">
                Мои отклики
            </button>
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-indigo-500">
          <Loader2 className="w-12 h-12 animate-spin mb-4" />
          <p>Загрузка Реестра контрактов...</p>
        </div>
      ) : tenders.length === 0 ? (
        <div className="text-center py-20 bg-white/5 rounded-2xl border border-white/10">
          <p className="text-gray-400">Активных тендеров не найдено.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {tenders.map((tender) => {
            const offer = priceOffers[tender.id] || tender.budget;
            const requiredSecurity = offer * 0.05;
            
            return (
              <div 
                key={tender.id} 
                className="bg-[#0A0A0B] border border-white/10 rounded-3xl p-6 lg:p-8 hover:border-indigo-500/30 transition-all group relative overflow-hidden"
              >
                {/* Visual Flair */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full filter blur-3xl opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <div className="flex flex-col lg:flex-row gap-8 relative z-10">
                  <div className="flex-1 space-y-4">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="px-2.5 py-1 text-xs font-black uppercase tracking-wider rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                            <ShieldCheck className="w-3.5 h-3.5" /> ФЗ-44 / B2B
                        </span>
                        <span className="px-2.5 py-1 text-xs font-bold rounded-md bg-white/10 text-gray-300">
                            ID: {tender.id}
                        </span>
                        <span className="px-2.5 py-1 text-xs font-bold uppercase rounded-md bg-blue-500/20 text-blue-400">
                            {tender.category}
                        </span>
                    </div>

                    <h2 className="text-2xl font-bold text-white leading-tight">
                        {tender.title}
                    </h2>
                    
                    <p className="text-gray-400 text-sm leading-relaxed max-w-3xl">
                        {tender.description}
                    </p>

                    <div className="flex flex-wrap items-center gap-6 mt-4 opacity-80">
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                            <MapPin className="w-4 h-4 text-indigo-400" />
                            {tender.region}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                            <Building2 className="w-4 h-4 text-indigo-400" />
                            Заказчик: скрыт (Конфиденциально)
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                            <Calendar className="w-4 h-4 text-indigo-400" />
                            Дедлайн: {new Date(tender.deadline).toLocaleDateString("ru-RU")}
                        </div>
                    </div>
                  </div>

                  <div className="w-full lg:w-[320px] shrink-0 bg-[#121214] rounded-2xl border border-white/5 p-6 flex flex-col justify-center">
                     <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-1 flex items-center gap-1">НМЦК (Бюджет)</p>
                     <div className="text-3xl font-black text-white mb-6">
                        {tender.budget.toLocaleString("ru-RU")} ₽
                     </div>
                     
                     <div className="space-y-4 mb-6">
                         <div>
                            <label className="text-xs text-gray-400 mb-1 block">Ваше предложение (Демпинг карается AI) 🤖</label>
                            <input 
                               type="number" 
                               min="1000"
                               value={priceOffers[tender.id] || tender.budget}
                               onChange={(e) => setTenderPrice(tender.id, parseInt(e.target.value) || 0)}
                               className="w-full bg-[#1A1A1D] border border-white/10 focus:border-indigo-500 outline-none text-white rounded-lg px-3 py-2 text-sm font-mono"
                            />
                         </div>
                         <div className="flex justify-between items-center text-sm">
                             <span className="text-gray-400 flex items-center gap-1">
                                 <FileCheck className="w-4 h-4" /> Холд (5%)
                             </span>
                             <span className="text-emerald-400 font-mono font-bold">
                                 {requiredSecurity.toLocaleString('ru-RU')} ₽
                             </span>
                         </div>
                     </div>

                     <button
                        onClick={() => handleBid(tender)}
                        disabled={biddingId === tender.id}
                        className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50 flex items-center justify-center gap-2 group-hover:scale-[1.02]"
                     >
                         {biddingId === tender.id ? (
                             <><Loader2 className="w-5 h-5 animate-spin"/> Обработка AI...</>
                         ) : (
                             <>Откликнуться <ArrowRight className="w-5 h-5" /></>
                         )}
                     </button>
                     <p className="text-center text-[10px] text-gray-500 mt-3 flex items-center justify-center gap-1">
                         <Banknote className="w-3 h-3" /> Средства холдируются Гарантом
                     </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
