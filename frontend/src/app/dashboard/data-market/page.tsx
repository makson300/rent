"use client";

import { useState } from "react";
import {
  Coins, Database, Shield, Zap, BarChart2,
  CheckCircle, Clock, Eye, ArrowUpRight, Wallet,
  Lock, Globe2, RefreshCw
} from "lucide-react";
import { toast } from "react-hot-toast";
import { datasetApi } from "@/lib/api";
import type { Dataset } from "@/lib/api";
import { useApiData } from "@/hooks/useApiData";

// ---------------------------------------------------------------------------
// Статические данные покупателей (не меняются)
// ---------------------------------------------------------------------------
const DATA_BUYERS = [
  { id: "b-001", name: "Яндекс Карты",     logo: "🗺️", category: "Картография",   buying: ["RGB Ортофото", "ЦМР", "LIDAR"],                     price_per_gb_usdt: 12, verified: true },
  { id: "b-002", name: "ГК Агро-ИИ",       logo: "🌾", category: "AgriTech AI",   buying: ["Сельхоз", "NDVI", "RGB Агро"],                      price_per_gb_usdt: 8,  verified: true },
  { id: "b-003", name: "Строй-Аналитика",  logo: "🏗️", category: "Стройконтроль", buying: ["Строительство", "LIDAR", "BIM"],                    price_per_gb_usdt: 18, verified: true },
  { id: "b-004", name: "МЧС Аналитика",    logo: "🚒", category: "Пожарный ИИ",   buying: ["Тепловизор", "Пожарный мониторинг", "Лесная съёмка"], price_per_gb_usdt: 22, verified: true },
];

