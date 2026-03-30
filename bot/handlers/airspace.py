import logging
import math
from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from bot.keyboards.main_menu import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

# Very simple mock of Russian major airports NFZ for MVP (lat, lng, radius_km, type)
MOCK_NFZ_ZONES = [
    (55.408, 37.906, 15, "AERODROME", "Аэропорт Домодедово (UUDD)"),
    (55.972, 37.414, 15, "AERODROME", "Аэропорт Шереметьево (UUEE)"),
    (55.605, 37.286, 15, "AERODROME", "Аэропорт Внуково (UUWW)"),
    (55.755, 37.617, 10, "UAV_BAN", "Центр Москвы (УДЗ)"),
    (59.800, 30.262, 15, "AERODROME", "Аэропорт Пулково (ULLI)"),
    (43.449, 39.956, 15, "AERODROME", "Аэропорт Сочи (URSS)"),
    (55.012, 82.650, 15, "AERODROME", "Аэропорт Толмачево (UNNT)"),
    (57.173, 65.558, 15, "AERODROME", "Аэропорт Рощино (USTR)"),
    # Add an active emergency zone simulation
    (51.660, 39.200, 50, "MILITARY", "Опасность БПЛА / Временный режим (Воронеж)"), 
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def check_airspace(lat: float, lng: float):
    for z_lat, z_lng, radius, z_type, z_name in MOCK_NFZ_ZONES:
        dist = haversine(lat, lng, z_lat, z_lng)
        if dist <= radius:
            return {"status": "RED", "name": z_name, "distance": dist, "type": z_type, "radius": radius}
            
    # Default is green but requires simple notification in Russia usually
    return {"status": "GREEN", "name": "Воздушное пространство класса G", "distance": None}

@router.message(F.text == "📍 Зоны NFZ")
async def nfz_menu(message: types.Message):
    """Entry point for checking No Fly Zones"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить геопозицию", request_location=True)],
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "🗺 <b>Проверка полетных зон (Airspace Scanner)</b>\n\n"
        "Отправьте боту свою текущую геопозицию, чтобы проверить возможность "
        "выполнения полётов беспилотником (NFZ / Аэропорты / Временные ограничения).",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.message(F.location)
async def process_location(message: types.Message):
    """Processes location and returns NFZ status"""
    lat = message.location.latitude
    lng = message.location.longitude
    
    zone = check_airspace(lat, lng)
    
    if zone["status"] == "RED":
        text = (
            f"🔴 <b>ПОЛЕТ ЗАПРЕЩЕН (NFZ)</b>\n\n"
            f"Вы находитесь в закрытой зоне для полетов!\n"
            f"<b>Причина:</b> {zone['name']}\n"
            f"<b>Дистанция до центра зоны:</b> {zone['distance']:.2f} км\n"
            f"<b>Радиус ограничения:</b> {zone['radius']} км\n\n"
            f"<i>Запуск БПЛА без получения спец. разрешения (МРВ) в этой зоне влечет штраф или уголовную ответственность.</i>"
        )
    else:
        text = (
            f"🟢 <b>ПОЛЕТ РАЗРЕШЕН (КЛАСС G)</b>\n\n"
            f"В радиусе 15 км не обнаружено крупных аэропортов или жестких ограничений NFZ.\n"
            f"<b>Зона:</b> {zone['name']}\n\n"
            f"<i>Напоминаем: в некоторых регионах РФ действуют локальные указы губернаторов о запрете полетов БПЛА. Всегда уточняйте статус в местной администрации.</i>"
        )
        
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu())
