"use client";

import { useState, useEffect } from "react";
import { ShieldCheck, Wallet as WalletIcon, History, AlertTriangle, ArrowUpRight, ArrowDownRight, CreditCard, Lock, Loader2 } from "lucide-react";

import { toast } from "react-hot-toast";
import { api } from "@/lib/api";

export default function WalletEscrowPage() {
  const [activeTab, setActiveTab] = useState<"balance" | "escrow" | "insurance">("balance");
  const [wallet, setWallet] = useState<any>(null);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Hardcode ID for now since Next.js doesn't natively share Telegram WebApp state on this route yet
  const USER_ID = 0; // System User Telegram ID (always exists in DB)

  const fetchWalletData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const walletData = await api.get<{ ok: boolean; wallet: any }>(`/wallet/${USER_ID}`);
      const txData = await api.get<{ ok: boolean; transactions: any[] }>(`/wallet/${USER_ID}/transactions`);

      if (walletData.ok) setWallet(walletData.wallet);
      if (txData.ok) setTransactions(txData.transactions);
    } catch (err: any) {
      console.error("Failed to load wallet", err);
      setError(err?.message || "Ошибка соединения с сервером");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWalletData();
  }, []);

  const handleTopUp = async () => {
    const amountStr = prompt("Введите сумму пополнения (в рублях):", "1000");
    if (!amountStr) return;
    const amount = parseFloat(amountStr);
    if (isNaN(amount) || amount <= 0) {
      toast.error("Некорректная сумма");
      return;
    }

    setIsProcessing(true);
    try {
      const data = await api.post<{ ok: boolean; confirmation_url?: string; error?: string }>("/payments/checkout", { telegram_id: USER_ID, amount });
      if (data.ok && data.confirmation_url) {
        toast.loading("Перенаправление на ЮKassa...");
        // Перенаправляем на шлюз Яндекса/Сбера
        window.location.href = data.confirmation_url;
      } else {
        toast.error("Ошибка эквайринга: " + data.error);
        setIsProcessing(false);
      }
    } catch {
      toast.error("Ошибка соединения с кассой.");
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-khokhloma-gold via-[#ffdd55] to-khokhloma-red drop-shadow-lg">
            Мой Кошелёк и Гарантии
          </h1>
          <p className="text-gray-400 mt-1">Оплата аренды, холдирование средств и страхование КАСКО БАС.</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-white/10 pb-2 overflow-x-auto scrollbar-hide">
        <button
          onClick={() => setActiveTab("balance")}
          className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
            activeTab === "balance"
              ? "bg-white/10 text-white shadow-[0_0_15px_rgba(255,255,255,0.1)]"
              : "text-gray-400 hover:text-white hover:bg-white/5"
          }`}
        >
          Общий баланс
        </button>
        <button
          onClick={() => setActiveTab("escrow")}
          className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
            activeTab === "escrow"
              ? "bg-khokhloma-red/20 text-white shadow-[0_0_20px_rgba(204,0,0,0.4)] border border-khokhloma-red/50"
              : "text-gray-400 hover:text-white hover:bg-white/5"
          }`}
        >
          <Lock className="w-4 h-4" />
          Безопасная Сделка
        </button>
        <button
          onClick={() => setActiveTab("insurance")}
          className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
            activeTab === "insurance"
              ? "bg-tricolor-blue/20 text-white shadow-[0_0_20px_rgba(0,102,204,0.4)] border border-tricolor-blue/50"
              : "text-gray-400 hover:text-white hover:bg-white/5"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Страхование КАСКО
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center p-20">
            <Loader2 className="w-8 h-8 text-khokhloma-gold animate-spin" />
        </div>
      ) : error ? (
        <div className="p-12 text-center rounded-2xl border border-red-500/20 bg-red-500/5 mt-8">
            <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2 text-white">Сервис временно недоступен</h3>
            <p className="text-gray-400 mb-6">Не удалось загрузить данные кошелька ({error}). Попробуйте обновить страницу.</p>
            <button onClick={fetchWalletData} className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors font-bold text-sm">Обновить</button>
        </div>
      ) : (
      <>
      {/* BALANCE TAB */}
      {activeTab === "balance" && wallet && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 relative overflow-hidden bg-gradient-to-br from-[#0F172A] to-[#0A0A0B] rounded-2xl border border-white/10 p-8 shadow-[0_8px_30px_rgba(0,0,0,0.5)] group">
              <div className="absolute top-0 right-0 w-64 h-64 bg-pattern-khokhloma opacity-5 transition-opacity duration-500 group-hover:opacity-10 pointer-events-none"></div>
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-khokhloma-gold/20 blur-[50px]"></div>
              
              <div className="relative z-10">
                <p className="text-gray-400 font-medium uppercase tracking-wider text-sm mb-2">Доступные средства</p>
                <h2 className="text-5xl font-black text-white drop-shadow-md">
                  {wallet.balance.toLocaleString('ru-RU')} <span className="text-2xl text-khokhloma-gold">{wallet.currency === 'RUB' ? '₽' : '⭐️'}</span>
                </h2>
                
                <div className="mt-8 flex gap-4">
                  <button 
                    onClick={handleTopUp}
                    disabled={isProcessing}
                    className="flex-1 bg-white text-black hover:bg-gray-200 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-transform hover:-translate-y-1 disabled:opacity-50"
                  >
                    {isProcessing ? <Loader2 className="w-5 h-5 animate-spin"/> : <ArrowDownRight className="w-5 h-5" />}
                    Пополнить
                  </button>
                  <button className="flex-1 bg-white/10 text-white hover:bg-white/20 border border-white/10 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-transform hover:-translate-y-1">
                    <ArrowUpRight className="w-5 h-5" />
                    Вывести
                  </button>
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden bg-[#0A0A0B]/80 rounded-2xl border border-white/5 p-6 shadow-lg">
              <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                <Lock className="w-5 h-5 text-khokhloma-red" />
                В холде (Гарант)
              </h3>
              <p className="text-3xl font-extrabold text-gray-300">
                {wallet.hold_balance.toLocaleString('ru-RU')} <span className="text-xl">{wallet.currency === 'RUB' ? '₽' : '⭐️'}</span>
              </p>
              <p className="text-xs text-gray-500 mt-2">Средства заморожены по активным сделкам аренды до подтверждения возврата оборудования.</p>
              
              <button 
                onClick={() => setActiveTab("escrow")}
                className="mt-6 w-full py-2.5 text-sm font-medium text-khokhloma-red hover:bg-khokhloma-red/10 rounded-lg transition-colors border border-khokhloma-red/20"
              >
                Детали сделок
              </button>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-bold text-white mb-4">История транзакций</h3>
            <div className="bg-[#0A0A0B]/60 rounded-xl border border-white/5 p-2 space-y-2">
              {transactions.length > 0 ? transactions.map((tx, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      tx.transaction_type === "deposit" ? "bg-green-500/20 text-green-400" : 
                      tx.transaction_type === "hold" ? "bg-khokhloma-red/20 text-khokhloma-red" : 
                      "bg-white/10 text-white"
                    }`}>
                      {tx.transaction_type === "deposit" && <ArrowDownRight className="w-5 h-5" />}
                      {tx.transaction_type === "hold" && <Lock className="w-5 h-5" />}
                      {(tx.transaction_type === "withdraw" || tx.transaction_type === "payment") && <ArrowUpRight className="w-5 h-5" />}
                    </div>
                    <div>
                      <p className="font-bold text-white text-sm">{tx.description || tx.transaction_type.toUpperCase()}</p>
                      <p className="text-xs text-gray-400">{new Date(tx.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-bold ${tx.transaction_type === "deposit" ? "text-green-400" : tx.transaction_type === "hold" ? "text-khokhloma-red" : "text-white"}`}>
                      {(tx.transaction_type === "deposit" ? '+' : '')}{tx.amount.toLocaleString()} 
                    </p>
                    <p className="text-[10px] text-gray-500 uppercase">{tx.status}</p>
                  </div>
                </div>
              )) : (
                <div className="p-8 text-center text-gray-500">
                   У вас пока нет транзакций.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ESCROW TAB */}
      {activeTab === "escrow" && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="bg-gradient-to-r from-khokhloma-red/20 to-[#0A0A0B] border border-khokhloma-red/30 rounded-2xl p-6 shadow-[0_0_30px_rgba(204,0,0,0.15)]">
            <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
              <ShieldCheck className="text-khokhloma-gold" />
              Горизонт Escrow (Гарант)
            </h2>
            <p className="text-gray-300 text-sm max-w-3xl leading-relaxed">
              Ваши средства находятся в безопасности на холодном счету ПАО Сбербанк. Они не будут зачислены арендодателю до тех пор, пока вы не подтвердите успешный возврат оборудования в целости и сохранности.
            </p>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white">Активные сделки в Гаранте</h3>
            
            {/* Escrow Item 1 */}
            <div className="bg-[#0A0A0B]/80 rounded-xl border border-white/10 p-6 relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-1 h-full bg-khokhloma-red animate-pulse"></div>
              <div className="flex flex-col md:flex-row justify-between gap-6">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-2.5 py-1 bg-khokhloma-red/20 text-khokhloma-red text-xs font-black rounded-md uppercase tracking-wider border border-khokhloma-red/30">
                      ХОЛД АКТИВЕН
                    </span>
                    <span className="text-gray-400 text-xs">Договор № 492-AX</span>
                  </div>
                  <h4 className="text-xl font-bold text-white">Аренда: DJI Matrice 30T</h4>
                  <p className="text-sm text-gray-400 mt-1">Арендодатель: ООО "СкайРент"</p>
                  
                  <div className="mt-4 flex flex-wrap gap-4 text-sm">
                    <div className="bg-white/5 px-3 py-2 rounded-lg border border-white/5">
                      <span className="text-gray-500 block text-xs">Сумма холда:</span>
                      <span className="text-lg font-bold text-khokhloma-gold">55 000 ₽</span>
                    </div>
                    <div className="bg-white/5 px-3 py-2 rounded-lg border border-white/5">
                      <span className="text-gray-500 block text-xs">Срок возврата:</span>
                      <span className="text-white font-medium">30 Марта, 18:00</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col justify-end gap-2 md:min-w-[200px]">
                  <button className="w-full py-2.5 bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg text-sm font-bold transition-colors">
                    Подтвердить завершение
                  </button>
                  <button className="w-full py-2.5 bg-white/5 hover:bg-white/10 text-white rounded-lg text-sm font-medium transition-colors">
                    Связаться с техподдержкой
                  </button>
                </div>
              </div>
            </div>

            {/* Escrow Item 2 */}
            <div className="bg-[#0A0A0B]/80 rounded-xl border border-white/10 p-6 relative overflow-hidden">
              <div className="flex flex-col md:flex-row justify-between gap-6">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-2.5 py-1 bg-white/10 text-gray-300 text-xs font-bold rounded-md uppercase tracking-wider">
                      ПОДГОТОВКА
                    </span>
                    <span className="text-gray-400 text-xs">Договор № 511-BB</span>
                  </div>
                  <h4 className="text-xl font-bold text-white">Тепловизионная съёмка ЛЭП</h4>
                  <p className="text-sm text-gray-400 mt-1">Исполнитель: Иван Г.</p>
                  
                  <div className="mt-4 flex flex-wrap gap-4 text-sm">
                    <div className="bg-white/5 px-3 py-2 rounded-lg border border-white/5">
                      <span className="text-gray-500 block text-xs">Бюджет заморожен:</span>
                      <span className="text-lg font-bold text-white">30 000 ₽</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col justify-end gap-2 md:min-w-[200px]">
                  <button className="w-full py-2.5 bg-white/5 text-gray-500 cursor-not-allowed rounded-lg text-sm font-medium border border-white/5">
                    Ожидание исполнителя
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* INSURANCE TAB */}
      {activeTab === "insurance" && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-[#0F172A] to-[#0A0A0B] rounded-2xl border border-tricolor-blue/30 p-8 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-tricolor-blue/20 blur-[40px] transition-all group-hover:bg-tricolor-blue/40"></div>
              
              <ShieldCheck className="w-12 h-12 text-tricolor-blue mb-6 drop-shadow-[0_0_10px_rgba(102,179,255,0.8)]" />
              <h3 className="text-2xl font-bold text-white mb-2">Надежное КАСКО</h3>
              <p className="text-gray-400 mb-6 leading-relaxed">
                Защитите арендуемый или ваш личный беспилотник от падений, столкновений и утерь. Страховка за 5 минут, покрытие до 2 000 000 ₽. Актуальный тариф — 5% от рыночной стоимости.
              </p>
              
              <div className="space-y-4 mb-6">
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Модель БПЛА</label>
                  <select 
                     id="ins-model" 
                     className="w-full bg-[#18181b] border border-white/10 text-white p-3 rounded-lg text-sm"
                  >
                     <option value="DJI Mavic 3 Enterprise">DJI Mavic 3 Enterprise</option>
                     <option value="DJI Matrice 30T">DJI Matrice 30T</option>
                     <option value="Autel Evo Max 4T">Autel Evo Max 4T</option>
                     <option value="Agra T40">DJI Agras T40</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Серийный номер (S/N)</label>
                  <input type="text" id="ins-sn" placeholder="Например: 1581F..." className="w-full bg-[#18181b] border border-white/10 text-white p-3 rounded-lg text-sm"/>
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Сумма страхового покрытия (руб)</label>
                  <input type="number" id="ins-val" defaultValue="50000" min="50000" step="10000" className="w-full bg-[#18181b] border border-white/10 text-white p-3 rounded-lg text-sm"/>
                </div>
              </div>
              
              <button 
                disabled={isProcessing}
                onClick={async () => {
                  const m = (document.getElementById('ins-model') as HTMLSelectElement).value;
                  const s = (document.getElementById('ins-sn') as HTMLInputElement).value;
                  const v = parseFloat((document.getElementById('ins-val') as HTMLInputElement).value);
                  if(!s) { toast.error("Введите серийный номер"); return; }
                  if(v < 50000) { toast.error("Минимум 50,000 руб"); return; }
                  
                  const premium = v * 0.05;
                  if (!confirm(`К оплате: ${premium.toLocaleString()} ₽\n\nСумма будет списана с вашего цифрового кошелька. Продолжить?`)) return;
                  
                  setIsProcessing(true);
                  try {
                    const d = await api.post<{ ok: boolean; error?: string }>("/insurance/buy", { telegram_id: USER_ID, drone_model: m, serial_number: s, coverage_amount: v });
                    if(d.ok) {
                        toast.success("Полис успешно оформлен!");
                        fetchWalletData(); 
                    } else {
                        toast.error(d.error || "Ошибка оплаты");
                    }
                  } catch {
                      toast.error("Сетевая ошибка");
                  } finally {
                      setIsProcessing(false);
                  }
                }}
                className="w-full py-3 flex items-center justify-center gap-2 bg-tricolor-blue hover:bg-blue-600 text-white rounded-xl font-bold transition-all shadow-[0_0_15px_rgba(0,102,204,0.4)] hover:shadow-[0_0_25px_rgba(0,102,204,0.6)] disabled:opacity-50"
              >
                {isProcessing && <Loader2 className="w-5 h-5 animate-spin"/>}
                Купить полис (5%)
              </button>
            </div>

            <div className="bg-[#0A0A0B]/80 rounded-2xl border border-white/5 p-6 flex flex-col h-full">
               <h3 className="text-xl font-bold text-white mb-4">Мои Полисы</h3>
               
               <div className="space-y-3 overflow-y-auto flex-1 custom-scrollbar">
                  {/* Мы пока имитируем загрузку списка или просто показываем заглушку, 
                      если вы хотите, можно расширить fetchWalletData() стейтом setPolicies(data). 
                      Для MVP Фазы 24 мы оставляем визуальный плейсхолдер 
                      (или маппинг из стейта, где мы его инициализируем). */}
                  
                  <div className="p-4 bg-white/5 border border-white/10 rounded-xl relative overflow-hidden group">
                     <div className="absolute top-0 right-0 p-2 opacity-50"><ShieldCheck className="w-8 h-8 text-green-500"/></div>
                     <span className="text-[10px] bg-green-500/20 text-green-400 font-bold px-2 py-0.5 rounded-sm uppercase">Активен</span>
                     <h4 className="text-white font-bold mt-2">DJI Matrice 30T</h4>
                     <p className="text-xs text-gray-500 font-mono mb-2">S/N: 1581F4R932J0...</p>
                     
                     <div className="flex justify-between items-end mt-4">
                        <div>
                           <p className="text-[10px] text-gray-500">Сумма покрытия:</p>
                           <p className="text-sm text-khokhloma-gold font-bold">850 000 ₽</p>
                        </div>
                        <div className="text-right">
                           <p className="text-[10px] text-gray-500">Действует до:</p>
                           <p className="text-sm text-white">25 Апр 2026</p>
                        </div>
                     </div>
                  </div>

                  <div className="p-8 flex flex-col items-center justify-center text-center opacity-50">
                     <AlertTriangle className="w-10 h-10 text-gray-600 mb-2" />
                     <p className="text-xs text-gray-500">Вы можете оформить неограниченное кол-во полисов.</p>
                  </div>
               </div>
            </div>
          </div>
        </div>
      )}
      </>
      )}

    </div>
  );
}
