import { Book, ShieldAlert, BadgeInfo } from "lucide-react";

export default function LawsTab() {
  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <Book className="w-6 h-6 text-indigo-400" />
          Сводка Законов БВС
        </h2>
        <p className="text-gray-400 max-w-2xl text-sm">
          Актуальная правовая база для гражданских беспилотных воздушных судов в Российской Федерации. Незнание закона не освобождает от ответственности.
        </p>
      </div>

      <div className="space-y-4">
        <div className="p-5 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center gap-2">
            <BadgeInfo className="w-5 h-5 text-indigo-400" />
            Что нужно ставить на учет?
          </h3>
          <p className="text-gray-400 text-sm leading-relaxed mb-3">
            Согласно Воздушному кодексу РФ и Постановлению Правительства №658, все гражданские беспилотники взлетной массой <b>от 150 грамм до 30 килограмм</b> подлежат <u>обязательному государственному учету</u> в Росавиации. 
          </p>
          <ul className="list-disc list-inside text-sm text-gray-500 space-y-1">
            <li>Заявление нужно подать в течение <b>10 дней</b> после покупки.</li>
            <li>При ввозе из-за границы — в течение <b>10 дней</b> со дня ввоза.</li>
            <li>Регистрация через Госуслуги полностью бесплатна и занимает до 10 рабочих дней.</li>
            <li>Выданный учетный номер наносится на дрон (мин. 3 раза в разных местах маркером).</li>
          </ul>
        </div>

        <div className="p-5 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-400" />
            Где можно летать без разрешения (ИВП)?
          </h3>
          <p className="text-gray-400 text-sm leading-relaxed mb-3">
            Вы можете летать <b>БЕЗ</b> установления местного режима ИВП (без заявок в ОрВД), если одновременно соблюдены <b>ВСЕ</b> следующие условия:
          </p>
          <ul className="list-disc list-inside text-sm text-gray-500 space-y-1">
            <li>Светлое время суток в пределах прямой видимости.</li>
            <li>Высота полета не более <b>150 метров</b> от земли.</li>
            <li>Полет проходит <b>вне диспетчерских зон аэродромов</b> гражданской и гос. авиации.</li>
            <li>Полет проходит <b>вне запретных зон (NFZ)</b>, зон ограничения полетов, специальных зон, и вне мест проведения публичных мероприятий.</li>
            <li>При полетах над населенным пунктом: требуется согласование органа местного самоуправления (администрации).</li>
          </ul>
          <p className="text-xs text-indigo-300 mt-4 bg-indigo-500/10 p-2 rounded-lg border border-indigo-500/20">
            Внимание! В связи с режимом базовой готовности/режимом СВО, во многих регионах России действуют <b>прямые указы губернаторов о запрете полетов дронов</b>. В этих субъектах для запуска всегда требуется официальное разрешение оперштаба или профильного министерства.
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center gap-2">
            <BadgeInfo className="w-5 h-5 text-indigo-400" />
            Страхование Гражданской Ответственности (ГО)
          </h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            Статья 131 Воздушного кодекса РФ обязывает владельцев любых воздушных судов страховать свою ответственность перед третьими лицами за вред, причиненный при осуществлении полетов. Это означает, что для законного использования БВС необходимо иметь полис страхования ГО на весь период. Вы можете оформить его у нас в 1 клик через карточку дрона.
          </p>
        </div>
      </div>
    </div>
  );
}
