import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from db.base import async_session
from db.crud.user import get_user, create_user, update_user_phone
from bot.keyboards import get_main_menu, get_contact_keyboard
from bot.states import RegistrationStates

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "/version")
async def cmd_version(message: types.Message):
    await message.answer("🚀 <b>Sky Rent Hub v1.0.4 (Final Launch Ready)</b>\nBuild date: 2024-03-26", parse_mode="HTML")

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработка /start — приветствие + проверка регистрации"""
    async with async_session() as session:
        user = await get_user(session, message.from_user.id)

    if user and user.phone:
        # Пользователь уже зарегистрирован — показываем меню
        await message.answer(
            f"👋 С возвращением, {message.from_user.first_name}!\n\n"
            "Выберите раздел в меню ниже ⬇️\n"
            "<i>Если меню не появилось, используйте команду /menu</i>",
            parse_mode="HTML",
            reply_markup=get_main_menu(),
        )
        return

    if user and not user.phone:
        # Пользователь в БД, но не завершил регистрацию
        await message.answer(
            "📱 Для завершения регистрации отправьте свой контакт:",
            reply_markup=get_contact_keyboard(),
        )
        await state.set_state(RegistrationStates.waiting_for_contact)
        return

    # Новый пользователь — создаём запись и запрашиваем контакт
    async with async_session() as session:
        await create_user(
            session,
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )

    await message.answer(
        f"👋 Добро пожаловать в маркетплейс аренды оборудования!\n\n"
        "Здесь вы можете:\n"
        "🏠 Сдать или арендовать технику\n"
        "🎓 Найти курсы и обучающие материалы\n"
        "🆘 Разместить объявление о ЧП\n\n"
        "📱 Для начала, пожалуйста, поделитесь своим контактом:",
        reply_markup=get_contact_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_for_contact)


@router.message(F.text == "/menu")
@router.message(F.text == "🔝 В главное меню")
async def show_main_menu_command(message: types.Message, state: FSMContext):
    """Явный вызов главного меню"""
    await state.clear()
    await message.answer(
        "📱 <b>Главное меню</b>\n\n"
        "Выберите интересующий вас раздел:",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )


@router.message(RegistrationStates.waiting_for_contact, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    """Получение контакта — завершение регистрации"""
    phone = message.contact.phone_number
    logger.info("Registration: user %s sent contact %s", message.from_user.id, phone)

    async with async_session() as session:
        await update_user_phone(session, message.from_user.id, phone)

    from bot.keyboards.main_menu import get_user_type_keyboard
    await message.answer(
        "📝 <b>Последний шаг:</b>\n"
        "Укажите, пожалуйста, ваш статус:",
        parse_mode="HTML",
        reply_markup=get_user_type_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_for_user_type)


@router.callback_query(RegistrationStates.waiting_for_user_type, F.data.startswith("user_type_"))
async def process_user_type(callback: types.CallbackQuery, state: FSMContext):
    """Сохранение типа пользователя и завершение регистрации"""
    user_type = callback.data.split("_")[2]
    
    async with async_session() as session:
        from db.crud.user import update_user_type
        await update_user_type(session, callback.from_user.id, user_type)

    await state.clear()
    
    type_name = "Частное лицо" if user_type == "private" else "Компания / Прокат"
    
    await callback.message.edit_text(
        f"✅ Регистрация завершена!\n\n"
        f"Ваш статус: <b>{type_name}</b>\n\n"
        "Выберите раздел в меню ниже:",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "🔝 Главное меню доски объявлений:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(RegistrationStates.waiting_for_contact)
async def contact_invalid(message: types.Message):
    """Если пользователь отправил текст вместо контакта"""
    await message.answer(
        "⚠️ Пожалуйста, нажмите кнопку «📱 Поделиться контактом» ниже.",
        reply_markup=get_contact_keyboard(),
    )
