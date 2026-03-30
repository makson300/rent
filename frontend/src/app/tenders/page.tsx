"use client";

import { useEffect, useState } from "react";
import { Briefcase, MapPin, Clock, ShieldCheck, FileText, CheckCircle2, ChevronRight, X, ShoppingCart, Zap } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function TendersPage() {
  const [tenders, setTenders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTender, setSelectedTender] = useState<any>(null);
  const [bidFormOpen, setBidFormOpen] = useState(false);
  const [priceOffer, setPriceOffer] = useState("");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchTenders = async () => {
    try {
      const data = await api.get<any[]>("/tenders");
      if (Array.isArray(data)) setTenders(data);
    } catch {
      console.error("Error fetching tenders");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTenders();
  }, []);

  const handleOpenTender = async (tenderId: number) => {
    try {
      const data = await api.get<any>(`/tenders/${tenderId}`);
      if (data.id) {
        setSelectedTender(data);
        setBidFormOpen(false);
      }
    } catch {
      console.error("Error opening tender");
    }
  };

  const submitBid = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTender) return;
    setSubmitting(true);
    try {
      const payload = {
        contractor_id: 1,
        price_offer: parseInt(priceOffer.replace(/\D/g, "")),
        comment: comment
      };
      const data = await api.post<{ ok: boolean }>(`/tenders/${selectedTender.id}/bid`, payload);
      if (data.ok) {
        setBidFormOpen(false);
        setPriceOffer("");
        setComment("");
        await handleOpenTender(selectedTender.id);
      }
    } catch {
      console.error("Error submitting bid");
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(num);
  };

  return (
    <div className="flex-1 p-8 md:p-12 overflow-y-auto relative bg-[#0A0A0B] min-h-screen text-white">
      {/* Decorative corporate bg */}
      <div 
        className="absolute top-0 right-0 w-full h-[600px] bg-pattern-tricolor opacity-5 pointer-events-none" 
        style={{ maskImage: "linear-gradient(to bottom, black, transparent)", WebkitMaskImage: "linear-gradient(to bottom, black, transparent)" }}
      ></div>

      <div className="relative z-10 max-w-7xl mx-auto flex flex-col md:flex-row gap-8">
        {/* Left Column - List of Tenders */}
        <div className="flex-1 w-full md:w-2/3">
          <header className="mb-8">
             <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-tricolor-blue/10 border border-tricolor-blue/20 text-tricolor-blue text-xs font-bold uppercase tracking-wider mb-4">
               <ShieldCheck className="w-4 h-4" /> B2B Портал Торгов
             </div>
             <h1 className="text-4xl font-extrabold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-tricolor-white to-gray-500">
               Коммерческие Тендеры
             </h1>
             <p className="text-gray-400">
               Официальный реестр заказов на аэромоделирование, геосъемку и патрулирование. 
               Принимайте участие в закупках и получайте корпоративные контракты.
             </p>
          </header>

          {loading ? (
             <div className="grid gap-4">
               {[1, 2, 3].map(i => (
                 <div key={i} className="h-32 bg-white/5 rounded-2xl animate-pulse"></div>
               ))}
             </div>
          ) : tenders.length === 0 ? (
             <div className="p-12 text-center rounded-2xl border border-dashed border-white/10 bg-white/5">
                <FileText className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold mb-2">Актуальных тендеров нет</h3>
                <p className="text-gray-400">Новые закупки появятся здесь в ближайшее время.</p>
             </div>
          ) : (
             <div className="grid gap-4">
               {tenders.map((t) => (
                 <div 
                   key={t.id} 
                   className={`p-6 rounded-2xl border transition-all cursor-pointer group ${selectedTender?.id === t.id ? 'border-tricolor-blue bg-tricolor-blue/5' : 'border-white/10 bg-[#121214] hover:bg-white/5 hover:border-white/20'}`}
                   onClick={() => handleOpenTender(t.id)}
                 >
                    <div className="flex justify-between items-start mb-3">
                       <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-tricolor-blue/20 text-blue-400 rounded-md">
                         {t.region}
                       </span>
                       <span className="text-lg font-bold text-emerald-400 font-mono">
                         {formatCurrency(t.budget)}
                       </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                      {t.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-gray-500">
                      <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" /> {t.region}</span>
                      <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" /> До {t.deadline ? new Date(t.deadline).toLocaleDateString("ru-RU") : "Бессрочно"}</span>
                    </div>
                 </div>
               ))}
             </div>
          )}
        </div>

        {/* Right Column - Tender Details Panel */}
        <div className="w-full md:w-1/3">
           {!selectedTender ? (
              <div className="sticky top-12 p-8 rounded-2xl border border-dashed border-white/10 bg-white/5 flex flex-col items-center justify-center text-center h-[500px]">
                 <Briefcase className="w-16 h-16 text-white/20 mb-4" />
                 <h3 className="text-lg font-bold text-gray-400">Выберите тендер в списке</h3>
                 <p className="text-sm text-gray-500 mt-2">Здесь появится детализация закупки, документы и форма подачи закрытого конверта со ставкой.</p>
              </div>
           ) : (
              <div className="sticky top-12 bg-[#141416] border border-tricolor-blue/30 rounded-2xl shadow-2xl flex flex-col h-[calc(100vh-100px)]">
                 <div className="p-6 border-b border-white/10 overflow-y-auto flex-1">
                    <div className="flex justify-between items-start mb-4">
                       <h2 className="text-2xl font-bold">{selectedTender.title}</h2>
                       <button onClick={() => setSelectedTender(null)} className="text-gray-500 hover:text-white transition-colors">
                          <X className="w-5 h-5" />
                       </button>
                    </div>
                    
                    <div className="mb-6 p-4 rounded-xl bg-tricolor-blue/10 border border-tricolor-blue/20">
                       <div className="text-xs text-tricolor-blue font-bold uppercase tracking-wider mb-1">НМЦК</div>
                       <div className="text-3xl font-mono text-white font-extrabold">{formatCurrency(selectedTender.budget)}</div>
                    </div>

                    <h4 className="text-sm text-gray-400 uppercase tracking-widest font-bold mb-3">Описание закупки</h4>
                    <p className="text-gray-300 text-sm leading-relaxed mb-6 whitespace-pre-wrap">
                      {selectedTender.description || "Заказчик не оставил детального описания. Ознакомьтесь с приложенной документацией."}
                    </p>

                    <h4 className="text-sm text-gray-400 uppercase tracking-widest font-bold mb-3">Сводка торгов</h4>
                    <div className="space-y-4">
                       <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 text-sm font-mono">
                          <span className="text-gray-400">Статус</span>
                          <span className="text-emerald-400 font-bold uppercase flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> Прием заявок</span>
                       </div>
                       <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 text-sm font-mono">
                          <span className="text-gray-400">Дедлайн рассмотрения</span>
                          <span className="text-white">{selectedTender.deadline ? new Date(selectedTender.deadline).toLocaleString("ru-RU") : "Открыто"}</span>
                       </div>
                       <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 text-sm font-mono">
                          <span className="text-gray-400">Подано предложений (закрытые)</span>
                          <span className="text-white font-bold">{selectedTender.total_bids || 0} шт.</span>
                       </div>

                       {/* List of anonymous bids */}
                       {(selectedTender.bids?.length > 0) && (
                         <div className="mt-4">
                           <h5 className="text-xs text-gray-500 uppercase font-bold mb-2">Конкурентные ставки:</h5>
                           {selectedTender.bids.map((b: any, idx: number) => (
                             <div key={b.id} className="flex justify-between items-center text-xs p-2 border-b border-white/5 last:border-0 font-mono text-gray-400">
                               <span>Участник #{idx + 1}</span>
                               <span className="text-white">{formatCurrency(b.price_offer)}</span>
                             </div>
                           ))}
                         </div>
                       )}
                     </div>

                     {/* === Cross-sell: Оборудование для задачи === */}
                     {selectedTender.recommended_drones?.length > 0 && (
                       <div className="mt-6 pt-5 border-t border-white/5">
                         <div className="flex items-center gap-2 mb-3">
                           <Zap className="w-4 h-4 text-khokhloma-gold" />
                           <h4 className="text-sm font-bold uppercase tracking-widest text-khokhloma-gold">
                             Оборудование для задачи
                           </h4>
                         </div>
                         <div className="space-y-2">
                           {selectedTender.recommended_drones.map((drone: any) => (
                             <div
                               key={drone.id}
                               className="flex items-center gap-3 p-3 rounded-xl bg-khokhloma-red/5 border border-khokhloma-gold/20 hover:border-khokhloma-gold/50 transition-all group/drone"
                             >
                               <div className="w-8 h-8 rounded-lg bg-khokhloma-gold/10 flex items-center justify-center flex-shrink-0 text-lg">
                                 🚁
                               </div>
                               <div className="flex-1 min-w-0">
                                 <p className="text-sm font-semibold text-white truncate">{drone.title}</p>
                                 <p className="text-xs text-gray-500 font-mono">
                                   {drone.listing_type === "rental" ? "🔄 Аренда" : "🛒 Продажа"} · {drone.city}
                                 </p>
                               </div>
                               <Link
                                 href="/catalog"
                                 className="flex-shrink-0 px-2.5 py-1.5 bg-khokhloma-gold/10 hover:bg-khokhloma-gold/20 border border-khokhloma-gold/30 text-khokhloma-gold rounded-lg text-xs font-bold transition-all flex items-center gap-1 group-hover/drone:shadow-[0_0_10px_rgba(212,175,55,0.2)]"
                               >
                                 <ShoppingCart className="w-3 h-3" /> Под заказ
                               </Link>
                             </div>
                           ))}
                         </div>
                       </div>
                     )}
                  </div>

                 <div className="p-6 bg-[#0A0A0B] rounded-b-2xl border-t border-white/10">
                    {!bidFormOpen ? (
                       <button 
                         className="w-full py-4 bg-tricolor-blue hover:bg-blue-600 text-white font-bold rounded-xl flex justify-center items-center gap-2 transition-colors shadow-[0_0_20px_rgba(59,130,246,0.2)]"
                         onClick={() => setBidFormOpen(true)}
                       >
                          Участвовать в закупке <ChevronRight className="w-5 h-5" />
                       </button>
                    ) : (
                       <form onSubmit={submitBid} className="space-y-4 animate-in fade-in slide-in-from-bottom-4">
                          <h4 className="font-bold text-white mb-2">Сформировать закрытую ставку</h4>
                          <div>
                            <label className="block text-xs text-gray-500 mb-1">Предлагаемая цена (Руб)</label>
                            <input 
                              type="text"
                              value={priceOffer}
                              onChange={(e) => setPriceOffer(e.target.value)}
                              className="w-full bg-[#1A1A1D] border border-white/10 rounded-lg p-3 text-white font-mono focus:border-tricolor-blue focus:outline-none"
                              placeholder={`Например: ${selectedTender.budget * 0.9}`}
                              required
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-500 mb-1">Опыт и сроки (КП)</label>
                            <textarea 
                              value={comment}
                              onChange={(e) => setComment(e.target.value)}
                              className="w-full bg-[#1A1A1D] border border-white/10 rounded-lg p-3 text-white text-sm focus:border-tricolor-blue focus:outline-none resize-none"
                              placeholder="Кратко опишите, почему вы подходите для этого заказа и за сколько дней выполните."
                              rows={3}
                            ></textarea>
                          </div>
                          <div className="flex gap-2 pt-2">
                            <button 
                              type="button" 
                              className="w-1/3 py-3 border border-white/10 text-white hover:bg-white/5 rounded-xl text-sm font-bold transition-colors"
                              onClick={() => setBidFormOpen(false)}
                            >
                              Отмена
                            </button>
                            <button 
                              type="submit" 
                              disabled={submitting || !priceOffer}
                              className="w-2/3 py-3 bg-tricolor-blue hover:bg-blue-600 text-white rounded-xl text-sm font-bold transition-colors shadow-lg disabled:opacity-50 flex justify-center items-center"
                            >
                              {submitting ? "Отправка..." : "Отправить ставку"}
                            </button>
                          </div>
                       </form>
                    )}
                 </div>
              </div>
           )}
        </div>
      </div>
    </div>
  );
}
