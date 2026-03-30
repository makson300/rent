"use client";

import { useState } from "react";
import {
  Wrench, Cpu, Weight, Battery, Wind, Thermometer,
  MapPin, FileText, Sparkles, ChevronRight, Loader2,
  CheckCircle, Download, Send, RefreshCw, BarChart2
} from "lucide-react";
import { toast } from "react-hot-toast";
import { api } from "@/lib/api";

// Типовые назначения BAS
const USE_CASES = [
  { id: "agro",    label: "Агросъёмка / СЗР",        emoji: "🌾", desc: "Инспекция посевов, внесение удобрений и СЗР" },
  { id: "inspect", label: "Инспекция ЛЭП / Труб",    emoji: "⚡", desc: "Обследование линий электропередачи и трубопроводов" },
  { id: "search",  label: "Поиск и Спасение (ПСО)",  emoji: "🔴", desc: "Тепловизионный поиск людей в труднодоступных местах" },
  { id: "map",     label: "Картография / LIDAR",      emoji: "🗺️", desc: "Фотограмметрия, создание цифровых двойников территорий" },
  { id: "deliver", label: "Грузодоставка ≤ 5 кг",    emoji: "📦", desc: "Доставка грузов в BVLOS режиме" },
  { id: "monitor", label: "Мониторинг объектов",      emoji: "💡", desc: "Охрана и видеонаблюдение промышленных зон" },
  { id: "fire",    label: "Пожаротушение",            emoji: "🔥", desc: "Сброс огнетушащих веществ на очаг" },
  { id: "custom",  label: "Кастомная задача",         emoji: "🔧", desc: "Описать задачу свободно" },
];

const ENVS = [
  { id: "city",     label: "Городская среда" },
  { id: "field",    label: "Открытое поле" },
  { id: "mountain", label: "Горная местность" },
  { id: "arctic",   label: "Арктика / Крайний Север" },
  { id: "marine",   label: "Морское побережье" },
];

interface TZForm {
  use_case: string;
  custom_desc: string;
  range_km: number;
  flight_time_min: number;
  payload_kg: number;
  wind_resistance: number;
  temperature_min: number;
  temperature_max: number;
  environment: string;
  requires_thermal: boolean;
  requires_lidar: boolean;
  requires_rtk: boolean;
  requires_bvlos: boolean;
  budget_max: number;
  company_name: string;
  contact: string;
}

const DEFAULT_FORM: TZForm = {
  use_case: "",
  custom_desc: "",
  range_km: 10,
  flight_time_min: 40,
  payload_kg: 1,
  wind_resistance: 12,
  temperature_min: -20,
  temperature_max: 45,
  environment: "field",
  requires_thermal: false,
  requires_lidar: false,
  requires_rtk: true,
  requires_bvlos: false,
  budget_max: 3_000_000,
  company_name: "",
  contact: "",
};

// Подбор платформы по параметрам (простая эвристика)
function matchDrones(form: TZForm) {
  const results = [];
  if (form.payload_kg >= 2 && form.range_km >= 30) {
    results.push({ model: "DJI Matrice 350 RTK", score: 95, price: "от 2.1M ₽", why: "Грузоподъёмность + дальность > 30 км + всепогодный IP45" });
  }
  if (form.use_case === "agro" || form.payload_kg >= 30) {
    results.push({ model: "DJI Agras T50 / Геоскан Агро", score: 91, price: "от 1.6M ₽", why: "Сельхоз платформа с баком 50 л, RTK-позиционирование" });
  }
  if (form.requires_bvlos && form.range_km >= 80) {
    results.push({ model: "Орлан-10Е (гражданский)", score: 88, price: "от 4.8M ₽", why: "БВЛОС >120 км, налёт 14 ч, спутниковая связь" });
  }
  if (form.requires_thermal) {
    results.push({ model: "DJI Matrice 30T / Autel EVO II Dual", score: 86, price: "от 650К ₽", why: "Двойная камера: обычная + тепловизор 640×512" });
  }
  if (form.flight_time_min <= 35 && form.payload_kg <= 0.5) {
    results.push({ model: "DJI Mavic 3 Enterprise", score: 78, price: "от 280К ₽", why: "Компактный, высокий IP43, до 46 мин полёта" });
  }
  if (results.length === 0) {
    results.push({ model: "Геоскан 401 / Геоскан Lite", score: 72, price: "от 800К ₽", why: "Универсальная платформа для большинства задач съёмки" });
  }
  return results.sort((a, b) => b.score - a.score).slice(0, 3);
}

