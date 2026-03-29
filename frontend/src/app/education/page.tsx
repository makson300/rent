import { BookOpen, MapPin, Clock, Users, ChevronRight, Award, Video, Building2 } from "lucide-react";
import Link from "next/link";

export const metadata = {
  title: "Обучение пилотированию БПЛА | SkyRent",
  description: "Академия SkyRent: Станьте профессиональным внешним пилотом дронов.",
};

const courses = [
  {
    id: "agro",
    title: "Пилот Агродрона",
    description: "Полный курс по управлению тяжелыми сельскохозяйственными дронами (DJI Agras, XAG). Внесение СЗР, построение маршрутов, обслуживание.",
    icon: <BookOpen className="w-8 h-8 text-emerald-400" />,
    format: "Гибридный (Теория + Практика)",
    duration: "3 недели",
    level: "С нуля",
    gradient: "from-emerald-900/40 to-[#0A0A0B]",
    border: "border-emerald-500/20",
    shadow: "shadow-emerald-500/10"
  },
  {
    id: "industrial",
    title: "Промышленные Инспекции",
    description: "Тепловизионная съемка, инспекция ЛЭП, нефтепроводов и вышек связи. Работа с DJI Matrice 350 RTK и полезными нагрузками Zenmuse.",
    icon: <Building2 className="w-8 h-8 text-orange-400" />,
    format: "Интенсив",
    duration: "2 недели",
    level: "Продвинутый",
    gradient: "from-orange-900/40 to-[#0A0A0B]",
    border: "border-orange-500/20",
    shadow: "shadow-orange-500/10"
  },
  {
    id: "photo",
    title: "Профессиональная Аэросъемка",
    description: "Кинематографичная съемка с воздуха. Настройки камеры, ND-фильтры, плавность пролетов, базовый монтаж FPV и DJI Mavic 3 Pro.",
    icon: <Video className="w-8 h-8 text-blue-400" />,
    format: "Онлайн + Выезд",
    duration: "1 месяц",
    level: "Базовый",
    gradient: "from-blue-900/40 to-[#0A0A0B]",
    border: "border-blue-500/20",
    shadow: "shadow-blue-500/10"
  },
  {
    id: "kids",
    title: "Школа Юных Пилотов",
    description: "Офлайн-занятия в Москве для детей 8-16 лет. Основы робототехники, сборка квадрокоптеров своими руками, веселые гонки на симуляторах.",
    icon: <Users className="w-8 h-8 text-purple-400" />,
    format: "Офлайн (Москва)",
    duration: "3 месяца",
    level: "Дети (8-16 лет)",
    gradient: "from-purple-900/40 to-[#0A0A0B]",
    border: "border-purple-500/20",
    shadow: "shadow-purple-500/10"
  }
];

