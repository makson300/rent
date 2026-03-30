"use client";

import { useState } from "react";
import {
  BookOpenCheck, Play, Lock, CheckCircle, Star, Clock,
  Award, TrendingUp, ChevronRight, Trophy, Zap, BarChart2,
  FileText, Users, Shield
} from "lucide-react";
import { toast } from "react-hot-toast";
import { academyApi, type CourseEnrollment } from "@/lib/api";
import { useApiData } from "@/hooks/useApiData";

// Категории курсов
const CATEGORIES = ["Все", "Пилотирование", "B2G Тендеры", "Аэрофотосъёмка", "ТО и Ремонт", "Законодательство", "Инженерия"];

// Каталог курсов
const COURSES = [
  {
    id: 1, category: "Пилотирование", level: "Начальный",
    title: "Базовый курс пилота БПЛА (ДОСААФ)",
    desc: "Основы управления, предполётная подготовка, права и ограничения. Официальная программа ДОСААФ.",
    duration_h: 12, lessons: 18, students: 1247, rating: 4.9,
    price: 0, certified: true, completed: true,
    badge: "🚁", color: "from-blue-600 to-indigo-700",
  },
  {
    id: 2, category: "B2G Тендеры", level: "Продвинутый",
    title: "B2G Тендеры: от заявки до победы",
    desc: "Как читать ФЗ-44 и ФЗ-223, формировать КП, избегать демпинга. Разбор реальных госзаказов.",
    duration_h: 8, lessons: 12, students: 483, rating: 4.8,
    price: 4900, certified: true, completed: false,
    badge: "📋", color: "from-amber-600 to-yellow-700",
  },
  {
    id: 3, category: "Аэрофотосъёмка", level: "Средний",
    title: "Фотограмметрия и Ортофотоплан",
    desc: "Создание цифровых моделей рельефа, обработка в Agisoft Metashape / Pix4D. Практика на реальных объектах.",
    duration_h: 20, lessons: 24, students: 312, rating: 4.7,
    price: 7900, certified: true, completed: false,
    badge: "🗺️", color: "from-emerald-600 to-teal-700",
  },
  {
    id: 4, category: "Законодательство", level: "Начальный",
    title: "Правовой Минимум Пилота (ФАП-69 + ОрВД)",
    desc: "Обязательный курс: постановка на учёт в Росавиации, зоны запрета, взаимодействие с ОрВД.",
    duration_h: 4, lessons: 8, students: 2103, rating: 4.6,
    price: 0, certified: false, completed: true,
    badge: "⚖️", color: "from-violet-600 to-purple-700",
  },
  {
    id: 5, category: "Инженерия", level: "Эксперт",
    title: "Конструирование БПЛА: от идеи до прототипа",
    desc: "Аэродинамика, выбор силовой установки, расчёт веса и ЦТ, 3D-печать рамы и интеграция полётного контроллера.",
    duration_h: 40, lessons: 52, students: 87, rating: 4.9,
    price: 24900, certified: true, completed: false,
    badge: "🔧", color: "from-cyan-600 to-blue-700",
  },
  {
    id: 6, category: "ТО и Ремонт", level: "Средний",
    title: "Техническое обслуживание агро-БВС",
    desc: "Регламентные работы на DJI Agras / Геоскан Агро: калибровка, замена пропеллеров, промывка системы СЗР.",
    duration_h: 6, lessons: 9, students: 194, rating: 4.5,
    price: 3500, certified: false, completed: false,
    badge: "🛠️", color: "from-rose-600 to-red-700",
  },
];

const LEVEL_COLOR: Record<string, string> = {
  "Начальный":   "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  "Средний":     "text-amber-400 bg-amber-500/10 border-amber-500/30",
  "Продвинутый": "text-blue-400 bg-blue-500/10 border-blue-500/30",
  "Эксперт":     "text-violet-400 bg-violet-500/10 border-violet-500/30",
};

// Сертификаты пользователя
const MY_CERTS = [
  { id: "GRZ-2026-001", title: "Базовый пилот БПЛА (ДОСААФ)", issued: "2026-01-15", valid: "2029-01-15" },
  { id: "GRZ-2026-002", title: "Правовой минимум пилота", issued: "2026-02-03", valid: "2029-02-03" },
];

