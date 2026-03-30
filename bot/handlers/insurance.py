import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.keyboards.main_menu import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

class InsuranceStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_model = State()
    waiting_for_value_and_date = State()

@router.message(F.text == "🛡 Страхование")
async def insurance_start(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚗 ОСАГО (Ответственность)", callback_data="insure_type_osago")],
        [InlineKeyboardButton(text="🛡 КАСКО (Ущерб дрону)", callback_data="insure_type_kasko")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="insure_cancel")]
    ])
    
    await message.answer(
        "🛡 <b>Страхование БПЛА (Beta)</b>\n\n"
        "Обезопасьте свои полеты! Предлагаем два типа полисов:\n\n"
        "1. <b>ОСАГО</b> — Покрывает ущерб третьим лицам (если дрон упадет на машину или человека).\n"
        "2. <b>КАСКО</b> — Покрывает ущерб вашему дрону (краш, потеря сигнала, RTH fail).\n\n"
        "<i>Выберите желаемый тип полиса:</i>",
        parse_mode="HTML",
        reply_markup=kb
    )
    await state.set_state(InsuranceStates.waiting_for_type)

@router.callback_query(F.data == "insure_cancel")
async def insure_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заявка на страховку отменена.")
    await callback.answer()

@router.callback_query(F.data.startswith("insure_type_"), InsuranceStates.waiting_for_type)
async def process_insurance_type(callback: types.CallbackQuery, state: FSMContext):
    insure_type = callback.data.split("_")[2]
    await state.update_data(insure_type=insure_type)
    
    t_name = "ОСАГО" if insure_type == "osago" else "КАСКО"
    
    await callback.message.edit_text(
        f"Выбран полис: <b>{t_name}</b>\n\n"
        f"📝 Введите <b>Производителя и Модель дрона</b> (Например: <i>DJI Mavic 3T</i>):",
        parse_mode="HTML"
    )
    await state.set_state(InsuranceStates.waiting_for_model)
    await callback.answer()

@router.message(InsuranceStates.waiting_for_model, F.text)
async def process_insurance_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    
    await message.answer(
        "Отлично! 🗓 Теперь укажите <b>Дату вылета</b> и <b>Оценочную стоимость дрона</b> "
        "(Например: <i>25 мая, 350000 руб</i>):",
        parse_mode="HTML"
    )
    await state.set_state(InsuranceStates.waiting_for_value_and_date)

@router.message(InsuranceStates.waiting_for_value_and_date, F.text)
async def process_insurance_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    insure_type = data.get("insure_type")
    model = data.get("model")
    date_val = message.text
    
    t_name = "ОСАГО" if insure_type == "osago" else "КАСКО"
    
    # Calculate mock premium
    premium = 1500 if insure_type == "osago" else 4500
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить Пошлину", callback_data="insure_pay_mock")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="insure_cancel")]
    ])
    
    await message.answer(
        "📝 <b>Заявка на страховку сформирована!</b>\n\n"
        f"<b>Тип полиса:</b> {t_name}\n"
        f"<b>Дрон:</b> {model}\n"
        f"<b>Данные вылета:</b> {date_val}\n\n"
        f"<b>Предварительная премия:</b> ~{premium} ₽\n\n"
        f"Ваша анкета передана нашим партнерам (АльфаСтрахование / Сбер). Мы свяжемся с вами для выпуска цифрового полиса.",
        parse_mode="HTML",
        reply_markup=kb
    )
    await state.clear()

@router.callback_query(F.data == "insure_pay_mock")
async def insure_pay_mock(callback: types.CallbackQuery):
    await callback.answer("В разработке: Интеграция с ЮKassa API для прямого биллинга.", show_alert=True)
