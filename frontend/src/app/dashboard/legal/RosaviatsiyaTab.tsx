"use client";

import { useState } from "react";
import { ShieldCheck, Mail, FileText, Printer, Info } from "lucide-react";

export default function RosaviatsiyaTab() {
  const [formData, setFormData] = useState({
    owner_fio: "",
    owner_snils: "",
    owner_passport: "",
    owner_address: "",
    owner_phone: "",
    owner_email: "",
    drone_type: "",
    drone_serial: "",
    drone_weight: "0.249",
    drone_engine_type: "Электрический",
    drone_engine_count: "4",
  });

  const [leadSent, setLeadSent] = useState(false);
  const [isHoveringPrint, setIsHoveringPrint] = useState(false);

  const handlePrint = async () => {
    // 1. Посылаем лид на бекенд (тихо)
    if (!leadSent && formData.drone_type && formData.owner_fio) {
      try {
        const userStr = localStorage.getItem("user");
        let userId = 0;
        if (userStr) {
          userId = JSON.parse(userStr).id;
        }

        const { api } = await import("@/lib/api");
        await api.post("/lead_registration", {
            user_id: userId,
            drone_brand_model: formData.drone_type,
            serial_number: formData.drone_serial,
        });
        setLeadSent(true);
      } catch {
        console.error("Lead tracking failed silently");
      }
    }

    // 2. Печатаем
    window.print();
  };

  return (
    <div className="w-full">
      <div className="mb-6 print:hidden">
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <ShieldCheck className="w-6 h-6 text-indigo-400" />
          Учет в Росавиации
        </h2>
        <p className="text-gray-400 max-w-2xl text-sm">
          Система автоматически сформирует эталонное Заявление физического лица о постановке БВС на учет.
          Введенные паспортные данные <b>не передаются</b> на сервера SkyRent и остаются только в вашем браузере для генерации печатного бланка.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 print:hidden">
        {/* Left Column - Instructions & Form */}
        <div className="space-y-6">
          <div className="bg-indigo-900/20 border border-indigo-500/20 rounded-2xl p-5">
            <h3 className="text-white font-medium mb-3 flex items-center gap-2">
              <Mail className="w-5 h-5 text-indigo-400" />
              Как поставить дрон на учет?
            </h3>
            <ol className="list-decimal list-inside text-sm text-indigo-200/80 space-y-2">
              <li>Заполните анкету владельца и дрона ниже.</li>
              <li>Распечатайте Заявление, нажав на кнопку Печати.</li>
              <li>Поставьте личную подпись синей ручкой.</li>
              <li>Приложите 1 цветное фото БВС на светлом фоне (должно быть видно все элементы дрона).</li>
              <li>Отправьте пакет документов заказным письмом: <br/><b>125167, г. Москва, Ленинградский проспект, д. 37, корп. 2, Росавиация.</b></li>
            </ol>
            <p className="mt-3 text-xs text-indigo-400">
              *Также вы можете подать электронное заявление через портал Госуслуг (потребуется отсканировать СНИЛС и Паспорт).
            </p>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-400" />
              Анкета Владельца
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm text-gray-400 mb-1">ФИО полностью</label>
                <input
                  type="text"
                  placeholder="Иванов Иван Иванович"
                  value={formData.owner_fio}
                  onChange={(e) => setFormData({...formData, owner_fio: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm text-gray-400 mb-1">СНИЛС</label>
                <input
                  type="text"
                  placeholder="123-456-789 00"
                  value={formData.owner_snils}
                  onChange={(e) => setFormData({...formData, owner_snils: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm text-gray-400 mb-1">Паспорт (Серия, номер, кем и когда выдан, код)</label>
                <input
                  type="text"
                  placeholder="Серия 1234 № 567890, выдан ГУ МВД..."
                  value={formData.owner_passport}
                  onChange={(e) => setFormData({...formData, owner_passport: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm text-gray-400 mb-1">Адрес регистрации (по паспорту)</label>
                <input
                  type="text"
                  placeholder="г. Москва, ул. Ленина, д. 1, кв. 1"
                  value={formData.owner_address}
                  onChange={(e) => setFormData({...formData, owner_address: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Телефон</label>
                <input
                  type="text"
                  placeholder="+7 (999) 000-00-00"
                  value={formData.owner_phone}
                  onChange={(e) => setFormData({...formData, owner_phone: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">E-mail</label>
                <input
                  type="email"
                  placeholder="ivan@example.com"
                  value={formData.owner_email}
                  onChange={(e) => setFormData({...formData, owner_email: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <h3 className="text-lg font-medium text-white flex items-center gap-2 mt-6">
              <FileText className="w-5 h-5 text-gray-400" />
              Данные БВС (Дрона)
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm text-gray-400 mb-1">Наименование беспилотника (марка, модель)</label>
                <input
                  type="text"
                  placeholder="Квадрокоптер DJI Mavic 3"
                  value={formData.drone_type}
                  onChange={(e) => setFormData({...formData, drone_type: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm text-gray-400 mb-1">Серийный номер (или идентификационный номер)</label>
                <input
                  type="text"
                  placeholder="Например: 1581F..."
                  value={formData.drone_serial}
                  onChange={(e) => setFormData({...formData, drone_serial: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Тип двигателей</label>
                <select
                  value={formData.drone_engine_type}
                  onChange={(e) => setFormData({...formData, drone_engine_type: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="Электрический">Электрический</option>
                  <option value="Вынутреннего сгорания">Внутреннего сгорания</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Кол-во моторов</label>
                <input
                  type="number"
                  value={formData.drone_engine_count}
                  onChange={(e) => setFormData({...formData, drone_engine_count: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm text-gray-400 mb-1">Максимальная взлетная масса (MTOW), кг</label>
                <input
                  type="text"
                  placeholder="Например: 0.895"
                  value={formData.drone_weight}
                  onChange={(e) => setFormData({...formData, drone_weight: e.target.value})}
                  className="w-full px-4 py-2 bg-[#0A0A0B] border border-white/10 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Preview & Actions */}
        <div className="flex flex-col">
          <button
            onClick={handlePrint}
            onMouseEnter={() => setIsHoveringPrint(true)}
            onMouseLeave={() => setIsHoveringPrint(false)}
            className="w-full py-4 bg-white text-black font-medium rounded-xl hover:bg-gray-100 transition flex items-center justify-center gap-2 mb-4 group shadow-lg shadow-white/5"
          >
            <Printer className={`w-5 h-5 ${isHoveringPrint ? 'animate-bounce' : ''}`} />
            Распечатать и сохранить Заявление
          </button>
          
          <div className="flex-1 bg-white rounded-xl p-8 overflow-y-auto max-h-[600px] text-black shadow-inner">
            <div className="text-center opacity-30 text-xs font-mono mb-4 flex justify-center items-center gap-1">
              <Info className="w-3 h-3" />
              ПРЕДПРОСМОТР БЛАНКА
            </div>
            
            {/* Visual representation of the form */}
            <div className="text-xs space-y-4 font-serif leading-tight">
              <div className="text-right">
                <p>Приложение № 1<br/>к Административному регламенту</p>
                <p className="mt-4 font-bold">В Федеральное агентство<br/>воздушного транспорта (Росавиация)</p>
              </div>
              <h2 className="text-center font-bold text-sm mt-8 mb-4">
                ЗАЯВЛЕНИЕ<br/>
                о постановке беспилотного гражданского воздушного судна на государственный учет
              </h2>
              <p className="text-justify indent-8">
                Прошу поставить на государственный учет беспилотное гражданское воздушное судно со следующими характеристиками:
              </p>
              
              <table className="w-full border-collapse border border-black mt-4 mb-6">
                <tbody>
                  <tr>
                    <td className="border border-black p-2 w-1/2">Тип (наименование) беспилотного воздушного судна</td>
                    <td className="border border-black p-2 font-bold">{formData.drone_type || "__________________"}</td>
                  </tr>
                  <tr>
                    <td className="border border-black p-2">Серийный номер</td>
                    <td className="border border-black p-2 font-bold">{formData.drone_serial || "__________________"}</td>
                  </tr>
                  <tr>
                    <td className="border border-black p-2">Тип и количество двигателей</td>
                    <td className="border border-black p-2 font-bold">{formData.drone_engine_type || "___"}, {formData.drone_engine_count || "___"} шт.</td>
                  </tr>
                  <tr>
                    <td className="border border-black p-2">Максимальная взлетная масса</td>
                    <td className="border border-black p-2 font-bold">{formData.drone_weight || "___"} кг</td>
                  </tr>
                </tbody>
              </table>

              <p className="font-bold underline mt-6">Сведения о владельце беспилотного воздушного судна:</p>
              <p className="mt-2"><b>Ф.И.О.:</b> {formData.owner_fio || "___________________________"}</p>
              <p className="mt-1"><b>СНИЛС:</b> {formData.owner_snils || "___________________________"}</p>
              <p className="mt-1"><b>Паспортные данные:</b> {formData.owner_passport || "___________________________"}</p>
              <p className="mt-1"><b>Адрес места жительства:</b> {formData.owner_address || "___________________________"}</p>
              <p className="mt-1"><b>Телефон:</b> {formData.owner_phone || "___________________________"}</p>
              <p className="mt-1"><b>Адрес электронной почты:</b> {formData.owner_email || "___________________________"}</p>

              <div className="flex justify-between mt-12 pt-8">
                <div>М.П.<br/>(при наличии)</div>
                <div className="text-center">
                  ____________________<br/><span className="text-[10px]">(подпись)</span>
                </div>
                <div className="text-center">
                  ____________________<br/><span className="text-[10px]">(расшифровка подписи)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 
        =======================================================
        PRINT ONLY LAYOUT (Invisible on screen, visible in PDF)
        =======================================================
      */}
      <div className="hidden print:block print:bg-white print:text-black w-[100%] absolute top-0 left-0 bg-white p-8 font-serif leading-tight">
        <style type="text/css" media="print">
            {`
              @page { size: A4 portrait; margin: 20mm 15mm 20mm 20mm; }
              body { background-color: #fff; color: #000; display: block; }
            `}
        </style>
        <div className="text-right text-sm">
          <p>Приложение № 1<br/>к Административному регламенту<br/>Федерального агентства воздушного транспорта<br/>предоставления государственной услуги по учету<br/>беспилотных гражданских воздушных судов<br/>с максимальной взлетной массой<br/>от 0,15 килограмма до 30 килограммов,<br/>ввезенных в Российскую Федерацию или произведенных<br/>в Российской Федерации, утвержденному<br/>приказом Росавиации от 28 октября 2020 г. N 1331</p>
          <p className="mt-6 font-bold text-base">В Федеральное агентство<br/>воздушного транспорта (Росавиация)</p>
        </div>

        <h2 className="text-center font-bold text-lg mt-12 mb-6">
          ЗАЯВЛЕНИЕ<br/>
          о постановке беспилотного гражданского воздушного судна на государственный учет
        </h2>
        
        <p className="text-justify indent-8 text-base leading-relaxed">
          Прошу поставить на государственный учет беспилотное гражданское воздушное судно со следующими характеристиками:
        </p>
        
        <table className="w-full border-collapse border border-black mt-4 mb-8 text-sm">
          <tbody>
            <tr>
              <td className="border border-black p-3 w-1/2">Тип (наименование) беспилотного воздушного судна</td>
              <td className="border border-black p-3 font-bold">{formData.drone_type || ""}</td>
            </tr>
            <tr>
              <td className="border border-black p-3">Серийный номер (при наличии) (или идентификационный номер, присвоенный изготовителем)</td>
              <td className="border border-black p-3 font-bold">{formData.drone_serial || ""}</td>
            </tr>
            <tr>
              <td className="border border-black p-3">Количество двигателей (при наличии) и их вид (электрический, внутреннего сгорания)</td>
              <td className="border border-black p-3 font-bold">{formData.drone_engine_type || ""}, {formData.drone_engine_count || ""} шт.</td>
            </tr>
            <tr>
              <td className="border border-black p-3">Максимальная взлетная масса беспилотного воздушного судна</td>
              <td className="border border-black p-3 font-bold">{formData.drone_weight || ""} кг.</td>
            </tr>
          </tbody>
        </table>

        <p className="font-bold text-base mb-4">Сведения о владельце беспилотного воздушного судна:</p>
        <div className="text-base leading-loose">
          <p><b>Ф.И.О. владельца (индивидуального предпринимателя):</b> <span className="border-b border-black w-full inline-block font-bold">{formData.owner_fio || " "}</span></p>
          <p className="mt-2"><b>СНИЛС физического лица:</b> <span className="border-b border-black w-full inline-block font-bold">{formData.owner_snils || " "}</span></p>
          <p className="mt-2"><b>Данные документа, удостоверяющего личность:</b> 
            <span className="border-b border-black w-full inline-block font-bold leading-normal min-h-[1.5rem] break-words"> 
               {formData.owner_passport || " "}
            </span>
          </p>
          <p className="mt-2"><b>Адрес места жительства:</b> 
            <span className="border-b border-black w-full inline-block font-bold leading-normal min-h-[1.5rem] break-words">
              {formData.owner_address || " "}
            </span>
          </p>
          <p className="mt-2 text-sm text-gray-700 italic text-center">(Адрес, по которому должно быть направлено уведомление Росавиации)</p>
          <p className="mt-2"><b>Номер телефона:</b> <span className="border-b border-black w-full inline-block font-bold">{formData.owner_phone || " "}</span></p>
          <p className="mt-2"><b>Адрес электронной почты (при наличии):</b> <span className="border-b border-black w-full inline-block font-bold">{formData.owner_email || " "}</span></p>
        </div>

        <div className="flex justify-between items-end mt-24">
          <div className="text-center font-bold">
            "____"<br></br> _________________ 20___ г.
          </div>
          <div className="text-center">
            ____________________<br/><span className="text-xs font-normal">(подпись)</span>
          </div>
          <div className="text-center">
            ____________________<br/><span className="text-xs font-normal">(расшифровка подписи)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