export default function AcademyPage() {
  const [category, setCategory] = useState("Все");
  const [tab, setTab] = useState<"catalog" | "my" | "certs">("catalog");
  const [enrolling, setEnrolling] = useState<number | null>(null);

  const { data: enrollments, refetch: refetchEnrollments } = useApiData(
    () => academyApi.enrollments()
  );

  const enrolledIds = new Set((enrollments ?? []).map(e => e.course_id));
  const myCertificates = (enrollments ?? []).filter(e => e.certificate_issued);
  const myCoursesList  = (enrollments ?? []).filter(e => !e.is_completed);

  const filtered = COURSES.filter(c => category === "Все" || c.category === category);

  const handleEnroll = async (course: typeof COURSES[0]) => {
    if (enrolledIds.has(course.id)) {
      toast("Уже записаны на этот курс ✅");
      return;
    }
    if (course.price > 0) {
      toast(`Переход к оплате: ${course.price.toLocaleString("ru-RU")} ₽`);
      return;
    }
    setEnrolling(course.id);
    try {
      await academyApi.enroll(course.id, course.title);
      toast.success(`Записаны: «${course.title}»!`);
      refetchEnrollments();
    } catch (err: unknown) {
      const e = err as { detail?: string };
      if (e.detail?.includes("Already enrolled")) {
        toast("Уже записаны ✅");
      } else {
        toast.error(e.detail ?? "Ошибка записи");
      }
    } finally {
      setEnrolling(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <span className="px-3 py-1 rounded-full bg-indigo-500/15 text-indigo-400 text-xs font-black uppercase tracking-wider mb-3 inline-flex items-center gap-1.5">
          <BookOpenCheck className="w-3.5 h-3.5" /> Фаза 44 · Академия Горизонт
        </span>
        <h1 className="text-4xl font-extrabold text-white mb-3 flex items-center gap-3">
          <Award className="w-8 h-8 text-indigo-400" />
          Академия «Горизонт»
        </h1>
        <p className="text-gray-400 max-w-3xl">
          Курсы, сертификаты и менторство от ведущих экспертов отрасли БПЛА.
          Обучение по стандартам <span className="text-indigo-400 font-bold">ДОСААФ</span> и{" "}
          <span className="text-indigo-400 font-bold">Росавиации</span>.
        </p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        {[
          { label: "Курсов", val: COURSES.length, icon: <BookOpenCheck className="w-4 h-4 text-indigo-400" /> },
          { label: "Обучающихся", val: "4 400+", icon: <Users className="w-4 h-4 text-blue-400" /> },
          { label: "Сертификатов выдано", val: "1 830", icon: <Shield className="w-4 h-4 text-emerald-400" /> },
          { label: "Ср. рейтинг", val: "4.8 ⭐", icon: <Star className="w-4 h-4 text-amber-400" /> },
        ].map((s, i) => (
          <div key={i} className="bg-[#0E0E10] border border-white/5 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-1">{s.icon}<span className="text-xs text-gray-500">{s.label}</span></div>
            <div className="text-2xl font-black text-white">{s.val}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10 mb-6 gap-1">
        {(["catalog", "my", "certs"] as const).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-5 py-2.5 text-sm font-bold border-b-2 transition-colors ${tab === t ? "border-indigo-500 text-indigo-400" : "border-transparent text-gray-400 hover:text-white"}`}
          >
            {t === "catalog" ? "Каталог курсов" : t === "my" ? "Мои курсы" : "Мои сертификаты"}
          </button>
        ))}
      </div>

      {tab === "catalog" && (
        <>
          {/* Category filter */}
          <div className="flex flex-wrap gap-2 mb-6">
            {CATEGORIES.map(c => (
              <button
                key={c}
                onClick={() => setCategory(c)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
                  category === c ? "bg-indigo-600 text-white border-indigo-500" : "bg-[#0E0E10] text-gray-400 border-white/10 hover:border-white/20"
                }`}
              >{c}</button>
            ))}
          </div>

          {/* Course Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map(course => (
              <div key={course.id} className={`bg-[#0A0A0B] border rounded-3xl overflow-hidden transition-all hover:scale-[1.01] ${course.completed ? "border-emerald-500/20" : "border-white/5 hover:border-indigo-500/20"}`}>
                {/* Course Header */}
                <div className={`bg-gradient-to-br ${course.color} p-6 relative overflow-hidden`}>
                  <div className="text-4xl mb-2">{course.badge}</div>
                  <div className={`inline-flex items-center px-2 py-0.5 rounded border text-[10px] font-black ${LEVEL_COLOR[course.level]}`}>
                    {course.level}
                  </div>
                  {course.completed && (
                    <div className="absolute top-3 right-3 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>

                {/* Course Body */}
                <div className="p-5">
                  <h3 className="font-black text-white text-sm mb-1 leading-tight">{course.title}</h3>
                  <p className="text-xs text-gray-500 mb-3 leading-relaxed">{course.desc}</p>

                  <div className="flex flex-wrap gap-3 text-xs text-gray-500 mb-4">
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {course.duration_h} ч</span>
                    <span className="flex items-center gap-1"><FileText className="w-3 h-3" /> {course.lessons} уроков</span>
                    <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {course.students}</span>
                    <span className="flex items-center gap-1"><Star className="w-3 h-3 text-amber-400" /> {course.rating}</span>
                  </div>

                  {course.certified && (
                    <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 mb-3">
                      <Shield className="w-3.5 h-3.5" /> Выдаётся сертификат Горизонт
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="font-black text-white">
                      {course.price === 0 ? (
                        <span className="text-emerald-400">Бесплатно</span>
                      ) : (
                        <span>{course.price.toLocaleString("ru-RU")} ₽</span>
                      )}
                    </div>
                    <button
                      onClick={() => handleEnroll(course)}
                      className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-black transition-all ${
                        course.completed
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-indigo-600 hover:bg-indigo-500 text-white"
                      }`}
                    >
                      {course.completed ? <><CheckCircle className="w-3.5 h-3.5" /> Пройден</> : <><Play className="w-3.5 h-3.5" /> Начать</>}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {tab === "my" && (
        <div className="space-y-3">
          {(myCoursesList.length === 0) ? (
            <div className="text-center py-16 text-gray-500">Вы ещё не записаны ни на один курс</div>
          ) : myCoursesList.map((enr: CourseEnrollment) => (
            <div key={enr.id} className="bg-[#0A0A0B] border border-indigo-500/20 rounded-2xl p-5 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-xl">🎓</div>
              <div className="flex-1">
                <div className="font-black text-white">{enr.course_title}</div>
                <div className="text-xs text-gray-500">Прогресс: {enr.progress_pct}%</div>
                <div className="h-1 bg-white/5 rounded-full mt-1.5 overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${enr.progress_pct}%` }} />
                </div>
              </div>
              {enr.is_completed && (
                <div className="flex items-center gap-2 text-emerald-400 text-sm font-black">
                  <CheckCircle className="w-5 h-5" /> Завершён
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === "certs" && (
        <div className="space-y-3">
          {myCertificates.length === 0 ? (
            <div className="text-center py-16 text-gray-500">Сертификаты появятся после завершения курса</div>
          ) : myCertificates.map((cert: CourseEnrollment) => (
            <div key={cert.id} className="bg-gradient-to-r from-[#0A0A0B] to-indigo-900/10 border border-indigo-500/20 rounded-2xl p-6 flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-indigo-500/15 flex items-center justify-center shrink-0">
                  <Award className="w-6 h-6 text-indigo-400" />
                </div>
                <div>
                  <div className="font-black text-white mb-1">{cert.course_title}</div>
                  <div className="text-xs text-gray-500 font-mono">№ {cert.cert_number ?? "GRZ-pending"}</div>
                  <div className="text-xs text-gray-600 mt-0.5">Записан: {new Date(cert.enrolled_at).toLocaleDateString("ru-RU")}</div>
                </div>
              </div>
              <button className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-400 text-xs font-bold rounded-lg transition-all">
                Скачать PDF
              </button>
            </div>
          ))}
          <div className="text-center py-4 text-xs text-gray-600">
            Все сертификаты верифицированы в реестре «Горизонт» и доступны для проверки по QR-коду.
          </div>
        </div>
      )}
    </div>
  );
}
