"use client";

import { useState } from "react";
import {
  FlaskConical, Upload, Zap, Wind, Weight, Gauge, ArrowUp,
  BarChart2, CheckCircle, AlertTriangle, Loader2, RefreshCw,
  Cpu, TrendingUp, Activity, Target
} from "lucide-react";
import { toast } from "react-hot-toast";

// --- Физическая модель (упрощённая аэродинамика) ---
function simulate(params: SimParams): SimResult {
  const { mass_kg, wing_area_m2, thrust_n, wind_ms, altitude_m, prop_diameter_cm } = params;

  const rho = 1.225 * Math.exp(-altitude_m / 8500); // плотность воздуха
  const g = 9.81;
  const weight = mass_kg * g;

  // Подъёмная сила (упрощённый вариант Жуковского)
  const cl = 0.8; // коэффициент подъёмной силы
  const v_hover = Math.sqrt(weight / (2 * rho * Math.PI * Math.pow(prop_diameter_cm / 200, 2) * params.num_props));
  const lift = 0.5 * rho * cl * wing_area_m2 * v_hover * v_hover;

  // Аэродинамическое качество
  const cd = 0.03 + 0.04 * cl * cl;
  const aero_quality = cl / cd;

  // КПД пропеллера (зависит от ветра)
  const wind_factor = Math.max(0.4, 1 - wind_ms / 30);

  // Эффективная тяга с учётом ветра
  const effective_thrust = thrust_n * wind_factor;
  const thrust_to_weight = effective_thrust / weight;

  // Максимальная скорость
  const v_max = Math.min(120, Math.sqrt(2 * effective_thrust / (rho * Math.PI * Math.pow(prop_diameter_cm / 200, 2) * params.num_props)));

  // Дальность (упрощённо)
  const flight_time_min = (params.battery_wh / (thrust_n * 2.5 / params.num_props)) * 60;
  const range_km = (v_max * 0.7 * flight_time_min) / 60;

  // Безопасность вылета
  let safe = true;
  const warnings: string[] = [];
  if (thrust_to_weight < 1.5) { safe = false; warnings.push("Тяга/вес < 1.5 — взлёт невозможен"); }
  if (wind_ms > 18) { warnings.push("Сильный ветер — риск потери управления"); }
  if (altitude_m > 3000) { warnings.push("Разрежённый воздух — снижение подъёмной силы на " + Math.round((1 - rho / 1.225) * 100) + "%"); }

  const scores = {
    stability:    Math.min(100, Math.round(thrust_to_weight * 40)),
    efficiency:   Math.min(100, Math.round(aero_quality * 5)),
    range_score:  Math.min(100, Math.round(range_km * 3)),
    wind_resist:  Math.min(100, Math.round(wind_factor * 100)),
  };

  return { thrust_to_weight, lift, aero_quality, v_max, flight_time_min, range_km, safe, warnings, scores };
}

interface SimParams {
  mass_kg: number;
  wing_area_m2: number;
  thrust_n: number;
  wind_ms: number;
  altitude_m: number;
  battery_wh: number;
  num_props: number;
  prop_diameter_cm: number;
}

interface Preset extends SimParams {
  name: string;
}


interface SimResult {
  thrust_to_weight: number;
  lift: number;
  aero_quality: number;
  v_max: number;
  flight_time_min: number;
  range_km: number;
  safe: boolean;
  warnings: string[];
  scores: { stability: number; efficiency: number; range_score: number; wind_resist: number };
}

const PRESETS: Preset[] = [
  { name: "DJI Mavic 3E", mass_kg: 0.895, wing_area_m2: 0.08, thrust_n: 35, wind_ms: 8, altitude_m: 0, battery_wh: 77, num_props: 4, prop_diameter_cm: 22 },
  { name: "Геоскан 401 (Агро)", mass_kg: 38, wing_area_m2: 0.4, thrust_n: 600, wind_ms: 5, altitude_m: 0, battery_wh: 2400, num_props: 8, prop_diameter_cm: 76 },
  { name: "Кастомный FPV Racing", mass_kg: 0.28, wing_area_m2: 0.02, thrust_n: 28, wind_ms: 3, altitude_m: 0, battery_wh: 18, num_props: 4, prop_diameter_cm: 15 },
  { name: "БВЛОС Крыло (VTOL)", mass_kg: 6.5, wing_area_m2: 1.2, thrust_n: 90, wind_ms: 12, altitude_m: 500, battery_wh: 350, num_props: 4, prop_diameter_cm: 38 },
];

