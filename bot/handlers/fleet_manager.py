import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from db.base import async_session
from db.models.fleet import FleetDrone, FleetBattery
from db.crud.user import get_user

router = Router()
logger = logging.getLogger(__name__)

class FleetAddState(StatesGroup):
    waiting_for_name = State()

@router.callback_query(F.data == "fleet_menu")
async def fleet_menu(callback: types.CallbackQuery, state: FSMContext):
    """Главная панель Ангара"""
    await state.clear()
    
    async with async_session() as session:
        user = await get_user(session, callback.from_user.id)
        if not user:
            return
            
        drones_res = await session.execute(select(FleetDrone).where(FleetDrone.user_id == user.id))
        drones = drones_res.scalars().all()
        
        bats_res = await session.execute(select(FleetBattery).where(FleetBattery.user_id == user.id))
        batteries = bats_res.scalars().all()

    text = "🔧 <b>Мой Ангар (Техническое Обслуживание)</b>\n\n"
    text += "Здесь вы можете вести учет вашего парка БПЛА и аккумуляторов. "
    text += "Система автоматически следит за износом (через Летную Книжку) и напомнит о замене пропеллеров.\n\n"
    
    text += "🚁 <b>Мои Дроны:</b>\n"
    if not drones:
        text += "<i>Нет добавленных дронов.</i>\n"
    else:
        for d in drones:
            warning = "⚠️ Требуется замена пропеллеров!" if d.total_flight_hours >= 200 else ""
            text += f"🔹 <b>{d.name}</b> — Налет: {d.total_flight_hours:.1f} ч. {warning}\n"
            
    text += "\n🔋 <b>Мои Аккумуляторы:</b>\n"
    if not batteries:
        text += "<i>Нет добавленных АКБ.</i>\n"
    else:
        for b in batteries:
            warning = "🥵 Ресурс исчерпан!" if b.charge_cycles >= 200 else ""
            text += f"🔸 <b>{b.name}</b> — Циклы: {b.charge_cycles} {warning}\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить Дрон", callback_data="fleet_add_drone"),
         InlineKeyboardButton(text="➕ Добавить АКБ", callback_data="fleet_add_bat")],
        [InlineKeyboardButton(text="🔙 Назад в профиль", callback_data="back_to_profile")]
    ])
    
    # We might be editing or sending a new message
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
        
    await callback.answer()

@router.callback_query(F.data.in_(["fleet_add_drone", "fleet_add_bat"]))
async def add_fleet_item(callback: types.CallbackQuery, state: FSMContext):
    item_type = "drone" if callback.data == "fleet_add_drone" else "battery"
    await state.update_data(item_type=item_type)
    
    name_str = "название дрона (например: DJI Mavic 3T)" if item_type == "drone" else "название АКБ (например: АКБ #1 Mavic 3)"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="fleet_menu")]
    ])
    
    await callback.message.edit_text(
        f"📝 Введите {name_str}:",
        reply_markup=kb
    )
    await state.set_state(FleetAddState.waiting_for_name)

@router.message(FleetAddState.waiting_for_name, F.text)
async def process_fleet_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item_type = data.get("item_type")
    
    async with async_session() as session:
        user = await get_user(session, message.from_user.id)
        if not user:
            return
            
        if item_type == "drone":
            item = FleetDrone(user_id=user.id, name=message.text)
        else:
            item = FleetBattery(user_id=user.id, name=message.text)
            
        session.add(item)
        await session.commit()
        
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В Ангар", callback_data="fleet_menu")]
    ])
    await message.answer(f"✅ Успешно добавлено в ангар!", reply_markup=kb)