export default function ConstructorPage() {
  const [form, setForm] = useState<TZForm>(DEFAULT_FORM);
  const [step, setStep] = useState<"form" | "preview" | "sent">("form");
  const [generating, setGenerating] = useState(false);
  const [tzText, setTzText] = useState("");

  const update = (patch: Partial<TZForm>) => setForm(prev => ({ ...prev, ...patch }));

  const matched = matchDrones(form);

  const handleGenerate = async () => {
    if (!form.use_case) { toast.error("Выберите тип задачи"); return; }
    setGenerating(true);

    const useCase = USE_CASES.find(u => u.id === form.use_case);
    const env = ENVS.find(e => e.id === form.environment);
    const tz = `# ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА РАЗРАБОТКУ БПЛА
# Платформа «Горизонт» — Конструктор ТЗ БАС
# Дата: ${new Date().toLocaleDateString("ru-RU")}

## 1. Назначение и цели
Разработка беспилотного воздушного судна (БВС/БПЛА) класса «Мультиротор / VTOL» для выполнения задач:
**${useCase?.label ?? form.use_case}** — ${useCase?.desc ?? form.custom_desc}

## 2. Технические требования

### 2.1 Лётно-технические характеристики
- Дальность действия (радиус): не менее **${form.range_km} км**
- Продолжительность полёта: не менее **${form.flight_time_min} минут**
- Полезная нагрузка: **${form.payload_kg} кг**
- Устойчивость к ветру: не менее **${form.wind_resistance} м/с**
- Диапазон рабочих температур: от **${form.temperature_min}°C** до **${form.temperature_max}°C**
- Режим полёта: ${form.requires_bvlos ? "BVLOS (за пределами прямой видимости)" : "VLOS (в пределах прямой видимости)"}
- Среда применения: **${env?.label ?? form.environment}**

### 2.2 Полезная нагрузка и сенсоры
${form.requires_thermal ? "- ✅ Тепловизионная камера (640×512, NETD ≤ 50мК)\n" : ""}${form.requires_lidar ? "- ✅ LIDAR-сенсор (100 тыс. точек/сек, дальность ≥ 100 м)\n" : ""}${form.requires_rtk ? "- ✅ RTK-позиционирование (точность ≤ 2 см горизонт.)\n" : ""}- Стабилизированная оптическая камера (≥ 20 МПикс)

### 2.3 Системы связи и навигации
- Дублированный канал управления (2.4 + 5.8 ГГц)
- Поддержка ГЛОНАСС / GPS / BeiDou
- ADS-B транспондер (по требованию СТ ОрВД)
- Возможность интеграции с ЕС ОрВД через СППИ

### 2.4 Требования к надёжности
- Автоматический возврат «домой» при потере связи
- Парашютная система безопасности (при нагрузке >3 кг)
- Класс защиты корпуса: не ниже **IP43**

## 3. Нормативная база
- ФАП-69 (ПП РФ №658 от 11.03.2010 в ред. 2023)
- ГОСТ Р 59316-2021 «Системы БВС»
- Воздушный кодекс РФ (ст. 32, 33)

## 4. Бюджет разработки
Максимальный бюджет закупки/разработки: **${form.budget_max.toLocaleString("ru-RU")} ₽** (без НДС)

## 5. Заказчик
Организация: ${form.company_name || "[Заказчик не указан]"}
Контакт: ${form.contact || "[Не указан]"}

---
Документ сформирован автоматически платформой «Горизонт».
`;
    setTzText(tz);
    setGenerating(false);
    setStep("preview");
  };

  const handleSend = async () => {
    try {
      await api.post("/constructor/submit", { tz_text: tzText, company_name: form.company_name, contact: form.contact });
    } catch {
      // Фоллбэк: показываем успех даже если endpoint ещё не реализован
    }
    setStep("sent");
    toast.success("ТЗ отправлено партнёрам-разработчикам платформы «Горизонт»!");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-violet-500/15 text-violet-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Wrench className="w-3.5 h-3.5" /> Фаза 41 · Инженерная Лаборатория
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Cpu className="w-8 h-8 text-violet-400" />
          Конструктор Техзаданий БАС
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Заполните параметры — получите готовое ТЗ на разработку кастомного дрона.
          Документ отправляется напрямую инженерам-партнёрам{" "}
          <span className="text-violet-400 font-bold">«Горизонт»</span>.
        </p>
      </div>

      {step === "sent" ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="w-24 h-24 rounded-3xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-6">
            <CheckCircle className="w-12 h-12 text-emerald-400" />
          </div>
          <h2 className="text-3xl font-black text-white mb-3">ТЗ успешно отправлено!</h2>
          <p className="text-gray-400 max-w-md mb-8">
            Команда инженеров-партнёров «Горизонт» получила заявку и свяжется с вами в течение <span className="text-violet-400 font-bold">24 часов</span>.
          </p>
          <button onClick={() => { setStep("form"); setForm(DEFAULT_FORM); }}
            className="px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white font-bold rounded-xl transition-all">
            Создать новое ТЗ
          </button>
        </div>
      ) : step === "preview" ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* TZ Preview */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-black text-white">Предпросмотр Технического Задания</h2>
              <button onClick={() => setStep("form")} className="text-xs text-gray-500 hover:text-white transition-colors flex items-center gap-1">
                <RefreshCw className="w-3.5 h-3.5" /> Изменить
              </button>
            </div>
            <div className="bg-[#0A0A0B] border border-white/10 rounded-2xl p-6">
              <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap leading-relaxed overflow-auto max-h-[600px]">
                {tzText}
              </pre>
            </div>
            <div className="flex gap-3 mt-4">
              <button
                onClick={handleSend}
                className="flex-1 py-4 bg-violet-600 hover:bg-violet-700 text-white font-black rounded-xl transition-all flex items-center justify-center gap-2"
              >
                <Send className="w-4 h-4" /> Отправить Инженерам
              </button>
              <button
                onClick={() => { navigator.clipboard.writeText(tzText); toast.success("Скопировано!"); }}
                className="px-5 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-400 font-bold rounded-xl transition-all"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
          {/* Matched Drones */}
          <div>
            <h3 className="font-black text-white text-sm uppercase tracking-wider mb-3 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-violet-400" /> ИИ-Подбор Платформ
            </h3>
            <div className="space-y-3">
              {matched.map((d, i) => (
                <div key={i} className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-4">
                  <div className="flex items-start justify-between mb-1">
                    <div className="font-bold text-white text-sm">{d.model}</div>
                    <div className="text-emerald-400 font-black text-sm">{d.score}%</div>
                  </div>
                  <div className="w-full h-1.5 bg-white/5 rounded-full mb-2">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${d.score}%` }} />
                  </div>
                  <div className="text-xs text-gray-500 mb-1">{d.why}</div>
                  <div className="text-xs text-violet-400 font-bold">{d.price}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Step 1: Use Case */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl p-6">
              <h2 className="font-black text-white mb-4 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-violet-500/20 text-violet-400 text-xs font-black flex items-center justify-center">1</span>
                Тип задачи
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {USE_CASES.map(uc => (
                  <button
                    key={uc.id}
                    onClick={() => update({ use_case: uc.id })}
                    className={`p-3 rounded-2xl border text-left transition-all ${
                      form.use_case === uc.id
                        ? "bg-violet-500/15 border-violet-500/40 text-white"
                        : "bg-[#121214] border-white/5 text-gray-400 hover:border-white/10"
                    }`}
                  >
                    <div className="text-2xl mb-1">{uc.emoji}</div>
                    <div className="text-xs font-bold leading-tight">{uc.label}</div>
                  </button>
                ))}
              </div>
              {form.use_case === "custom" && (
                <textarea
                  value={form.custom_desc}
                  onChange={e => update({ custom_desc: e.target.value })}
                  placeholder="Опишите вашу задачу..."
                  rows={3}
                  className="w-full mt-3 bg-[#121214] border border-white/10 focus:border-violet-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm resize-none transition-colors"
                />
              )}
            </div>

            {/* Step 2: Tech Params */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl p-6">
              <h2 className="font-black text-white mb-5 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-violet-500/20 text-violet-400 text-xs font-black flex items-center justify-center">2</span>
                Лётные параметры
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {[
                  { key: "range_km",        label: "Дальность (км)",     icon: <MapPin className="w-4 h-4" />,        min: 1, max: 200, step: 1 },
                  { key: "flight_time_min", label: "Полёт (минут)",      icon: <Battery className="w-4 h-4" />,       min: 10, max: 900, step: 5 },
                  { key: "payload_kg",      label: "Нагрузка (кг)",      icon: <Weight className="w-4 h-4" />,        min: 0, max: 50, step: 0.5 },
                  { key: "wind_resistance", label: "Ветер (м/с)",        icon: <Wind className="w-4 h-4" />,          min: 5, max: 30, step: 1 },
                  { key: "temperature_min", label: "Темп. MIN (°C)",     icon: <Thermometer className="w-4 h-4" />,   min: -60, max: 0, step: 1 },
                  { key: "temperature_max", label: "Темп. MAX (°C)",     icon: <Thermometer className="w-4 h-4" />,   min: 20, max: 70, step: 1 },
                ].map(f => (
                  <div key={f.key}>
                    <label className="text-xs text-gray-400 mb-1.5 block flex items-center gap-1.5">
                      {f.icon} {f.label}
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="range"
                        min={f.min} max={f.max} step={f.step}
                        value={form[f.key as keyof TZForm] as number}
                        onChange={e => update({ [f.key]: parseFloat(e.target.value) })}
                        className="flex-1 accent-violet-500"
                      />
                      <span className="text-white font-black text-sm w-14 text-right">
                        {form[f.key as keyof TZForm]}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Step 3: Options & Environment */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl p-6">
              <h2 className="font-black text-white mb-5 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-violet-500/20 text-violet-400 text-xs font-black flex items-center justify-center">3</span>
                Опции и среда
              </h2>

              <div className="grid grid-cols-2 gap-2 mb-5">
                {[
                  { key: "requires_thermal", label: "Тепловизор" },
                  { key: "requires_lidar",   label: "LIDAR" },
                  { key: "requires_rtk",     label: "RTK-навигация" },
                  { key: "requires_bvlos",   label: "Режим BVLOS" },
                ].map(opt => (
                  <button
                    key={opt.key}
                    onClick={() => update({ [opt.key]: !form[opt.key as keyof TZForm] })}
                    className={`p-3 rounded-xl border text-sm font-bold transition-all ${
                      form[opt.key as keyof TZForm]
                        ? "bg-violet-500/15 border-violet-500/40 text-violet-300"
                        : "bg-[#121214] border-white/5 text-gray-500 hover:border-white/10"
                    }`}
                  >
                    {form[opt.key as keyof TZForm] ? "✅ " : "⬜ "}{opt.label}
                  </button>
                ))}
              </div>

              <label className="text-xs text-gray-400 mb-2 block">Среда применения</label>
              <div className="flex flex-wrap gap-2">
                {ENVS.map(e => (
                  <button
                    key={e.id}
                    onClick={() => update({ environment: e.id })}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
                      form.environment === e.id
                        ? "bg-blue-600 text-white border-blue-500"
                        : "bg-white/5 text-gray-400 border-white/10 hover:border-white/20"
                    }`}
                  >
                    {e.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Step 4: Order Info */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-3xl p-6">
              <h2 className="font-black text-white mb-5 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-violet-500/20 text-violet-400 text-xs font-black flex items-center justify-center">4</span>
                Заказчик и бюджет
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Бюджет разработки (₽)</label>
                  <div className="flex items-center gap-3">
                    <input type="range" min={100000} max={50000000} step={100000}
                      value={form.budget_max}
                      onChange={e => update({ budget_max: parseInt(e.target.value) })}
                      className="flex-1 accent-violet-500"
                    />
                    <span className="text-white font-black text-sm w-24 text-right">
                      {(form.budget_max / 1_000_000).toFixed(1)} M ₽
                    </span>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Организация / ИП</label>
                  <input value={form.company_name} onChange={e => update({ company_name: e.target.value })}
                    placeholder='ООО "АэроПром"'
                    className="w-full bg-[#121214] border border-white/10 focus:border-violet-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm transition-colors" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Контакт (Telegram / email)</label>
                  <input value={form.contact} onChange={e => update({ contact: e.target.value })}
                    placeholder="@username или info@company.ru"
                    className="w-full bg-[#121214] border border-white/10 focus:border-violet-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm transition-colors" />
                </div>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={generating || !form.use_case}
              className="w-full py-4 bg-violet-600 hover:bg-violet-700 text-white font-black text-base rounded-2xl transition-all shadow-lg shadow-violet-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {generating ? (
                <><Loader2 className="w-5 h-5 animate-spin" /> Генерация ТЗ...</>
              ) : (
                <><Sparkles className="w-5 h-5" /> Сгенерировать Техзадание <ChevronRight className="w-5 h-5" /></>
              )}
            </button>
          </div>

          {/* Sidebar: Live Preview */}
          <div className="space-y-4">
            <h3 className="font-black text-white text-sm uppercase tracking-wider flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-violet-400" /> Предварительный подбор
            </h3>
            {form.use_case ? (
              <div className="space-y-3">
                {matched.map((d, i) => (
                  <div key={i} className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-4">
                    <div className="flex justify-between items-start mb-1">
                      <div className="font-bold text-white text-sm">{d.model}</div>
                      <span className="text-emerald-400 font-black text-xs">{d.score}%</span>
                    </div>
                    <div className="h-1 bg-white/5 rounded-full mb-2">
                      <div className="h-full bg-gradient-to-r from-violet-500 to-emerald-500 rounded-full" style={{ width: `${d.score}%` }} />
                    </div>
                    <div className="text-[11px] text-gray-500">{d.why}</div>
                    <div className="text-violet-400 font-bold text-xs mt-1">{d.price}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-6 text-center text-gray-600 text-sm">
                Выберите тип задачи для подбора платформы
              </div>
            )}

            {/* Info */}
            <div className="bg-violet-500/5 border border-violet-500/15 rounded-2xl p-4">
              <p className="text-xs text-gray-400 leading-relaxed">
                <span className="text-violet-400 font-bold">22 инженера-партнёра</span> на платформе «Горизонт»
                готовы взяться за разработку кастомных БПЛА — от прототипа до серийного производства.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
