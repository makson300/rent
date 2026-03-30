"use client";

import { useState, useEffect } from "react";
import { Briefcase, Building2, MapPin, Calendar, Banknote, ShieldCheck, FileCheck, ArrowRight, Loader2, Cpu, Users, BarChart2, TrendingUp, Zap, ChevronDown, Star } from "lucide-react";
import DroneLoader from "@/components/DroneLoader";
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

// Mock respondents for "Заказчик" view
const MOCK_PILOTS = [
  { id: 1, name: "Игорь Самарин", rating: 4.9, flights: 312, drone: "DJI Matrice 300 RTK", trust: 97, offer: null },
  { id: 2, name: "ООО 'СкайТех'", rating: 4.7, flights: 891, drone: "Geoscan 201", trust: 91, offer: null },
  { id: 3, name: "Денис Кравцов", rating: 4.5, flights: 54, drone: "DJI Mavic 3E", trust: 78, offer: null },
];

// AI complexity heuristic based on budget
function getAiComplexity(budget: number): { label: string; color: string; score: number } {
  if (budget > 2_000_000) return { label: "Высокая сложность", color: "text-red-400 bg-red-500/10 border-red-500/30", score: 87 };
  if (budget > 500_000) return { label: "Средняя сложность", color: "text-amber-400 bg-amber-500/10 border-amber-500/30", score: 54 };
  return { label: "Низкая сложность", color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30", score: 23 };
}

export default function TendersPage() {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);
  const [biddingId, setBiddingId] = useState<number | null>(null);
  const [userId, setUserId] = useState<number | null>(null);
  const [mode, setMode] = useState<"contractor" | "employer">("contractor");
  const [expandedPilots, setExpandedPilots] = useState<number | null>(null);
  const [priceOffers, setPriceOffers] = useState<Record<number, number>>({});

  useEffect(() => {
    const userStr = localStorage.getItem("skyrent_user");
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        setUserId(u.telegram_id || u.id);
      } catch {}
    } else {
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
    } catch {
      toast.error("Не удалось связаться с сервером");
    } finally {
      setBiddingId(null);
    }
  };

  const [aiLoading, setAiLoading] = useState<number | null>(null);
  const handleAiRoute = async (tender: Tender) => {
    setAiLoading(tender.id);
    try {
      const res = await fetch(`${API_BASE}/api/v1/ai/route-calculator`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          drone_name: "DJI Mavic 3 Enterprise",
          battery_mah: 5000,
          payload_kg: 2.5,
          distance_km: (tender.budget / 100000) * 10,
          wind_ms: 5.5,
        }),
      });
      const data = await res.json();
      if (res.ok && data.ok) {
        const resObj = data.result;
        if (resObj.is_possible) {
          toast.success(`🤖 ИИ: Вылет возможен.\n${resObj.explanation}\nОстаток батареи: ${resObj.estimated_battery_left_percent}%`, { duration: 6000 });
        } else {
          toast.error(`🧨 ИИ: Энергии недостаточно.\n${resObj.explanation}`, { duration: 6000 });
        }
      } else {
        toast.error("Ошибка ИИ-сервиса маршрутизации");
      }
    } catch {
      toast.error("Не удалось подключиться к ИИ");
    } finally {
      setAiLoading(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
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
            {mode === "contractor"
              ? "Участвуйте в крупных тендерах. Защита от демпинга контролируется ИИ. Обеспечение 5%."
              : "Управляйте своими заказами. Просматривайте отклики исполнителей с рейтингом доверия."}
          </p>
        </div>

        {/* Mode Switcher */}
        <div className="flex bg-[#121214] p-1 rounded-xl border border-white/5 shrink-0">
          <button
            onClick={() => setMode("contractor")}
            className={`px-4 py-2 text-sm font-bold rounded-lg transition-all flex items-center gap-2 ${
              mode === "contractor" ? "bg-indigo-600 text-white shadow-lg" : "text-gray-400 hover:text-white"
            }`}
          >
            <Cpu className="w-4 h-4" /> Кабинет Исполнителя
          </button>
          <button
            onClick={() => setMode("employer")}
            className={`px-4 py-2 text-sm font-bold rounded-lg transition-all flex items-center gap-2 ${
              mode === "employer" ? "bg-amber-500 text-black shadow-lg" : "text-gray-400 hover:text-white"
            }`}
          >
            <Building2 className="w-4 h-4" /> Кабинет Заказчика
          </button>
        </div>
      </div>

      {/* Stats Bar (Employer mode) */}
      {mode === "employer" && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon: <BarChart2 className="w-5 h-5 text-indigo-400" />, label: "Активных тендеров", val: tenders.length },
            { icon: <Users className="w-5 h-5 text-emerald-400" />, label: "Всего откликов", val: tenders.length * 3 },
            { icon: <TrendingUp className="w-5 h-5 text-amber-400" />, label: "Средняя цена", val: tenders.length > 0 ? `${Math.round(tenders.reduce((s, t) => s + t.budget, 0) / tenders.length / 1000)}к ₽` : "—" },
            { icon: <Zap className="w-5 h-5 text-blue-400" />, label: "Экономия ИИ", val: "от 12%" },
          ].map((s, i) => (
            <div key={i} className="bg-[#0E0E10] border border-white/5 rounded-2xl p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center shrink-0">{s.icon}</div>
              <div>
                <div className="text-xs text-gray-500 mb-0.5">{s.label}</div>
                <div className="text-xl font-black text-white">{s.val}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-indigo-500">
          <DroneLoader text="Синхронизация..." subtext="Загрузка Реестра B2G контрактов" color="blue" />
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
            const complexity = getAiComplexity(tender.budget);
            const mockBids = Math.floor((tender.id * 7) % 11) + 2; // deterministic mock
            const isExpanded = expandedPilots === tender.id;

            return (
              <div
                key={tender.id}
                className="bg-[#0A0A0B] border border-white/10 rounded-3xl overflow-hidden hover:border-indigo-500/30 transition-all group relative"
              >
                {/* Glow */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full filter blur-3xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

                <div className="p-6 lg:p-8">
                  <div className="flex flex-col lg:flex-row gap-8 relative z-10">
                    {/* Left: Info */}
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
                        {/* AI Complexity Badge */}
                        <span className={`px-2.5 py-1 text-xs font-bold uppercase rounded-md border flex items-center gap-1 ${complexity.color}`}>
                          <Cpu className="w-3 h-3" /> {complexity.label}
                        </span>
                      </div>

                      <h2 className="text-2xl font-bold text-white leading-tight">{tender.title}</h2>
                      <p className="text-gray-400 text-sm leading-relaxed max-w-3xl">{tender.description}</p>

                      <div className="flex flex-wrap items-center gap-6 mt-4 opacity-80">
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                          <MapPin className="w-4 h-4 text-indigo-400" /> {tender.region}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                          <Building2 className="w-4 h-4 text-indigo-400" />
                          {mode === "employer" ? "Мой заказ" : "Заказчик: скрыт (Конфиденциально)"}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                          <Calendar className="w-4 h-4 text-indigo-400" />
                          Дедлайн: {new Date(tender.deadline).toLocaleDateString("ru-RU")}
                        </div>
                        {mode === "employer" && (
                          <div className="flex items-center gap-2 text-sm text-gray-300">
                            <Users className="w-4 h-4 text-emerald-400" />
                            <span className="text-emerald-400 font-bold">{mockBids} откликов</span>
                          </div>
                        )}
                      </div>

                      {/* AI Complexity Bar */}
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                          <span className="flex items-center gap-1"><TrendingUp className="w-3 h-3" /> ИИ-оценка сложности</span>
                          <span>{complexity.score}/100</span>
                        </div>
                        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${
                              complexity.score > 70 ? "bg-red-500" : complexity.score > 40 ? "bg-amber-500" : "bg-emerald-500"
                            }`}
                            style={{ width: `${complexity.score}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Right: Action Panel */}
                    {mode === "contractor" ? (
                      <div className="w-full lg:w-[320px] shrink-0 bg-[#121214] rounded-2xl border border-white/5 p-6 flex flex-col justify-center">
                        <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-1">НМЦК (Бюджет)</p>
                        <div className="text-3xl font-black text-white mb-6">{tender.budget.toLocaleString("ru-RU")} ₽</div>

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
                            <span className="text-emerald-400 font-mono font-bold">{requiredSecurity.toLocaleString("ru-RU")} ₽</span>
                          </div>
                        </div>

                        <div className="flex flex-col gap-2">
                          <button
                            onClick={() => handleAiRoute(tender)}
                            disabled={aiLoading === tender.id || biddingId === tender.id}
                            className="w-full py-3.5 bg-[#1A1A1D] hover:bg-[#252529] border border-white/5 text-khokhloma-gold font-bold rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                          >
                            {aiLoading === tender.id ? (
                              <><Loader2 className="w-5 h-5 animate-spin" /> Анализ...</>
                            ) : (
                              <><Cpu className="w-5 h-5" /> Справится ли мой дрон?</>
                            )}
                          </button>
                          <button
                            onClick={() => handleBid(tender)}
                            disabled={biddingId === tender.id}
                            className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50 flex items-center justify-center gap-2 group-hover:scale-[1.02]"
                          >
                            {biddingId === tender.id ? (
                              <><Loader2 className="w-5 h-5 animate-spin" /> Обработка AI...</>
                            ) : (
                              <>Откликнуться <ArrowRight className="w-5 h-5" /></>
                            )}
                          </button>
                        </div>

                        <p className="text-center text-[10px] text-gray-500 mt-3 flex items-center justify-center gap-1">
                          <Banknote className="w-3 h-3" /> Средства холдируются Гарантом
                        </p>
                      </div>
                    ) : (
                      /* Employer Mode: Budget + Manage */
                      <div className="w-full lg:w-[320px] shrink-0 bg-[#121214] rounded-2xl border border-amber-500/20 p-6 flex flex-col justify-center">
                        <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider mb-1">Бюджет заказа</p>
                        <div className="text-3xl font-black text-white mb-2">{tender.budget.toLocaleString("ru-RU")} ₽</div>
                        <div className="text-xs text-amber-400 font-bold mb-6">Ожидаемая экономия ИИ: ~{Math.round(tender.budget * 0.12).toLocaleString("ru-RU")} ₽</div>

                        <button
                          onClick={() => setExpandedPilots(isExpanded ? null : tender.id)}
                          className="w-full py-3 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 font-bold rounded-xl transition-all flex items-center justify-center gap-2"
                        >
                          <Users className="w-5 h-5" /> Список Откликов ({mockBids})
                          <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                        </button>
                        <button className="w-full mt-2 py-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 font-bold rounded-xl transition-all flex items-center justify-center gap-2 text-sm">
                          Закрыть тендер
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Expanded Pilots List (Employer mode) */}
                {mode === "employer" && isExpanded && (
                  <div className="border-t border-white/5 bg-[#0D0D0F] p-6">
                    <h3 className="text-sm font-black text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                      <Users className="w-4 h-4 text-amber-400" /> Откликнувшиеся Исполнители
                    </h3>
                    <div className="space-y-3">
                      {MOCK_PILOTS.map((pilot) => {
                        const pilotOffer = Math.round(tender.budget * (0.82 + pilot.id * 0.04));
                        return (
                          <div key={pilot.id} className="flex flex-col md:flex-row items-start md:items-center justify-between bg-[#121214] rounded-2xl p-4 border border-white/5 hover:border-white/10 transition-all gap-4">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center font-black text-indigo-400 text-sm">
                                {pilot.name.charAt(0)}
                              </div>
                              <div>
                                <div className="font-bold text-white text-sm">{pilot.name}</div>
                                <div className="text-xs text-gray-500">{pilot.drone} · {pilot.flights} полётов</div>
                              </div>
                            </div>
                            <div className="flex items-center gap-4 text-sm">
                              <div className="flex items-center gap-1 text-amber-400 font-bold">
                                <Star className="w-4 h-4 fill-amber-400" /> {pilot.rating}
                              </div>
                              <div className="flex items-center gap-1">
                                <div className="w-20 h-1.5 bg-white/5 rounded-full overflow-hidden">
                                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${pilot.trust}%` }} />
                                </div>
                                <span className="text-emerald-400 font-bold text-xs">{pilot.trust}%</span>
                              </div>
                              <div className="font-mono font-black text-white">{pilotOffer.toLocaleString("ru-RU")} ₽</div>
                              <button className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition-colors">
                                Выбрать
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