const STATUS_CONFIG: Record<string, { label: string; cls: string }> = {
  listed:   { label: "Выставлено", cls: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
  sold:     { label: "Продано",    cls: "text-blue-400 bg-blue-500/10 border-blue-500/20" },
  unlisted: { label: "Черновик",   cls: "text-gray-400 bg-white/5 border-white/10" },
};

// ---------------------------------------------------------------------------
// Компонент
// ---------------------------------------------------------------------------
export default function DataTokenPage() {
  const [tab, setTab] = useState<"my" | "market">("my");
  const [publishing, setPublishing] = useState<number | null>(null);

  const { data: rawDatasets, loading, refetch } = useApiData(() => datasetApi.list());
  const datasets: Dataset[] = rawDatasets ?? [];

  const totalEarned    = datasets.filter(d => d.status === "sold").reduce((a, d) => a + d.price_usdt, 0);
  const pendingRevenue = datasets.filter(d => d.status === "listed").reduce((a, d) => a + d.price_usdt * d.buyer_count, 0);

  const handlePublish = async (id: number) => {
    setPublishing(id);
    try {
      await datasetApi.publish(id);
      toast.success("✅ Датасет выставлен на Data Marketplace!");
      refetch();
    } catch (err: unknown) {
      const e = err as { detail?: string };
      toast.error(e.detail ?? "Ошибка публикации");
    } finally {
      setPublishing(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-yellow-500/15 text-yellow-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Coins className="w-3.5 h-3.5" /> Фаза 51 · Data Monetization
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Database className="w-8 h-8 text-yellow-400" />
          Data Marketplace — Продай Свои Полёты
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Продавайте данные аэрофотосъёмки Яндексу, агро-компаниям и государственным структурам.
          Монетизация через{" "}
          <span className="text-yellow-400 font-bold">USDT / Горизонт-Токен (GRZ)</span>.
        </p>
      </div>

      {/* Revenue Panel */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        {[
          { label: "Заработано (USDT)", val: `$${totalEarned}`,    icon: <Coins   className="w-4 h-4 text-yellow-400" /> },
          { label: "Ожидаемый доход",   val: `$${pendingRevenue}`, icon: <Clock   className="w-4 h-4 text-blue-400" /> },
          { label: "Датасетов продано", val: datasets.filter(d => d.status === "sold").length, icon: <Database className="w-4 h-4 text-emerald-400" /> },
          { label: "Покупателей",       val: DATA_BUYERS.length,   icon: <Globe2  className="w-4 h-4 text-violet-400" /> },
        ].map((s, i) => (
          <div key={i} className="bg-gradient-to-br from-[#0E0E10] to-yellow-900/5 border border-yellow-500/10 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-1">{s.icon}<span className="text-xs text-gray-500">{s.label}</span></div>
            <div className="text-2xl font-black text-white">{s.val}</div>
          </div>
        ))}
      </div>

      {/* How it works */}
      <div className="bg-gradient-to-r from-yellow-900/15 to-amber-900/10 border border-yellow-500/15 rounded-2xl p-5 mb-6">
        <div className="font-black text-white mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" /> Как работает автоматический доход
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center text-xs">
          {[
            { emoji: "🚁", label: "Летите на работе" },
            { emoji: "📡", label: "Телеметрия в Горизонт" },
            { emoji: "🤖", label: "ИИ оценивает качество" },
            { emoji: "💰", label: "Выставляет на рынок" },
            { emoji: "📲", label: "USDT на кошелёк" },
          ].map((s, i) => (
            <div key={i} className="flex flex-col items-center gap-1">
              <div className="text-2xl">{s.emoji}</div>
              <div className="text-gray-400">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10 mb-6 gap-1">
        {(["my", "market"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-5 py-2.5 text-sm font-bold border-b-2 transition-colors ${tab === t ? "border-yellow-500 text-yellow-400" : "border-transparent text-gray-400 hover:text-white"}`}>
            {t === "my" ? "📁 Мои Датасеты" : "🏪 Покупатели"}
          </button>
        ))}
      </div>

      {/* My Datasets */}
      {tab === "my" && (
        <div className="space-y-3">
          {loading && (
            <div className="text-center py-16 text-gray-500 flex items-center justify-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin" /> Загружаем датасеты...
            </div>
          )}
          {!loading && datasets.length === 0 && (
            <div className="text-center py-20 text-gray-500">
              <Database className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p>У вас ещё нет датасетов. Загрузите первый полёт в разделе «Телеметрия».</p>
            </div>
          )}
          {datasets.map(ds => {
            const st = STATUS_CONFIG[ds.status] ?? STATUS_CONFIG["unlisted"];
            const isPublishing = publishing === ds.id;
            return (
              <div key={ds.id} className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5 hover:border-white/10 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-black text-white mb-0.5">{ds.area_name}</div>
                    <div className="text-xs text-gray-500 font-mono">{ds.flight_id}</div>
                  </div>
                  <span className={`px-2 py-0.5 text-[11px] font-black rounded border ${st.cls}`}>{st.label}</span>
                </div>

                <div className="flex flex-wrap gap-4 text-xs text-gray-500 mb-3">
                  <span className="flex items-center gap-1"><Database className="w-3 h-3" /> {ds.size_gb} ГБ</span>
                  {ds.pii_sanitized && <span className="text-emerald-400 flex items-center gap-1"><Shield className="w-3 h-3" /> PII очищен</span>}
                </div>

                <div className="flex flex-wrap gap-1.5 mb-3">
                  {ds.tags.split(",").filter(Boolean).map(t => (
                    <span key={t} className="text-[10px] px-2 py-0.5 bg-white/5 border border-white/5 text-gray-400 rounded-lg">{t.trim()}</span>
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    {ds.status === "sold"    && <span className="text-emerald-400 font-black text-sm">${ds.price_usdt} USDT получено</span>}
                    {ds.status === "listed"  && <span className="text-yellow-400 font-black text-sm">${ds.price_usdt} USDT · {ds.buyer_count} покупателей</span>}
                    {ds.status === "unlisted"&& <span className="text-gray-500 text-sm">Не выставлено на рынок</span>}
                  </div>
                  {ds.status === "unlisted" && (
                    <button
                      onClick={() => handlePublish(ds.id)}
                      disabled={isPublishing}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-600 hover:bg-yellow-500 text-black text-xs font-black rounded-lg transition-all disabled:opacity-50"
                    >
                      {isPublishing ? "Публикация..." : <><ArrowUpRight className="w-3.5 h-3.5" /> Выставить</>}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Market — Buyers */}
      {tab === "market" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DATA_BUYERS.map(buyer => (
            <div key={buyer.id} className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5 hover:border-yellow-500/20 transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-2xl">{buyer.logo}</div>
                  <div>
                    <div className="font-black text-white flex items-center gap-1.5">
                      {buyer.name}
                      {buyer.verified && <Shield className="w-3.5 h-3.5 text-emerald-400" />}
                    </div>
                    <div className="text-xs text-gray-500">{buyer.category}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-black text-yellow-400">${buyer.price_per_gb_usdt}</div>
                  <div className="text-[10px] text-gray-500">USDT/ГБ</div>
                </div>
              </div>
              <div>
                <div className="text-[10px] text-gray-500 mb-1.5">Покупают датасеты типа:</div>
                <div className="flex flex-wrap gap-1.5">
                  {buyer.buying.map(b => (
                    <span key={b} className="text-[10px] px-2 py-0.5 bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 rounded-lg">{b}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Disclaimer */}
      <div className="mt-6 flex items-start gap-2 text-xs text-gray-600">
        <Lock className="w-3.5 h-3.5 shrink-0 mt-0.5" />
        <span>
          Все данные перед публикацией проходят автоматическую де-идентификацию ПДн согласно 152-ФЗ.
          Координаты объектов класса «Закрытый» не публикуются.
        </span>
      </div>

    </div>
  );
}