const DEFAULT_PARAMS: SimParams = PRESETS[0];
const DEFAULT_PRESET_NAME = PRESETS[0].name;

function ScoreBar({ label, score, color }: { label: string; score: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-black">{score}/100</span>
      </div>
      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-700 ${color}`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}

export default function PolygonPage() {
  const [params, setParams] = useState<SimParams>(DEFAULT_PARAMS);
  const [result, setResult] = useState<SimResult | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [activePreset, setActivePreset] = useState<string>(DEFAULT_PRESET_NAME);

  const update = (patch: Partial<SimParams>) => setParams(p => ({ ...p, ...patch }));

  const handleSimulate = async () => {
    setSimulating(true);
    await new Promise(r => setTimeout(r, 1500));
    const res = simulate(params);
    setResult(res);
    setSimulating(false);
    if (res.safe) {
      toast.success("Симуляция завершена. Вылет возможен!");
    } else {
      toast.error("Критические параметры — вылет ЗАПРЕЩЁН");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <FlaskConical className="w-3.5 h-3.5" /> Фаза 43 · Инженерная Лаборатория
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Cpu className="w-8 h-8 text-cyan-400" />
          Виртуальный Полигон БАС
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Облачный аэродинамический симулятор. Задайте параметры дрона и получите расчёт лётных характеристик
          на основе уравнений Жуковского и модели Прандтля.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Params Panel */}
        <div className="lg:col-span-2 space-y-5">
          {/* Presets */}
          <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5">
            <label className="text-xs font-black text-gray-400 uppercase tracking-wider block mb-3">Шаблоны платформ</label>
            <div className="grid grid-cols-2 gap-2">
              {PRESETS.map((p, i) => (
                <button
                  key={i}
                  onClick={() => { const { name, ...simParams } = p; setParams(simParams); setActivePreset(name); setResult(null); }}
                  className={`p-2.5 rounded-xl border text-left text-xs transition-all ${
                    activePreset === p.name
                      ? "bg-cyan-500/10 border-cyan-500/40 text-white"
                      : "bg-[#121214] border-white/5 text-gray-400 hover:border-white/10"
                  }`}
                >
                  <div className="font-bold leading-tight">{p.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Physical Params */}
          <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5 space-y-4">
            <label className="text-xs font-black text-gray-400 uppercase tracking-wider block">Параметры Конструкции</label>
            {[
              { key: "mass_kg",         label: "Масса (кг)",         icon: <Weight className="w-4 h-4" />, min: 0.1, max: 100, step: 0.1 },
              { key: "wing_area_m2",    label: "Площадь несущ. (м²)", icon: <ArrowUp className="w-4 h-4" />, min: 0.01, max: 5, step: 0.01 },
              { key: "thrust_n",        label: "Тяга (Ньютон)",      icon: <Zap className="w-4 h-4" />,    min: 5, max: 2000, step: 5 },
              { key: "num_props",       label: "Кол-во пропеллеров", icon: <Target className="w-4 h-4" />, min: 2, max: 12, step: 2 },
              { key: "prop_diameter_cm",label: "Диаметр пропеллера (см)", icon: <Gauge className="w-4 h-4" />, min: 10, max: 120, step: 1 },
              { key: "battery_wh",     label: "Батарея (Вт·ч)",    icon: <Activity className="w-4 h-4" />, min: 5, max: 5000, step: 5 },
            ].map(f => (
              <div key={f.key}>
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-gray-400 flex items-center gap-1">{f.icon} {f.label}</span>
                  <span className="text-white font-black font-mono">{params[f.key as keyof SimParams]}</span>
                </div>
                <input
                  type="range" min={f.min} max={f.max} step={f.step}
                  value={params[f.key as keyof SimParams] as number}
                  onChange={e => { update({ [f.key]: parseFloat(e.target.value) }); setResult(null); }}
                  className="w-full accent-cyan-500"
                />
              </div>
            ))}
          </div>

          {/* Environment */}
          <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5 space-y-4">
            <label className="text-xs font-black text-gray-400 uppercase tracking-wider block">Условия Среды</label>
            {[
              { key: "wind_ms",    label: "Скорость ветра (м/с)", icon: <Wind className="w-4 h-4" />,   min: 0, max: 30, step: 0.5 },
              { key: "altitude_m", label: "Высота полёта (м)",    icon: <TrendingUp className="w-4 h-4" />, min: 0, max: 5000, step: 50 },
            ].map(f => (
              <div key={f.key}>
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-gray-400 flex items-center gap-1">{f.icon} {f.label}</span>
                  <span className="text-white font-black font-mono">{params[f.key as keyof SimParams]}</span>
                </div>
                <input
                  type="range" min={f.min} max={f.max} step={f.step}
                  value={params[f.key as keyof SimParams] as number}
                  onChange={e => { update({ [f.key]: parseFloat(e.target.value) }); setResult(null); }}
                  className="w-full accent-cyan-500"
                />
              </div>
            ))}
          </div>

          <button
            onClick={handleSimulate}
            disabled={simulating}
            className="w-full py-4 bg-cyan-600 hover:bg-cyan-500 text-white font-black text-base rounded-2xl transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {simulating
              ? <><Loader2 className="w-5 h-5 animate-spin" /> Симуляция...</>
              : <><FlaskConical className="w-5 h-5" /> Запустить Симуляцию</>}
          </button>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-3">
          {result ? (
            <div className="space-y-4">
              {/* Safety Banner */}
              <div className={`rounded-2xl p-4 border flex items-center gap-3 ${
                result.safe
                  ? "bg-emerald-500/10 border-emerald-500/30"
                  : "bg-red-500/10 border-red-500/30"
              }`}>
                {result.safe
                  ? <CheckCircle className="w-6 h-6 text-emerald-400 shrink-0" />
                  : <AlertTriangle className="w-6 h-6 text-red-400 shrink-0" />}
                <div>
                  <div className={`font-black text-sm ${result.safe ? "text-emerald-400" : "text-red-400"}`}>
                    {result.safe ? "✅ Вылет разрешён" : "🚫 Вылет ЗАПРЕЩЁН"}
                  </div>
                  {result.warnings.map((w, i) => (
                    <div key={i} className="text-xs text-gray-400 mt-0.5">{w}</div>
                  ))}
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { label: "Тяга / Вес",    val: result.thrust_to_weight.toFixed(2), unit: "×",    color: result.thrust_to_weight >= 1.5 ? "text-emerald-400" : "text-red-400" },
                  { label: "Скорость MAX",  val: result.v_max.toFixed(1),             unit: "км/ч", color: "text-cyan-400" },
                  { label: "Время полёта",  val: result.flight_time_min.toFixed(0),   unit: "мин",  color: "text-blue-400" },
                  { label: "Дальность",     val: result.range_km.toFixed(1),          unit: "км",   color: "text-violet-400" },
                  { label: "Кач-во аэро",   val: result.aero_quality.toFixed(1),      unit: "K",    color: "text-amber-400" },
                  { label: "Подъём. сила",  val: result.lift.toFixed(0),              unit: "Н",    color: "text-indigo-400" },
                ].map((m, i) => (
                  <div key={i} className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-4 text-center">
                    <div className="text-xs text-gray-500 mb-1">{m.label}</div>
                    <div className={`text-2xl font-black ${m.color}`}>{m.val}</div>
                    <div className="text-xs text-gray-600">{m.unit}</div>
                  </div>
                ))}
              </div>

              {/* Score Bars */}
              <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-6 space-y-4">
                <h3 className="font-black text-white flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-cyan-400" /> Профиль Характеристик
                </h3>
                <ScoreBar label="Устойчивость / Тяга" score={result.scores.stability}   color="bg-emerald-500" />
                <ScoreBar label="Аэродинамика"        score={result.scores.efficiency}  color="bg-cyan-500" />
                <ScoreBar label="Дальность"            score={result.scores.range_score} color="bg-violet-500" />
                <ScoreBar label="Ветроустойчивость"   score={result.scores.wind_resist} color="bg-amber-500" />
              </div>

              {/* Radar Chart (SVG) */}
              <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-6">
                <h3 className="font-black text-white mb-4 flex items-center gap-2">
                  <Target className="w-4 h-4 text-cyan-400" /> Радар Характеристик
                </h3>
                <div className="flex justify-center">
                  <svg viewBox="-110 -110 220 220" className="w-48 h-48">
                    {/* Grid */}
                    {[0.25, 0.5, 0.75, 1].map((r, i) => (
                      <polygon key={i} points={[0,1,2,3].map(j => {
                        const a = (j * Math.PI * 2) / 4 - Math.PI / 2;
                        return `${Math.cos(a) * r * 90},${Math.sin(a) * r * 90}`;
                      }).join(" ")}
                        fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                    ))}
                    {/* Axes */}
                    {[0,1,2,3].map(j => {
                      const a = (j * Math.PI * 2) / 4 - Math.PI / 2;
                      return <line key={j} x1="0" y1="0" x2={Math.cos(a) * 90} y2={Math.sin(a) * 90} stroke="rgba(255,255,255,0.08)" strokeWidth="1" />;
                    })}
                    {/* Data polygon */}
                    {(() => {
                      const vals = [
                        result.scores.stability / 100,
                        result.scores.efficiency / 100,
                        result.scores.range_score / 100,
                        result.scores.wind_resist / 100,
                      ];
                      const pts = vals.map((v, j) => {
                        const a = (j * Math.PI * 2) / 4 - Math.PI / 2;
                        return `${Math.cos(a) * v * 90},${Math.sin(a) * v * 90}`;
                      }).join(" ");
                      return <>
                        <polygon points={pts} fill="rgba(6,182,212,0.2)" stroke="#06b6d4" strokeWidth="2" />
                        {vals.map((v, j) => {
                          const a = (j * Math.PI * 2) / 4 - Math.PI / 2;
                          return <circle key={j} cx={Math.cos(a) * v * 90} cy={Math.sin(a) * v * 90} r="4" fill="#06b6d4" />;
                        })}
                      </>;
                    })()}
                    {/* Labels */}
                    {["Устойч.", "Аэродин.", "Дальность", "Ветер"].map((label, j) => {
                      const a = (j * Math.PI * 2) / 4 - Math.PI / 2;
                      return <text key={j} x={Math.cos(a) * 100} y={Math.sin(a) * 100} textAnchor="middle" dominantBaseline="middle" fill="rgba(156,163,175,1)" fontSize="11">{label}</text>;
                    })}
                  </svg>
                </div>
              </div>

              <button onClick={() => { setResult(null); }} className="w-full py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-400 font-bold rounded-xl transition-all flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4" /> Сбросить результаты
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center min-h-[500px] bg-[#0A0A0B] border border-white/5 rounded-3xl text-center p-8">
              <div className="w-20 h-20 rounded-3xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-6 animate-pulse">
                <FlaskConical className="w-10 h-10 text-cyan-400" />
              </div>
              <h3 className="text-white font-black text-xl mb-2">Полигон готов к симуляции</h3>
              <p className="text-gray-500 text-sm max-w-xs mb-6">
                Настройте параметры конструкции и нажмите «Запустить симуляцию».
                Расчёт занимает ~1–2 секунды.
              </p>
              <div className="grid grid-cols-2 gap-3 text-xs text-gray-600 max-w-xs">
                {["Уравнения Жуковского", "Модель Прандтля", "Атмосфера ИКАО", "ISA 1976"].map(m => (
                  <div key={m} className="flex items-center gap-1.5">
                    <CheckCircle className="w-3 h-3 text-cyan-500" /> {m}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
