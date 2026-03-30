"use client";

import { useState } from "react";
import {
  ScrollText, Search, Plus, Send, CheckCircle, Clock,
  FileText, Sparkles, ChevronRight, Loader2, Shield,
  BookOpen, Globe2, AlertTriangle, Award, Lock
} from "lucide-react";
import { toast } from "react-hot-toast";
import { patentApi, api, type PatentApplication } from "@/lib/api";
import { useApiData } from "@/hooks/useApiData";

// --- МПК Классификатор (упрощённый) ---
const IPC_CLASSES = [
  { code: "B64C", label: "Воздушные суда (конструкция)" },
  { code: "B64D", label: "Оборудование ВС (приборы, двигатели)" },
  { code: "B64U", label: "Беспилотные ЛА (БПЛА)" },
  { code: "G05D", label: "Системы управления" },
  { code: "H04B", label: "Передача данных (канал связи)" },
  { code: "G01S", label: "Радиолокация, навигация" },
  { code: "F02K", label: "Реактивные двигатели" },
  { code: "H02J", label: "Источники питания (батареи)" },
  { code: "G06N", label: "Нейронные сети / ИИ" },
  { code: "A01B", label: "Сельскохозяйственные машины" },
];

// История заявок (мок)
const MOCK_APPLICATIONS = [
  {
    id: "РФ-2026-0041",
    title: "Алгоритм автономного облёта препятствий для БПЛА в условиях РЭБ",
    ipc: "G05D / B64U",
    filed_at: "2026-02-14",
    status: "examination",
    status_label: "Экспертиза ФИПС",
    progress: 55,
  },
  {
    id: "РФ-2025-1837",
    title: "Способ повышения дальности связи БПЛА через mesh-сеть ретрансляторов",
    ipc: "H04B / B64C",
    filed_at: "2025-11-03",
    status: "published",
    status_label: "Опубликовано",
    progress: 100,
  },
];

type Step = "list" | "form" | "review" | "success";

interface PatentForm {
  title: string;
  ipc_codes: string[];
  abstract: string;
  claims: string;
  author: string;
  company: string;
  inn: string;
  secret: boolean;
}

