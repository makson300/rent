from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from db.base import async_session
from db.models.user import User
from bot.states.company import CompanyState

router = Router()

@router.callback_query(F.data == "setup_company")
async def start_company_setup(callback: CallbackQuery, state: FSMContext):
    """Начало перевода статуса на ИП/ООО."""
    await callback.message.edit_text(
        "🏢 <b>Регистрация Юридического Лица / ИП</b>\n\n"
        "Статус компании позволяет вам участвовать в крупных "
        "Государственных и Коммерческих закупках, которые работают только по 44-ФЗ и договорам.\n\n"
        "Пожалуйста, введите ваш <b>ИНН</b> (10 или 12 цифр):",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="my_profile")]])
    )
    await state.set_state(CompanyState.waiting_for_inn)

@router.message(CompanyState.waiting_for_inn)
async def process_inn(message: Message, state: FSMContext):
    inn = message.text.strip()
    
    # Очень простая валидация
    if not inn.isdigit() or len(inn) not in (10, 12):
        await message.answer("⚠️ Ошибка: ИНН должен состоять строго из 10 (для ООО) или 12 (для ИП) цифр. Попробуйте еще раз:")
        return
        
    await state.update_data(inn=inn)
    await message.answer(
        "✅ ИНН принят!\n\n"
        "Теперь введите <b>Краткое название вашей компании</b> "
        "(например: <i>ООО 'АэроМониторинг'</i> или <i>ИП Иванов И.И.</i>):",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Отмена", callback_data="my_profile")]])
    )
    await state.set_state(CompanyState.waiting_for_company_name)

@router.message(CompanyState.waiting_for_company_name)
async def process_company_name(message: Message, state: FSMContext):
    company_name = message.text.strip()
    
    if len(company_name) < 3 or len(company_name) > 100:
        await message.answer("⚠️ Название должно быть от 3 до 100 символов. Попробуйте снова:")
        return

    data = await state.get_data()
    inn = data['inn']
    user_id = message.from_user.id
    
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.user_type = "company"
            user.inn = inn
            user.company_name = company_name
            await session.commit()
            
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Мой профиль", callback_data="my_profile")]
    ])
    
    await message.answer(
        "🎉 <b>Ваш статус Компании подтвержден!</b>\n\n"
        "Теперь заказчики будут видеть вас как надежного корпоративного исполнителя. "
        "Вам стали полноценно доступны все B2G (Гос. Закупки) и B2B заказы на платформе Горизонт.",
        parse_mode="HTML",
        reply_markup=kb
    )
