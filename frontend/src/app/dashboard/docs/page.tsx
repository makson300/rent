"use client";

import { useState } from "react";
import { FileText, Printer, ShieldAlert } from "lucide-react";

export default function DocumentGenerator() {
  const [formData, setFormData] = useState({
    city: "Москва",
    date: new Date().toLocaleDateString('ru-RU'),
    lessor: "Иванов Иван Иванович",
    lessee: "Петров Петр Петрович",
    equipment: "Квадрокоптер DJI Mavic 3 Enterprise, серийный номер: ABC123XYZ",
    cost: "5000",
    rentalDays: "5",
    deposit: "50000",
  });

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 h-full">
      <div className="mb-8 print:hidden">
        <h1 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
          <FileText className="w-8 h-8 text-blue-400" />
          Генератор Договоров
        </h1>
        <p className="text-gray-400 max-w-2xl">
          Автоматическое формирование юридически значимых договоров аренды беспилотных систем (B2B/B2C). 
          Заполните форму слева и распечатайте/сохраните акт в PDF.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8 h-[calc(100vh-200px)] print:h-auto">
        
        {/* Editor (Left, hidden on print) */}
        <div className="w-full lg:w-[450px] shrink-0 bg-white/5 border border-white/10 p-6 rounded-3xl overflow-y-auto print:hidden shadow-xl custom-scrollbar">
          <h2 className="text-xl font-bold text-white mb-6">Реквизиты сделки</h2>
          
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Город заключения</label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({...formData, city: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Дата договора</label>
                <input
                  type="text"
                  value={formData.date}
                  onChange={(e) => setFormData({...formData, date: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Арендодатель (ФИО / ЮЛ)</label>
              <input
                type="text"
                value={formData.lessor}
                onChange={(e) => setFormData({...formData, lessor: e.target.value})}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Арендатор (ФИО / ЮЛ)</label>
              <input
                type="text"
                value={formData.lessee}
                onChange={(e) => setFormData({...formData, lessee: e.target.value})}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Предмет аренды (Оборудование)</label>
              <textarea
                value={formData.equipment}
                onChange={(e) => setFormData({...formData, equipment: e.target.value})}
                rows={3}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Арендная плата (Руб/День)</label>
                <input
                  type="number"
                  value={formData.cost}
                  onChange={(e) => setFormData({...formData, cost: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Срок аренды (Дней)</label>
                <input
                  type="number"
                  value={formData.rentalDays}
                  onChange={(e) => setFormData({...formData, rentalDays: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Залог (Оценочная стоимость, Руб)</label>
              <input
                type="number"
                value={formData.deposit}
                onChange={(e) => setFormData({...formData, deposit: e.target.value})}
                className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <button 
              onClick={handlePrint}
              className="mt-6 w-full flex justify-center items-center py-3.5 px-4 border rounded-xl font-bold transition-all bg-blue-600 border-blue-500 text-white hover:bg-blue-700 shadow-lg shadow-blue-500/20"
            >
              <Printer className="w-5 h-5 mr-2" />
              Скачать в PDF (Печать)
            </button>
            
            <div className="mt-4 flex items-start gap-3 p-4 rounded-xl bg-orange-500/10 border border-orange-500/20">
              <ShieldAlert className="w-5 h-5 text-orange-400 shrink-0 mt-0.5" />
              <p className="text-xs text-orange-200/80 leading-relaxed">
                Документ не имеет юридической силы, пока не подписан электронно-цифровой подписью (ЭЦП) или живой подписью сторон. 
                Внимательно проверяйте паспортные данные перед подписанием!
              </p>
            </div>
          </div>
        </div>

        {/* Live Preview (A4 Paper Document) */}
        <div className="flex-1 overflow-y-auto flex justify-center bg-[#0A0A0B] border border-white/5 rounded-3xl p-4 print:p-0 print:border-none print:bg-white custom-scrollbar">
          <div className="bg-white w-full max-w-[210mm] min-h-[297mm] shadow-2xl p-10 md:p-16 text-black print:shadow-none print:m-0 print:w-full print:max-w-none text-sm font-serif">
            
            <div className="text-center font-bold text-lg mb-8 uppercase tracking-wide border-b-2 border-black pb-4">
              ДОГОВОР АРЕНДЫ БЕСПИЛОТНОЙ ТЕХНИКИ И ОБОРУДОВАНИЯ № {Math.floor(Math.random() * 9000) + 1000}
            </div>

            <div className="flex justify-between mb-8">
              <span>г. {formData.city || "___________"}</span>
              <span>«{formData.date.split('.')[0] || "__"}» {formData.date.split('.')[1] || "____"} 20{formData.date.split('.')[2]?.substring(2) || "2_"} г.</span>
            </div>

            <div className="mb-6 leading-relaxed text-justify">
              Гражданин (или юридическое лицо) <b>{formData.lessor || "_________________________________"}</b>, именуемый в дальнейшем «Арендодатель», с одной стороны, и гражданин (или юридическое лицо) <b>{formData.lessee || "_________________________________"}</b>, именуемый в дальнейшем «Арендатор», с другой стороны, совместно именуемые «Стороны», заключили настоящий Договор о нижеследующем.
            </div>

            <div className="font-bold mb-3 uppercase">1. ПРЕДМЕТ ДОГОВОРА</div>
            <div className="mb-6 leading-relaxed text-justify pl-4">
              1.1. Арендодатель обязуется передать во временное пользование Арендатору принадлежащее Арендодателю на праве собственности оборудование, а именно:<br />
              <span className="inline-block border-b border-black min-w-[300px] mt-1 font-semibold">
                {formData.equipment || "______________________________________________________"}
              </span><br />
              (далее - «Оборудование»), а Арендатор обязуется принять Оборудование, выплачивать за его использование арендную плату и вернуть Оборудование Арендодателю в исправном состоянии.
            </div>

            <div className="font-bold mb-3 uppercase">2. АРЕНДНАЯ ПЛАТА И ПОРЯДОК РАСЧЕТОВ</div>
            <div className="mb-6 leading-relaxed text-justify pl-4">
              2.1. Арендная плата за пользование Оборудованием устанавливается в размере <b>{formData.cost || "_____"} руб.</b> за 1 (Один) календарный день аренды.<br />
              2.2. Срок аренды составляет <b>{formData.rentalDays || "_____"} дней</b>.<br />
              2.3. Итоговая сумма арендной платы по данному Договору составляет <b>{Number(formData.cost || 0) * Number(formData.rentalDays || 0)} руб.</b><br />
              2.4. В качестве обеспечения исполнения обязательств Арендатор вносит Арендодателю обеспечительный платеж (залог) в размере <b>{formData.deposit || "_____"} руб.</b>, который возвращается Арендатору после возврата Оборудования в исправном состоянии.
            </div>

            <div className="font-bold mb-3 uppercase">3. ПРАВА И ОБЯЗАННОСТИ СТОРОН</div>
            <div className="mb-6 leading-relaxed text-justify pl-4">
              3.1. Арендодатель обязан:<br />
              &nbsp;&nbsp;&nbsp;&nbsp;3.1.1. Передать Арендатору Оборудование в состоянии, пригодном для его использования по назначению, со всеми принадлежностями.<br />
              3.2. Арендатор обязан:<br />
              &nbsp;&nbsp;&nbsp;&nbsp;3.2.1. Использовать Оборудование бережно и исключительно по его прямому назначению, согласно требованиям безопасности эксплуатации беспилотных воздушных судов.<br />
              &nbsp;&nbsp;&nbsp;&nbsp;3.2.2. Не передавать Оборудование третьим лицам без письменного согласия Арендодателя.<br />
              &nbsp;&nbsp;&nbsp;&nbsp;3.2.3. В случае повреждения или утраты Оборудования полностью возместить Арендодателю его оценочную стоимость, указанную как залоговая сумма в пункте 2.4.
            </div>

            <div className="font-bold mb-3 uppercase">4. ОТВЕТСТВЕННОСТЬ СТОРОН</div>
            <div className="mb-8 leading-relaxed text-justify pl-4">
              4.1. Внешний пилот (Арендатор) принимает на себя всю полноту юридической и административной ответственности за соблюдение правил использования воздушного пространства РФ в период осуществления полетов арендованным Оборудованием.<br />
              4.2. При нарушении сроков возврата Оборудования Арендатор уплачивает пени в размере 5% от суммы аренды за каждый день просрочки.
            </div>

            <div className="grid grid-cols-2 gap-12 mt-12 pt-12 border-t-2 border-black">
              <div>
                <div className="font-bold mb-8 uppercase text-center border-b border-gray-300 pb-2">АРЕНДОДАТЕЛЬ</div>
                <div className="mb-4 text-sm font-medium">{formData.lessor}</div>
                <div className="mb-4">Подпись: ______________________</div>
                <div>М.П. (При наличии)</div>
              </div>
              <div>
                <div className="font-bold mb-8 uppercase text-center border-b border-gray-300 pb-2">АРЕНДАТОР</div>
                <div className="mb-4 text-sm font-medium">{formData.lessee}</div>
                <div className="mb-4">Подпись: ______________________</div>
                <div>М.П. (При наличии)</div>
              </div>
            </div>

            {/* Print Only Footer Watermark */}
            <div className="hidden print:block mt-16 text-center text-xs text-gray-400">
              Сформировано автоматически платформой [ Национальная Экосистема SkyRent ]
            </div>

          </div>
        </div>

      </div>

      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          body * {
            visibility: hidden;
          }
          .print\\:block, .print\\:block * {
            visibility: visible;
          }
          .print\\:hidden {
            display: none !important;
          }
          .flex-1 {
            position: absolute;
            left: 0;
            top: 0;
            margin: 0;
            padding: 0;
            width: 100%;
            visibility: visible;
          }
          .flex-1 * {
            visibility: visible;
          }
        }
        
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}} />
    </div>
  );
}
