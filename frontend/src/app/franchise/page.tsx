"use client";

import { useState } from "react";
import { Globe, ArrowRight, ShieldCheck, MapPin, Building2, Phone, Briefcase, Loader2, DollarSign } from "lucide-react";
import { toast } from "react-hot-toast";
import { api } from "@/lib/api";

// Жесткий белый список прямо на фронтенде
const FRIENDLY_COUNTRIES = [
    "Россия", "Беларусь", "Казахстан", "Китай", "ОАЭ", 
    "Сербия", "Индия", "Бразилия", "ЮАР", "Иран", "Куба", "Другое (БРИКС)"
];

export default function FranchisePage() {
    const [form, setForm] = useState({
        fullname: "",
        country: "Беларусь",
        city: "",
        contact: "",
        investment_budget: "1M-5M RUB"
    });
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const data = await api.post<{ ok: boolean; message?: string; error?: string }>("/franchise/apply", form);
            if (data.ok) {
                setSubmitted(true);
                toast.success(data.message || "Заявка успешно отправлена");
            } else {
                toast.error(data.error || "Ошибка при отправке заявки");
            }
        } catch {
            toast.error("Ошибка сети. Попробуйте позже.");
        } finally {
            setLoading(false);
        }
    };

    if (submitted) {
        return (
            <div className="min-h-screen bg-[#0A0A0B] flex items-center justify-center p-4">
                <div className="max-w-md w-full bg-[#121214] border border-khokhloma-gold/30 rounded-3xl p-8 text-center animate-in zoom-in-95">
                    <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                        <ShieldCheck className="w-10 h-10 text-emerald-400" />
                    </div>
                    <h2 className="text-2xl font-black text-white mb-4">БИЗНЕС-МИССИЯ СОГЛАСОВАНА</h2>
                    <p className="text-gray-400 mb-8">
                        Ваша заявка на международную франшизу "Горизонт Хаб" успешно принята. 
                        Директор по развитию свяжется с вами по указанным контактам.
                    </p>
                    <a href="/" className="inline-block px-6 py-3 bg-khokhloma-gold hover:bg-yellow-600 text-black font-bold rounded-xl transition-colors">
                        Вернуться на главную
                    </a>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0A0A0B]">
            {/* HER0 SECION */}
            <div className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
                <div className="absolute inset-0 z-0">
                    <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px]" />
                    <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-khokhloma-gold/5 rounded-full blur-[100px]" />
                </div>
                
                <div className="max-w-7xl mx-auto relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                    
                    {/* ТЕКСТ САЙТА */}
                    <div className="text-left">
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-gray-300 mb-6 flex-wrap">
                            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            Международная Экспансия БАС
                        </div>
                        <h1 className="text-5xl lg:text-7xl font-black text-white leading-tight mb-6">
                            Экспорт Экосистемы <br/>
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-khokhloma-gold to-yellow-400">
                                ГОРИЗОНТ
                            </span>
                        </h1>
                        <p className="text-xl text-gray-400 mb-8 leading-relaxed max-w-xl">
                            Запустите Национальную Платформу учета и шеринга дронов в вашей стране по модели "Master Franchise". 
                            Мы предоставляем весь ИТ-Стек: логику, биллинг, Anti-Dumping ИИ и тендерные алгоритмы.
                        </p>
                        
                        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 max-w-xl mb-8 flex gap-3 items-start">
                            <ShieldCheck className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                            <div className="text-sm text-gray-300">
                                <span className="font-bold text-red-400 block mb-1">Ограничение Экспорта Технологий</span>
                                Платформа "Горизонт Хаб" не лицензируется и не поставляется в недружественные юрисдикции. 
                                Франшиза доступна строго для доверенных гео-зон (СНГ, Страны БРИКС).
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <div className="bg-[#121214] border border-white/5 px-6 py-4 rounded-2xl">
                                <div className="text-3xl font-black text-white mb-1">12+</div>
                                <div className="text-xs text-gray-500 uppercase font-bold tracking-wider">Доступных Стран</div>
                            </div>
                            <div className="bg-[#121214] border border-white/5 px-6 py-4 rounded-2xl">
                                <div className="text-3xl font-black text-white mb-1">0%</div>
                                <div className="text-xs text-gray-500 uppercase font-bold tracking-wider">Роялти первый год</div>
                            </div>
                        </div>
                    </div>

                    {/* ФОРМА ЗАЯВКИ */}
                    <div className="bg-[#121214]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-8 lg:p-10 shadow-2xl relative">
                        <div className="absolute top-0 right-0 p-6 opacity-10">
                            <Globe className="w-32 h-32" />
                        </div>
                        
                        <h3 className="text-2xl font-bold text-white mb-2 relative z-10">Заявка на Мастер-Франшизу</h3>
                        <p className="text-gray-400 text-sm mb-8 relative z-10">
                            Только для стратегических партнеров в утвержденных регионах.
                        </p>

                        <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                                    <Building2 className="w-3 h-3"/> Название Компании / ФИО
                                </label>
                                <input 
                                    required
                                    type="text" 
                                    value={form.fullname}
                                    onChange={e => setForm({...form, fullname: e.target.value})}
                                    placeholder="OOO АэроТех / Иванов И.И."
                                    className="w-full bg-[#1A1A1D] border border-white/10 focus:border-khokhloma-gold outline-none text-white rounded-xl px-4 py-3"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-xs font-bold text-khokhloma-gold uppercase tracking-wider mb-2 flex items-center gap-2">
                                        <Globe className="w-3 h-3"/> Страна Внедрения *
                                    </label>
                                    <select 
                                        value={form.country}
                                        onChange={e => setForm({...form, country: e.target.value})}
                                        className="w-full bg-[#1A1A1D] border border-khokhloma-gold/50 focus:border-khokhloma-gold outline-none text-white rounded-xl px-4 py-3 appearance-none cursor-pointer"
                                    >
                                        {FRIENDLY_COUNTRIES.map(country => (
                                            <option key={country} value={country}>{country}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                                        <MapPin className="w-3 h-3"/> Размещение Серверов
                                    </label>
                                    <input 
                                        required
                                        type="text" 
                                        value={form.city}
                                        onChange={e => setForm({...form, city: e.target.value})}
                                        placeholder="Город дата-центра"
                                        className="w-full bg-[#1A1A1D] border border-white/10 focus:border-khokhloma-gold outline-none text-white rounded-xl px-4 py-3"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                                    <DollarSign className="w-3 h-3"/> Планируемый Инвест. Бюджет
                                </label>
                                <select 
                                    value={form.investment_budget}
                                    onChange={e => setForm({...form, investment_budget: e.target.value})}
                                    className="w-full bg-[#1A1A1D] border border-white/10 focus:border-khokhloma-gold outline-none text-white rounded-xl px-4 py-3 appearance-none cursor-pointer"
                                >
                                    <option value="1M-5M RUB">От 1 до 5 млн. рублей</option>
                                    <option value="5M-10M RUB">От 5 до 10 млн. рублей</option>
                                    <option value="10M+ RUB">Свыше 10 млн. рублей</option>
                                    <option value="Government">Гос. Заказ (Субсидия)</option>
                                </select>
                            </div>

                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                                    <Phone className="w-3 h-3"/> Контакт для связи (Telegram / Телефон)
                                </label>
                                <input 
                                    required
                                    type="text" 
                                    value={form.contact}
                                    onChange={e => setForm({...form, contact: e.target.value})}
                                    placeholder="+7 ... или @username"
                                    className="w-full bg-[#1A1A1D] border border-white/10 focus:border-khokhloma-gold outline-none text-white rounded-xl px-4 py-3"
                                />
                            </div>

                            <button 
                                type="submit"
                                disabled={loading}
                                className="w-full py-4 bg-khokhloma-gold hover:bg-yellow-600 text-black font-black uppercase tracking-wider rounded-xl transition-all shadow-xl shadow-khokhloma-gold/20 disabled:opacity-50 flex items-center justify-center gap-2 mt-6"
                            >
                                {loading ? (
                                    <><Loader2 className="w-5 h-5 animate-spin"/> Проверка...</>
                                ) : (
                                    <>Подать Заявку <ArrowRight className="w-5 h-5" /></>
                                )}
                            </button>
                            <p className="text-[10px] text-gray-500 text-center mt-4">
                                Нажимая кнопку, вы подтверждаете наличие гражданства одной из дружественных юрисдикций.
                            </p>
                        </form>
                    </div>

                </div>
            </div>
        </div>
    );
}
