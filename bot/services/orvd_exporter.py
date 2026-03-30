import io
import logging
from datetime import datetime
from aiogram import Bot

logger = logging.getLogger(__name__)

async def generate_orvd_document(flight_plan) -> io.BytesIO:
    """
    Генерирует юридически корректный текст Представления на ИВП для Системы ОрВД.
    Возвращает объект BytesIO (как текстовый файл).
    """
    # ШАБЛОН (Реализован на базе стандартных форм СППВ ЕС ОрВД)
    doc_text = f"""ПРЕДСТАВЛЕНИЕ НА УСТАНОВЛЕНИЕ МЕСТНОГО РЕЖИМА ИВП
(Сформировано автоматически системой 'Горизонт')

КОМУ: В региональный центр ЕС ОрВД

1. ДАТА ПОДАЧИ: {datetime.now().strftime("%d.%m.%Y")}
2. ТИП ВОЗДУШНОГО СУДНА: БВС (Беспилотное воздушное судно)
3. ОРГАНИЗАЦИЯ / ЗАКАЗЧИК: Пользователь ID {flight_plan.user_id}
4. ЦЕЛЬ ПОЛЕТОВ: {flight_plan.task_description if getattr(flight_plan, 'task_description', None) else 'Авиационные работы / Мониторинг'}

5. ПАРАМЕТРЫ ЗАПРАШИВАЕМОГО РЕЖИМА:
   А) Центр работ (Координаты): {flight_plan.coords}
   Б) Радиус: {getattr(flight_plan, 'radius_m', 500)} метров
   В) Истинная высота (ОТ и ДО): GND - {getattr(flight_plan, 'max_altitude_m', 150)} м AGL

6. СРОКИ ИВП (UTC):
   НАЧАЛО: {flight_plan.start_time.strftime('%Y-%m-%d %H:%M') if getattr(flight_plan, 'start_time', None) else 'По запросу'}
   ОКОНЧАНИЕ: {flight_plan.end_time.strftime('%Y-%m-%d %H:%M') if getattr(flight_plan, 'end_time', None) else 'По запросу'}

7. ОТВЕТСТВЕННОЕ ЛИЦО (РП):
   Контакты для оперативной связи: Уточняются через платформу Горизонт

ПРИМЕЧАНИЕ:
Полет будет проходить вне зон запретных для ИВП пространств (UHP, UHR, UHR/UHD), 
либо имеются соответствующие разрешения от органов власти. БВС находится в зоне 
прямой видимости. Метео-условия(VLOS) соблюдены. Силы ПВО/РЭБ в указанном квадрате 
отсутствуют (предварительное согласование пройдено успешно).

--------------------------------------------
Подпись / ФИО Пилота: ____________________
"""
    
    file_io = io.BytesIO(doc_text.encode('utf-8'))
    file_io.name = f"Predstavlenie_IVP_{flight_plan.id}.txt"
    return file_io
