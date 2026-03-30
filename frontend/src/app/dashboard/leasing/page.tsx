"use client";

import { useState } from "react";
import {
  Plane, ShieldCheck, Banknote, Clock, CheckCircle,
  ChevronRight, Sparkles, Building2, Star, AlertTriangle,
  Cpu, FileText, ArrowRight, Loader2, BarChart2, Zap
} from "lucide-react";
import { toast } from "react-hot-toast";
import DroneLoader from "@/components/DroneLoader";
import { leasingApi } from "@/lib/api";

// Каталог дронов доступных в лизинг
const LEASING_CATALOG = [
  {
    id: 1,
    model: "DJI Matrice 350 RTK",
    category: "Топографическая Съёмка / Инспекция",
    price: 1_850_000,
    monthly_payment: 68_000,
    term_months: 36,
    down_payment_pct: 15,
    image_emoji: "🛰️",
    specs: ["Дальность 20 км", "Полезная нагрузка 2.7 кг", "IP45"],
    suitable_for: ["Кадастровые работы", "Инспекция ЛЭП", "Геодезия"],
    in_stock: 3,
    tender_match_count: 12,
    tender_match_sum: 3_400_000,
    rating: 4.9,
  },
  {
    id: 2,
    model: "Геоскан 401",
    category: "Агро / Опрыскивание",
    price: 2_200_000,
    monthly_payment: 81_000,
    term_months: 36,
    down_payment_pct: 10,
    image_emoji: "🌾",
    specs: ["Бак 40 л", "Ширина захвата 9 м", "RTK точность"],
    suitable_for: ["Внесение СЗР", "Агромониторинг", "Госзаказы МСХ"],
    in_stock: 1,
    tender_match_count: 8,
    tender_match_sum: 5_100_000,
    rating: 4.7,
  },
  {
    id: 3,
    model: "БПЛА Орлан-10Е (гражданский)",
    category: "БВЛОС / Мониторинг",
    price: 4_800_000,
    monthly_payment: 142_000,
    term_months: 48,
    down_payment_pct: 20,
    image_emoji: "✈️",
    specs: ["Дальность 120 км", "Налёт 14 ч", "Видение 360°"],
    suitable_for: ["Мониторинг трубопроводов", "ЧС / МЧС", "Картография"],
    in_stock: 1,
    tender_match_count: 5,
    tender_match_sum: 18_000_000,
    rating: 4.8,
  },
  {
    id: 4,
    model: "DJI Agras T50",
    category: "Агро / Премиум",
    price: 1_650_000,
    monthly_payment: 57_000,
    term_months: 36,
    down_payment_pct: 10,
    image_emoji: "🚜",
    specs: ["Бак 50 л", "8 форсунок", "AI Spot Check"],
    suitable_for: ["Точное земледелие", "Малые КФХ", "Субсидии РФ"],
    in_stock: 5,
    tender_match_count: 19,
    tender_match_sum: 2_800_000,
    rating: 4.6,
  },
];

// Активные тендеры-подсказки (гарантированные заказы)
const GUARANTEED_TENDERS = [
  {
    id: 101,
    title: "Аэрофотосъёмка Кадастрового квартала — г. Казань",
    budget: 780_000,
    deadline: "2026-06-15",
    requires: "DJI Matrice 350 RTK",
    status: "collecting",
    region: "Татарстан",
  },
  {
    id: 102,
    title: "Обработка полей СЗР — Краснодарский край (8000 га)",
    budget: 1_240_000,
    deadline: "2026-05-01",
    requires: "Геоскан 401 / T50",
    status: "collecting",
    region: "Краснодарский край",
  },
  {
    id: 103,
    title: "Мониторинг нефтепровода Самара-Уфа",
    budget: 3_600_000,
    deadline: "2026-07-30",
    requires: "БВЛОС 100+ км",
    status: "collecting",
    region: "Самарская область",
  },
];

function RoiBadge({ months, tender_sum, monthly }: { months: number; tender_sum: number; monthly: number }) {
  const total_paid = monthly * months;
  const roi = Math.round(((tender_sum - total_paid) / total_paid) * 100);
  return (
    <div className={`text-xs font-black px-2 py-0.5 rounded-full ${roi > 0 ? "bg-emerald-500/15 text-emerald-400" : "bg-red-500/15 text-red-400"}`}>
      ROI {roi > 0 ? "+" : ""}{roi}%
    </div>
  );
}