export default function EducationPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="relative rounded-3xl overflow-hidden mb-16 border border-white/10">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/80 to-purple-900/80 pointer-events-none mix-blend-multiply" />
        <div className="relative bg-[#0A0A0B]/60 backdrop-blur-sm p-8 md:p-16 text-center md:text-left flex flex-col md:flex-row items-center gap-8">
          <div className="flex-1">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-400 text-sm font-semibold mb-6">
              <Award className="w-4 h-4" />
              Академия SkyRent
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-6 leading-tight">
              Освойте профессию <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">будущего</span> уже сегодня
            </h1>
            <p className="text-lg text-gray-300 mb-8 max-w-2xl leading-relaxed">
              От базовых навыков пилотирования до промышленных инспекций и агро-сферы. Обучайтесь у сертифицированных инструкторов на новейшем оборудовании.
            </p>
            <div className="flex flex-wrap gap-4 justify-center md:justify-start">
              <Link href="#programs" className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-all shadow-lg shadow-blue-500/25 hover:-translate-y-0.5">
                Подобрать программу
              </Link>
              <Link href="https://t.me/skyrent_education" target="_blank" className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-medium rounded-xl transition-all border border-white/10 backdrop-blur-md">
                Задать вопрос
              </Link>
            </div>
          </div>
          <div className="w-64 h-64 md:w-80 md:h-80 relative flex-shrink-0">
            <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-3xl animate-pulse" />
            <div className="w-full h-full bg-gradient-to-tr from-blue-600/20 to-purple-600/20 rounded-full border border-white/10 flex items-center justify-center relative backdrop-blur-sm">
              <Award className="w-32 h-32 text-white/80" />
            </div>
          </div>
        </div>
      </div>

      {/* Stats/Benefits */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        {[
          { num: "500+", label: "Выпускников" },
          { num: "12", label: "Профильных курсов" },
          { num: "98%", label: "Успешная сдача экзаменов" },
          { num: "№1", label: "Платформа в СНГ" }
        ].map((stat, i) => (
          <div key={i} className="bg-white/5 border border-white/5 rounded-2xl p-6 text-center">
            <div className="text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-gray-500 mb-2">
              {stat.num}
            </div>
            <div className="text-sm font-medium text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Courses Grid */}
      <h2 id="programs" className="text-3xl font-bold text-white mb-8 border-b border-white/5 pb-4">
        Образовательные Программы
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
        {courses.map((c) => (
          <div key={c.id} className={`bg-gradient-to-br ${c.gradient} border ${c.border} p-8 rounded-3xl relative overflow-hidden group hover:shadow-2xl ${c.shadow} transition-all duration-300 hover:-translate-y-1`}>
            <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:scale-110 transition-transform duration-500">
              {c.icon}
            </div>
            
            <div className="mb-6">{c.icon}</div>
            <h3 className="text-2xl font-bold text-white mb-4 relative z-10">{c.title}</h3>
            <p className="text-gray-400 mb-8 leading-relaxed relative z-10 min-h-[80px]">
              {c.description}
            </p>
            
            <div className="grid grid-cols-2 gap-4 mb-8 relative z-10">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <MapPin className="w-4 h-4 text-gray-500" />
                {c.format}
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <Clock className="w-4 h-4 text-gray-500" />
                {c.duration}
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300 col-span-2 mt-2">
                <Users className="w-4 h-4 text-gray-500" />
                Уровень: {c.level}
              </div>
            </div>

            <button className="w-full py-4 rounded-xl bg-white/10 hover:bg-white/20 border border-white/10 text-white font-semibold transition-all flex justify-between items-center px-6 group-hover:border-white/30 relative z-10">
              Узнать подробности
              <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
            </button>
          </div>
        ))}
      </div>
      
      {/* Test Center Card */}
      <div className="bg-blue-900/20 border border-blue-500/20 rounded-3xl p-8 md:p-12 flex flex-col md:flex-row items-center justify-between gap-8">
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">Независимый Центр Тестирования</h2>
          <p className="text-blue-200/80 mb-6 max-w-xl">
            Уже умеете летать, но нужен официальный статус и бейдж "Проверенный Пилот" в системе SkyRent? Сдайте теоретический и практический экзамен в нашем учебном центре.
          </p>
          <ul className="space-y-3 mb-8">
            <li className="flex items-center gap-3 text-sm text-blue-100">
              <div className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
                <div className="w-2 h-2 rounded-full bg-blue-400" />
              </div>
              Подтверждение налета книжкой пилота
            </li>
            <li className="flex items-center gap-3 text-sm text-blue-100">
              <div className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
                <div className="w-2 h-2 rounded-full bg-blue-400" />
              </div>
              Справка о прохождении ВЛЭК (если применимо)
            </li>
          </ul>
        </div>
        <div className="shrink-0 w-full md:w-auto">
          <Link href="/dashboard" className="block w-full px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-2xl text-center shadow-xl shadow-blue-500/20 transition-all">
            Подать заявку на бейдж
          </Link>
        </div>
      </div>
    </div>
  );
}
