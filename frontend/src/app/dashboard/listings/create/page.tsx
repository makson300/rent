"use client";

import { useState, useEffect } from "react";
import { PlusCircle, Search, ShieldCheck, Camera, CheckCircle2, ArrowRight, Loader2, Building2 } from "lucide-react";
import { toast } from "react-hot-toast";
import { api } from "@/lib/api";

export default function CreateListingWeb() {
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [dadataLoading, setDadataLoading] = useState(false);
  
  // DaData State
  const [inn, setInn] = useState("");
  const [companyData, setCompanyData] = useState<any>(null);

  // Form State
  const [formData, setFormData] = useState({
    category_id: 1,
    city: "",
    title: "",
    description: "",
    price_list: "",
    contacts: "",
  });

  useEffect(() => {
    // Check auth
    const userStr = localStorage.getItem("skyrent_user");
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        setUserId(u.telegram_id || u.id);
      } catch {}
    } else {
        setUserId(0); // Mock for testing
    }
  }, []);

  const handleDadataSearch = async () => {
    if (!inn || inn.length < 10) {
      toast.error("Введите корректный ИНН (10 или 12 цифр)");
      return;
    }
    
    setDadataLoading(true);
    try {
      const data = await api.get<{ ok: boolean; company_name?: string; director?: string; address?: string; error?: string }>(`/dadata/company?inn=${inn}`);
      if (data.ok) {
        setCompanyData(data);
        toast.success("Компания успешно верифицирована");
      } else {
        toast.error(data.error || "Компания не найдена");
        setCompanyData(null);
      }
    } catch {
      toast.error("Ошибка при связи с DaData");
      setCompanyData(null);
    } finally {
      setDadataLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) {
      toast.error("Вы не авторизованы");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        user_telegram_id: userId,
        ...formData,
        listing_type: "rental",
      };

      const json = await api.post<{ ok: boolean; status?: string; ai_reason?: string; error?: string }>("/listings/web", payload);
      if (json.ok) {
        if (json.status === "active") {
          toast.success("Объявление прошло ИИ-Модерацию и мгновенно опубликовано!");
        } else {
          toast.success("Объявление создано и отправлено на ручную модерацию. ИИ Вердикт: " + json.ai_reason);
        }
        setFormData({
            category_id: 1, city: "", title: "", description: "", price_list: "", contacts: ""
        });
      } else {
        toast.error(json.error || "Ошибка публикации");
      }
    } catch {
      toast.error("Не удалось связаться с сервером");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 transition-all">
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-3 inline-block">
          Web Portal (Beta)
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <PlusCircle className="w-8 h-8 text-emerald-400" />
          Размещение техники
        </h1>
        <p className="text-gray-400 max-w-2xl text-lg">
          Добавьте дрон или оборудование в каталог "Горизонт". Все новые объявления автоматически проверяются нашей нейросетью(ИИ).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          <form onSubmit={handleSubmit} className="bg-[#0A0A0B] border border-white/10 rounded-3xl p-6 lg:p-8 space-y-6">
            
            <div className="space-y-4">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                 <Camera className="w-5 h-5 text-gray-400" /> Основные данные
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Категория</label>
                    <select 
                      value={formData.category_id} 
                      onChange={e => setFormData({...formData, category_id: Number(e.target.value)})}
                      className="w-full bg-[#121214] border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none transition-all"
                    >
                      <option value="1">Аэросъемка (БПЛА)</option>
                      <option value="2">Агро-дроны</option>
                      <option value="3">Камеры / Объективы</option>
                      <option value="4">Тепловизоры / RTK</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Поддомен / Город</label>
                    <input 
                      type="text" required placeholder="Например: Москва"
                      value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})}
                      className="w-full bg-[#121214] border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-emerald-500/50 outline-none transition-all"
                    />
                  </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Название оборудования</label>
                <input 
                  type="text" required placeholder="Например: DJI Mavic 3 Pro Cine"
                  value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})}
                  className="w-full bg-[#121214] border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-emerald-500/50 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Описание для заказчика</label>
                <textarea 
                  required rows={4} placeholder="Подробно опишите характеристики и состояние..."
                  value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})}
                  className="w-full bg-[#121214] border border-white/10 rounded-xl px-4 py-3 text-white font-sans focus:ring-2 focus:ring-emerald-500/50 outline-none transition-all resize-none"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Прайс-лист / Ставка</label>
                    <input 
                      type="text" required placeholder="Например: 5000 руб/смена"
                      value={formData.price_list} onChange={e => setFormData({...formData, price_list: e.target.value})}
                      className="w-full bg-[#121214] border border-white/10 rounded-xl px-4 py-3 text-amber-400 focus:ring-2 focus:ring-emerald-500/50 outline-none transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Контакты</label>
                    <input 
                      type="text" required placeholder="@username или Телефон"
                      value={formData.contacts} onChange={e => setFormData({...formData, contacts: e.target.value})}
                      className="w-full bg-[#121214] border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-emerald-500/50 outline-none transition-all"
                    />
                  </div>
              </div>
            </div>

            <button
              type="submit" disabled={loading}
              className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50 flex items-center justify-center gap-2 group-hover:scale-[1.02]"
            >
              {loading ? <><Loader2 className="w-5 h-5 animate-spin"/> Нейросеть проверяет...</> : <>Опубликовать <ArrowRight className="w-5 h-5"/></>}
            </button>
            <p className="text-center text-[10px] text-gray-500">Нажимая кнопку, вы соглашаетесь с условиями ИИ-модерации</p>
          </form>
        </div>

        {/* Sidebar: KYC DaData */}
        <div className="space-y-6">
          <div className="bg-[#0A0A0B] border border-khokhloma-gold/30 rounded-3xl p-6 relative overflow-hidden group">
             <div className="absolute top-0 right-0 w-32 h-32 bg-khokhloma-gold/10 rounded-full filter blur-2xl pointer-events-none" />
             
             <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-2">
                 <ShieldCheck className="w-5 h-5 text-khokhloma-gold" /> 
                 Верификация B2B
             </h3>
             <p className="text-xs text-gray-400 mb-4">
                 Интеграция с ФНС России. Подтвердите свою компанию (KYC), чтобы получать доверие Заказчиков в тендерах.
             </p>
             
             <div className="flex gap-2 mb-4">
                <input 
                   type="text" placeholder="Введите ИНН..." 
                   value={inn} onChange={(e) => setInn(e.target.value)}
                   className="flex-1 bg-[#121214] border border-white/10 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-khokhloma-gold transition-colors"
                />
                <button 
                   onClick={handleDadataSearch} disabled={dadataLoading}
                   className="bg-khokhloma-gold text-black rounded-lg px-3 py-2 font-bold hover:bg-[#ffdd55] transition-colors disabled:opacity-50"
                >
                   {dadataLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                </button>
             </div>

             {companyData && (
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3 text-sm animate-in fade-in slide-in-from-top-2">
                    <div className="flex items-center gap-1.5 text-emerald-400 font-bold mb-2">
                        <CheckCircle2 className="w-4 h-4" /> Юрлицо найдено
                    </div>
                    <div className="text-gray-300 space-y-1">
                        <p className="font-bold text-white flex items-center gap-2"><Building2 className="w-3 h-3 text-khokhloma-gold"/> {companyData.company_name}</p>
                        <p className="text-[11px] text-gray-400">Гендир: {companyData.director}</p>
                        <p className="text-[11px] text-gray-400">{companyData.address}</p>
                    </div>
                </div>
             )}
          </div>
        </div>
      </div>
    </div>
  );
}