interface ApplicationForm {
  droneId: number | null;
  tenderId: number | null;
  company_name: string;
  inn: string;
  contact: string;
}

export default function LeasingPage() {
  const [selected, setSelected] = useState<number | null>(null);
  const [step, setStep] = useState<"catalog" | "form" | "success">("catalog");
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<ApplicationForm>({
    droneId: null,
    tenderId: null,
    company_name: "",
    inn: "",
    contact: "",
  });

  const drone = LEASING_CATALOG.find((d) => d.id === selected);

  const handleApply = async () => {
    if (!form.company_name || !form.inn) {
      toast.error("Заполните название компании и ИНН");
      return;
    }
    if (!drone) return;
    setSubmitting(true);
    try {
      await leasingApi.create({
        company_name: form.company_name,
        inn: form.inn,
        contact_email: form.contact.includes("@") && !form.contact.startsWith("@")
          ? form.contact
          : `pilot@${form.inn}.ru`,          // фоллбэк если ввели telegram
        contact_phone: form.contact,
        drone_model: drone.model,
        tender_guarantee_id: form.tenderId ? String(form.tenderId) : undefined,
        requested_amount_rub: drone.price,
      });
      setStep("success");
      toast.success("Заявка на лизинг принята! Менеджер свяжется в течение 2 часов.");
    } catch (err: unknown) {
      const e = err as { detail?: string };
      toast.error(e.detail ?? "Ошибка при подаче заявки");
    } finally {
      setSubmitting(false);
    }
  };


  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-amber-500/15 text-amber-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5" /> Фаза 36 · B2B Инфраструктура
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Plane className="w-8 h-8 text-amber-400" />
          Лизинг Дронов под Госзаказ
        </h1>
        <p className="text-gray-400 max-w-3xl text-lg">
          Получите дрон в лизинг под гарантированный тендер с платформы{" "}
          <span className="text-amber-400 font-bold">Горизонт</span>. Залог — это сам госконтракт. Одобрение за 2 часа.
        </p>
      </div>

      {step === "success" ? (
        /* Success Screen */
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="w-24 h-24 rounded-3xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center mb-6">
            <CheckCircle className="w-12 h-12 text-emerald-400" />
          </div>
          <h2 className="text-3xl font-black text-white mb-3">Заявка принята!</h2>
          <p className="text-gray-400 text-lg mb-2 max-w-md">
            Менеджер лизинговой службы свяжется с вами по указанному контакту в течение{" "}
            <span className="text-amber-400 font-bold">2 часов</span>.
          </p>
          <p className="text-gray-600 text-sm mb-8">
            Средства по первому платежу будут зарезервированы из эскроу-гарантии по тендеру.
          </p>
          <button
            onClick={() => { setStep("catalog"); setSelected(null); }}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition-all"
          >
            Вернуться в каталог
          </button>
        </div>
      ) : step === "form" && drone ? (
        /* Application Form */
        <div className="max-w-2xl mx-auto">
          <button
            onClick={() => setStep("catalog")}
            className="text-gray-500 hover:text-white text-sm mb-6 flex items-center gap-1 transition-colors"
          >
            ← Вернуться к каталогу
          </button>

          <div className="bg-[#0E0E10] border border-amber-500/20 rounded-3xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-14 h-14 rounded-2xl bg-amber-500/10 flex items-center justify-center text-3xl">
                {drone.image_emoji}
              </div>
              <div>
                <h2 className="text-xl font-black text-white">{drone.model}</h2>
                <p className="text-gray-500 text-sm">{drone.category}</p>
              </div>
            </div>

            {/* Leasing Summary */}
            <div className="grid grid-cols-3 gap-3 mb-6">
              {[
                { label: "Стоимость", val: `${(drone.price / 1_000_000).toFixed(2)}M ₽` },
                { label: "Платёж/мес", val: `${drone.monthly_payment.toLocaleString("ru-RU")} ₽` },
                { label: "Срок", val: `${drone.term_months} мес.` },
              ].map((s, i) => (
                <div key={i} className="bg-[#121214] rounded-xl p-3 text-center border border-white/5">
                  <div className="text-xs text-gray-500 mb-1">{s.label}</div>
                  <div className="font-black text-white text-sm">{s.val}</div>
                </div>
              ))}
            </div>

            {/* Guaranteed Tender Selector */}
            <div className="mb-5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Привязать к Тендеру-Гаранту (опционально)
              </label>
              <div className="space-y-2">
                {GUARANTEED_TENDERS.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setForm(prev => ({ ...prev, tenderId: prev.tenderId === t.id ? null : t.id }))}
                    className={`w-full flex items-start justify-between p-3 rounded-xl border text-left transition-all ${
                      form.tenderId === t.id
                        ? "bg-emerald-500/10 border-emerald-500/40 text-white"
                        : "bg-[#121214] border-white/5 text-gray-400 hover:border-white/10"
                    }`}
                  >
                    <div>
                      <div className="font-bold text-sm text-white">{t.title}</div>
                      <div className="text-xs text-gray-500">{t.region} · до {new Date(t.deadline).toLocaleDateString("ru-RU")}</div>
                    </div>
                    <div className="text-emerald-400 font-black text-sm shrink-0 ml-3">
                      {t.budget.toLocaleString("ru-RU")} ₽
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Company Details */}
            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Название компании / ИП</label>
                <input
                  value={form.company_name}
                  onChange={e => setForm(prev => ({ ...prev, company_name: e.target.value }))}
                  placeholder='ООО "АэроТех"'
                  className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm transition-colors"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">ИНН</label>
                <input
                  value={form.inn}
                  onChange={e => setForm(prev => ({ ...prev, inn: e.target.value }))}
                  placeholder="7702000001"
                  className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm font-mono transition-colors"
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Telegram / Телефон для связи</label>
                <input
                  value={form.contact}
                  onChange={e => setForm(prev => ({ ...prev, contact: e.target.value }))}
                  placeholder="@username или +7..."
                  className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm transition-colors"
                />
              </div>
            </div>

            <button
              onClick={handleApply}
              disabled={submitting}
              className="w-full mt-6 py-4 bg-amber-500 hover:bg-amber-400 text-black font-black rounded-xl transition-all shadow-lg shadow-amber-500/20 disabled:opacity-50 flex items-center justify-center gap-2 text-base"
            >
              {submitting ? (
                <><Loader2 className="w-5 h-5 animate-spin" /> Обработка заявки...</>
              ) : (
                <>Подать заявку на Лизинг <ArrowRight className="w-5 h-5" /></>
              )}
            </button>
            <p className="text-center text-[11px] text-gray-600 mt-3">
              Первый взнос ({drone.down_payment_pct}%) может быть выплачен из средств эскроу по выбранному тендеру
            </p>
          </div>
        </div>
      ) : (
        /* Catalog View */
        <>
          {/* Guaranteed Tenders Banner */}
          <div className="bg-[#0A0A0B] border border-emerald-500/20 rounded-2xl p-5 mb-8">
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <h2 className="font-black text-white text-sm uppercase tracking-wider">Тендеры с Гарантией (Доступны Прямо Сейчас)</h2>
              <span className="ml-auto text-xs text-emerald-400 font-bold">{GUARANTEED_TENDERS.length} открытых контракта</span>
            </div>
            <div className="flex flex-wrap gap-3">
              {GUARANTEED_TENDERS.map((t) => (
                <div key={t.id} className="flex items-center gap-2 bg-emerald-500/5 border border-emerald-500/15 rounded-xl px-3 py-2">
                  <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
                  <span className="text-xs text-gray-300 font-bold">{t.title.substring(0, 45)}...</span>
                  <span className="text-xs text-emerald-400 font-black">{(t.budget / 1000).toFixed(0)}к ₽</span>
                </div>
              ))}
            </div>
          </div>

          {/* Drone Catalog Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {LEASING_CATALOG.map((drone) => {
              const downPayment = Math.round(drone.price * drone.down_payment_pct / 100);
              const isSelected = selected === drone.id;

              return (
                <div
                  key={drone.id}
                  className={`bg-[#0A0A0B] border rounded-3xl overflow-hidden transition-all cursor-pointer group relative ${
                    isSelected ? "border-amber-500/50 shadow-lg shadow-amber-500/10" : "border-white/10 hover:border-white/20"
                  }`}
                  onClick={() => setSelected(isSelected ? null : drone.id)}
                >
                  {/* Glow */}
                  <div className="absolute top-0 left-0 w-full h-full bg-amber-500/3 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none rounded-3xl" />

                  <div className="p-6 relative z-10">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center text-3xl">
                          {drone.image_emoji}
                        </div>
                        <div>
                          <div className="font-black text-white text-lg leading-tight">{drone.model}</div>
                          <div className="text-xs text-gray-500">{drone.category}</div>
                          <div className="flex items-center gap-1 mt-0.5">
                            <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                            <span className="text-xs text-amber-400 font-bold">{drone.rating}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-500 mb-0.5">В наличии</div>
                        <div className={`font-black text-sm ${drone.in_stock > 0 ? "text-emerald-400" : "text-red-400"}`}>
                          {drone.in_stock} шт.
                        </div>
                      </div>
                    </div>

                    {/* Specs pills */}
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {drone.specs.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 text-[11px] bg-white/5 text-gray-400 rounded-md border border-white/5">
                          {s}
                        </span>
                      ))}
                    </div>

                    {/* Financials */}
                    <div className="grid grid-cols-2 gap-3 mb-4">
                      <div className="bg-[#121214] rounded-xl p-3 border border-white/5">
                        <div className="text-[10px] text-gray-500 mb-0.5 flex items-center gap-1">
                          <Banknote className="w-3 h-3" /> Ежемесячно
                        </div>
                        <div className="font-black text-white">{drone.monthly_payment.toLocaleString("ru-RU")} ₽</div>
                        <div className="text-[10px] text-gray-600">{drone.term_months} мес.</div>
                      </div>
                      <div className="bg-[#121214] rounded-xl p-3 border border-white/5">
                        <div className="text-[10px] text-gray-500 mb-0.5 flex items-center gap-1">
                          <Building2 className="w-3 h-3" /> Первый взнос
                        </div>
                        <div className="font-black text-white">{downPayment.toLocaleString("ru-RU")} ₽</div>
                        <div className="text-[10px] text-gray-600">{drone.down_payment_pct}% от цены</div>
                      </div>
                    </div>

                    {/* Tender Match (ROI Hook) */}
                    <div className="bg-emerald-500/5 border border-emerald-500/15 rounded-2xl p-3 mb-4">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-black">
                          <BarChart2 className="w-3.5 h-3.5" />
                          Подходит для {drone.tender_match_count} тендеров на сумму
                        </div>
                        <RoiBadge
                          months={drone.term_months}
                          tender_sum={drone.tender_match_sum}
                          monthly={drone.monthly_payment}
                        />
                      </div>
                      <div className="text-lg font-black text-emerald-400">{drone.tender_match_sum.toLocaleString("ru-RU")} ₽</div>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {drone.suitable_for.map((s, i) => (
                          <span key={i} className="text-[10px] text-emerald-400/60 bg-emerald-500/5 px-1.5 py-0.5 rounded">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelected(drone.id);
                        setForm(prev => ({ ...prev, droneId: drone.id }));
                        setStep("form");
                      }}
                      className="w-full py-3.5 bg-amber-500 hover:bg-amber-400 text-black font-black rounded-xl transition-all shadow-lg shadow-amber-500/15 flex items-center justify-center gap-2"
                    >
                      <FileText className="w-4 h-4" />
                      Оформить Лизинг
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Info Footer */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { icon: <Clock className="w-5 h-5 text-indigo-400" />, title: "Одобрение за 2 часа", desc: "Проверка по базе ЕГРЮЛ и текущим тендерам на платформе" },
              { icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />, title: "Залог — Госконтракт", desc: "Активный тендер с эскроу-блокировкой средств заменяет залог имущества" },
              { icon: <Zap className="w-5 h-5 text-amber-400" />, title: "Без твёрдого залога", desc: "Покрытие первого взноса из суммы выигранного тендера" },
            ].map((f, i) => (
              <div key={i} className="bg-[#0E0E10] border border-white/5 rounded-2xl p-4 flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center shrink-0">{f.icon}</div>
                <div>
                  <div className="font-bold text-white text-sm mb-0.5">{f.title}</div>
                  <div className="text-xs text-gray-500">{f.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