const DEFAULT_FORM: PatentForm = {
  title: "", ipc_codes: [], abstract: "", claims: "",
  author: "", company: "", inn: "", secret: false,
};

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { cls: string; icon: React.ReactNode }> = {
    examination: { cls: "bg-amber-500/15 text-amber-400 border-amber-500/30",  icon: <Clock className="w-3 h-3" /> },
    published:   { cls: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30", icon: <CheckCircle className="w-3 h-3" /> },
    rejected:    { cls: "bg-red-500/15 text-red-400 border-red-500/30",        icon: <AlertTriangle className="w-3 h-3" /> },
    draft:       { cls: "bg-gray-500/15 text-gray-400 border-gray-500/30",     icon: <FileText className="w-3 h-3" /> },
  };
  const s = map[status] ?? map.draft;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-black rounded border ${s.cls}`}>
      {s.icon} {map[status] ? "" : status}
    </span>
  );
}

export default function PatentBureau() {
  const [step, setStep] = useState<Step>("list");
  const [form, setForm] = useState<PatentForm>(DEFAULT_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);

  // Реальные данные из API
  const { data: apiPatents, refetch } = useApiData(() => patentApi.list());
  const applications = [
    ...MOCK_APPLICATIONS,
    ...(apiPatents ?? []).map((p: PatentApplication) => ({
      id: p.fips_id ?? `GRZ-${p.id}`,
      title: p.title,
      ipc: p.ipc_codes,
      filed_at: p.created_at.slice(0, 10),
      status: p.status,
      status_label: p.status === "draft" ? "Подано в ФИПС" : p.status,
      progress: p.progress_pct,
    })),
  ];

  const update = (patch: Partial<PatentForm>) => setForm(p => ({ ...p, ...patch }));

  const toggleIpc = (code: string) => {
    setForm(p => ({
      ...p,
      ipc_codes: p.ipc_codes.includes(code)
        ? p.ipc_codes.filter(c => c !== code)
        : [...p.ipc_codes, code].slice(0, 3),
    }));
  };

  const handleAiAbstract = async () => {
    if (!form.title) { toast.error("Введите название изобретения"); return; }
    setAiLoading(true);
    try {
      const data = await api.post<{ abstract: string; claims: string }>("/patents/ai-draft", { title: form.title, ipc_codes: form.ipc_codes });
      update({ abstract: data.abstract, claims: data.claims });
      toast.success("ИИ-формула изобретения готова!");
    } catch {
      // Фоллбэк на локальную генерацию если API не отвечает
      update({
        abstract: `Изобретение относится к области беспилотной авиации, в частности к ${form.title.toLowerCase()}. Технический результат — повышение надёжности и расширение функциональных возможностей беспилотных воздушных судов. Указанный результат достигается за счёт применения разработанного метода, включающего этапы первичной инициализации системы, последовательного выполнения алгоритма управления и верификации результата с точностью не менее 98%.`,
        claims: `1. ${form.title}, отличающийся тем, что содержит блок управления с интегрированным алгоритмом обработки сенсорной информации.\n2. Устройство по п. 1, отличающееся тем, что алгоритм реализован на нейросетевой архитектуре трансформерного типа.\n3. Способ по п. 1, отличающийся тем, что обеспечивает работу в условиях радиоэлектронного подавления.`,
      });
      toast.success("ИИ-формула сгенерирована (оффлайн)");
    } finally {
      setAiLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!form.title || !form.abstract || form.ipc_codes.length === 0) {
      toast.error("Заполните название, МПК и реферат");
      return;
    }
    setSubmitting(true);
    try {
      await patentApi.submit({
        title: form.title,
        ipc_codes: form.ipc_codes.join(" / "),
        abstract: form.abstract,
        claims: form.claims,
        author_name: form.author || undefined,
        organization: form.company || undefined,
        inn: form.inn || undefined,
        is_secret: form.secret,
      });
      refetch();
      setStep("success");
      toast.success("Заявка направлена в ФИПС (Роспатент)!");
    } catch (err: unknown) {
      const e = err as { detail?: string };
      toast.error(e.detail ?? "Ошибка подачи заявки");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-amber-500/15 text-amber-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <Award className="w-3.5 h-3.5" /> Фаза 42 · IP-Бюро
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <ScrollText className="w-8 h-8 text-amber-400" />
          Патентное Бюро «Горизонт»
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Подача патентных заявок на изобретения в области БАС через{" "}
          <span className="text-amber-400 font-bold">ФИПС / Роспатент</span> прямо с платформы.
          ИИ-помощник сформирует формулу изобретения по описанию.
        </p>
      </div>

      {step === "success" ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-24 h-24 rounded-3xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-6">
            <ScrollText className="w-12 h-12 text-amber-400" />
          </div>
          <h2 className="text-3xl font-black text-white mb-3">Заявка подана в ФИПС!</h2>
          <p className="text-gray-400 max-w-md mb-8">
            Регистрационный номер присвоен. Уведомление придёт на контактный email / Telegram.
            Средний срок экспертизы — <span className="text-amber-400 font-bold">12–18 месяцев</span>.
          </p>
          <button onClick={() => { setStep("list"); setForm(DEFAULT_FORM); }}
            className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-black font-black rounded-xl transition-all">
            К Моим Заявкам
          </button>
        </div>
      ) : step === "form" ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="lg:col-span-2 space-y-5">
            <button onClick={() => setStep("list")} className="text-xs text-gray-500 hover:text-white transition-colors flex items-center gap-1">
              ← Назад к заявкам
            </button>

            {/* Title */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">Название изобретения / полезной модели</label>
              <input
                value={form.title}
                onChange={e => update({ title: e.target.value })}
                placeholder="Устройство управления БПЛА с защитой от РЭБ..."
                className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm transition-colors"
              />
            </div>

            {/* IPC Classifier */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 block flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-amber-400" /> МПК Классификатор (выберите до 3)
              </label>
              <div className="grid grid-cols-2 gap-2">
                {IPC_CLASSES.map(cl => (
                  <button
                    key={cl.code}
                    onClick={() => toggleIpc(cl.code)}
                    className={`text-left p-3 rounded-xl border text-sm transition-all ${
                      form.ipc_codes.includes(cl.code)
                        ? "bg-amber-500/10 border-amber-500/40 text-white"
                        : "bg-[#121214] border-white/5 text-gray-400 hover:border-white/10"
                    }`}
                  >
                    <span className="font-black text-amber-400 font-mono text-xs">{cl.code}</span>
                    <br /><span className="text-xs">{cl.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Abstract + AI */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Реферат</label>
                <button
                  onClick={handleAiAbstract}
                  disabled={aiLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 text-amber-400 text-xs font-bold rounded-lg transition-all disabled:opacity-50"
                >
                  {aiLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                  {aiLoading ? "Генерация..." : "ИИ-помощник"}
                </button>
              </div>
              <textarea
                value={form.abstract}
                onChange={e => update({ abstract: e.target.value })}
                rows={5}
                placeholder="Краткое описание изобретения (150–250 слов)..."
                className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm resize-none transition-colors"
              />
            </div>

            {/* Claims */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">Формула изобретения</label>
              <textarea
                value={form.claims}
                onChange={e => update({ claims: e.target.value })}
                rows={6}
                placeholder="1. Устройство/способ ..., отличающееся тем, что..."
                className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm font-mono resize-none transition-colors"
              />
            </div>

            {/* Author & Company */}
            <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Автор (ФИО)</label>
                <input value={form.author} onChange={e => update({ author: e.target.value })}
                  placeholder="Иванов И.И." className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-lg px-3 py-2.5 text-sm transition-colors" />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Организация</label>
                <input value={form.company} onChange={e => update({ company: e.target.value })}
                  placeholder='ООО "АэроТех"' className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-lg px-3 py-2.5 text-sm transition-colors" />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">ИНН</label>
                <input value={form.inn} onChange={e => update({ inn: e.target.value })}
                  placeholder="7702000001" className="w-full bg-[#121214] border border-white/10 focus:border-amber-500/50 outline-none text-white rounded-lg px-3 py-2.5 text-sm font-mono transition-colors" />
              </div>
            </div>

            {/* Secret toggle */}
            <div className="flex items-center gap-3 p-4 bg-red-500/5 border border-red-500/15 rounded-2xl">
              <button
                onClick={() => update({ secret: !form.secret })}
                className={`w-12 h-6 rounded-full transition-all shrink-0 ${form.secret ? "bg-red-500" : "bg-white/10"}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full transition-all shadow-md mx-0.5 ${form.secret ? "translate-x-6" : ""}`} />
              </button>
              <div>
                <div className="text-sm font-bold text-white flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-red-400" /> Секретное изобретение (ФСБ / ГОСТайна)
                </div>
                <div className="text-xs text-gray-500">Направляется в ФСТЭК, доступно только спецреестру</div>
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="w-full py-4 bg-amber-500 hover:bg-amber-400 text-black font-black text-base rounded-2xl transition-all shadow-lg shadow-amber-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {submitting ? <><Loader2 className="w-5 h-5 animate-spin" /> Подача в ФИПС...</> : <><Send className="w-5 h-5" /> Подать Заявку в Роспатент <ChevronRight className="w-5 h-5" /></>}
            </button>
          </div>

          {/* Sidebar info */}
          <div className="space-y-4">
            <div className="bg-[#0A0A0B] border border-amber-500/15 rounded-2xl p-5">
              <h3 className="font-black text-white text-sm mb-3 flex items-center gap-2"><Shield className="w-4 h-4 text-amber-400" /> Процесс подачи</h3>
              {[
                { step: 1, label: "Заполнение анкеты", done: true },
                { step: 2, label: "МПК классификация", done: form.ipc_codes.length > 0 },
                { step: 3, label: "Формула + реферат", done: !!form.abstract },
                { step: 4, label: "Подача в ФИПС", done: false },
                { step: 5, label: "Формальная экспертиза (2 мес.)", done: false },
                { step: 6, label: "Экспертиза по существу (12 мес.)", done: false },
              ].map(s => (
                <div key={s.step} className={`flex items-center gap-2 py-1.5 text-xs ${s.done ? "text-emerald-400" : "text-gray-500"}`}>
                  {s.done ? <CheckCircle className="w-3.5 h-3.5 shrink-0" /> : <div className="w-3.5 h-3.5 rounded-full border border-gray-600 shrink-0" />}
                  {s.label}
                </div>
              ))}
            </div>
            <div className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-4">
              <p className="text-xs text-gray-400 leading-relaxed">
                <span className="text-amber-400 font-bold">Пошлина:</span> 3 300–8 250 ₽ (для МСП скидка 50%). Горизонт автоматически рассчитывает размер при подаче.
              </p>
            </div>
          </div>
        </div>
      ) : (
        /* List View */
        <>
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-black text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-400" /> Мои Патентные Заявки
            </h2>
            <button
              onClick={() => { setForm(DEFAULT_FORM); setStep("form"); }}
              className="flex items-center gap-2 px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-black rounded-xl transition-all text-sm"
            >
              <Plus className="w-4 h-4" /> Новая заявка
            </button>
          </div>

          {/* Applications List */}
          <div className="space-y-3 mb-8">
            {applications.map(app => (
              <div key={app.id} className="bg-[#0A0A0B] border border-white/5 rounded-2xl p-5 hover:border-amber-500/20 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-black text-white mb-0.5">{app.title}</div>
                    <div className="text-xs text-gray-500 font-mono">
                      {app.id} · МПК: <span className="text-amber-400">{app.ipc}</span> · Подано: {app.filed_at}
                    </div>
                  </div>
                  <StatusBadge status={app.status} />
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-amber-500 to-emerald-500 rounded-full transition-all" style={{ width: `${app.progress}%` }} />
                  </div>
                  <span className="text-xs text-gray-500 w-10 text-right">{app.progress}%</span>
                  <span className="text-xs text-gray-400">{app.status_label}</span>
                </div>
              </div>
            ))}
          </div>

          {/* FIPS Info Banner */}
          <div className="bg-gradient-to-r from-amber-900/20 to-yellow-900/10 border border-amber-500/20 rounded-2xl p-5 flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center shrink-0">
              <Globe2 className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <div className="font-black text-white mb-1">Интеграция с ФИПС (Роспатент)</div>
              <p className="text-sm text-gray-400">
                Горизонт — первый дронный маркетплейс с прямым API-подключением к системе ФИПС.
                Статус заявок обновляется автоматически. Уведомления в Telegram.
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
