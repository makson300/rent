import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.keyboards import get_main_menu
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.states.education import EducationApplyStates
from aiogram.fsm.state import State, StatesGroup

class EducationTestStates(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    score = State()
router = Router()
logger = logging.getLogger(__name__)

# --- ОБУЧЕНИЕ ---

@router.message(F.text == "🎓 Обучение")
async def education_main(message: types.Message):
    """Главный экран раздела Обучение"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 База знаний", callback_data="edu_base")],
        [InlineKeyboardButton(text="🎓 Пройти ИИ-Тест (Сертификат)", callback_data="edu_test_start")],
        [InlineKeyboardButton(text="💼 Обучение профессии", callback_data="edu_pro")],
        [InlineKeyboardButton(text="👶 Для детей (Offline MSK)", callback_data="edu_kids")]
    ])
    await message.answer(
        "🎓 <b>Раздел обучения</b>\n\n"
        "Выберите интересующее вас направление:",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data == "edu_base")
async def edu_base(callback: types.CallbackQuery):
    await callback.message.answer(
        "📚 <b>База знаний</b>\n\n"
        "Здесь собраны полезные статьи, чек-листы и инструкции по работе с оборудованием.\n\n"
        "<i>Раздел наполняется контентом...</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "edu_pro")
async def edu_pro(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚜 Агродроны", callback_data="edu_pro_agro")],
        [InlineKeyboardButton(text="🏗 Промышленные дроны", callback_data="edu_pro_ind")],
        [InlineKeyboardButton(text="📸 Профессиональная съемка", callback_data="edu_pro_photo")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="edu_back")]
    ])
    await callback.message.edit_text(
        "💼 <b>Обучение профессии</b>\n\n"
        "Выберите направление подготовки специалистов:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "edu_kids")
async def edu_kids(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Подать заявку", callback_data="edu_apply_kids")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="edu_back")]
    ])
    await callback.message.edit_text(
        "👶 <b>Обучение для детей</b>\n\n"
        "📍 Формат: Офлайн (Москва)\n"
        "👥 Возраст: от 8 до 16 лет\n\n"
        "Интересные занятия по пилотированию и основам робототехники под руководством опытных инструкторов.\n\n"
        "Нажмите кнопку ниже, чтобы подать заявку!",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "edu_apply_kids")
async def start_edu_apply(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 <b>Заявка на обучение</b>\n\nВведите имя ребенка:", parse_mode="HTML")
    await state.set_state(EducationApplyStates.waiting_for_name)
    await callback.answer()

@router.message(EducationApplyStates.waiting_for_name)
async def process_edu_name(message: types.Message, state: FSMContext):
    await state.update_data(child_name=message.text)
    await message.answer("Укажите возраст ребенка:")
    await state.set_state(EducationApplyStates.waiting_for_age)

@router.message(EducationApplyStates.waiting_for_age)
async def process_edu_age(message: types.Message, state: FSMContext):
    await state.update_data(child_age=message.text)
    await message.answer("Оставьте контактный номер телефона для связи:")
    await state.set_state(EducationApplyStates.waiting_for_phone)

@router.message(EducationApplyStates.waiting_for_phone)
async def process_edu_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    report = (
        "🚀 <b>НОВАЯ ЗАЯВКА (ДЕТИ)</b>\n\n"
        f"Ребенок: {data['child_name']}\n"
        f"Возраст: {data['child_age']}\n"
        f"Телефон: {message.text}\n"
        f"Отправитель: @{message.from_user.username or '—'}"
    )
    
    # Save to DB
    from db.models.education import EducationApplication
    from db.base import async_session
    
    async with async_session() as session:
        new_app = EducationApplication(
            user_id=message.from_user.id,
            child_name=data['child_name'],
            age=data['child_age'],
            phone=message.text
        )
        session.add(new_app)
        await session.commit()
        logger.info(f"Saved new education application from {message.from_user.id}")

    # Notify admin (optional logging/notification here)
    
    await state.clear()
    await message.answer(
        "✅ <b>Заявка принята!</b>\n\n"
        "Мы свяжемся с вами в ближайшее время для уточнения деталей.",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "edu_back")
async def edu_back(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 База знаний", callback_data="edu_base")],
        [InlineKeyboardButton(text="💼 Обучение профессии", callback_data="edu_pro")],
        [InlineKeyboardButton(text="👶 Для детей (Offline MSK)", callback_data="edu_kids")]
    ])
    await callback.message.edit_text(
        "🎓 <b>Раздел обучения</b>\n\n"
        "Выберите интересующее вас направление:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

# --- ПРАВИЛА ---

@router.callback_query(F.data == "edu_test_start")
async def start_edu_test(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EducationTestStates.q1)
    await state.update_data(score=0)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="А) 150 метров", callback_data="test_q1_150")],
        [InlineKeyboardButton(text="Б) 500 метров", callback_data="test_q1_500")],
        [InlineKeyboardButton(text="В) Без ограничений", callback_data="test_q1_inf")]
    ])
    
    await callback.message.edit_text(
        "🎓 <b>ИИ Академия Горизонт</b>\n\n"
        "Вопрос 1/3:\n"
        "Какая максимальная высота полета БПЛА без установления местного режима (ИВП) в прямой видимости вне диспетчерских зон?\n",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(EducationTestStates.q1, F.data.startswith("test_q1_"))
async def process_test_q1(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 0)
    
    if callback.data == "test_q1_150":
        score += 1
        
    await state.update_data(score=score)
    await state.set_state(EducationTestStates.q2)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="А) Да, если дрон легкий", callback_data="test_q2_yes")],
        [InlineKeyboardButton(text="Б) Нет, категорически запрещено", callback_data="test_q2_no")]
    ])
    
    await callback.message.edit_text(
        "Вопрос 2/3:\nМожно ли летать над неконтролируемой толпой людей на массовых мероприятиях без специальных разрешений?",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(EducationTestStates.q2, F.data.startswith("test_q2_"))
async def process_test_q2(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 0)
    
    if callback.data == "test_q2_no":
        score += 1
        
    await state.update_data(score=score)
    await state.set_state(EducationTestStates.q3)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="А) Поставить на учет в Росавиации", callback_data="test_q3_reg")],
        [InlineKeyboardButton(text="Б) Просто приклеить наклейку с номером телефона", callback_data="test_q3_phone")]
    ])
    
    await callback.message.edit_text(
        "Вопрос 3/3:\nЧто обязательно нужно сделать с дроном тяжелее 150 грамм после покупки?",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(EducationTestStates.q3, F.data.startswith("test_q3_"))
async def process_test_q3(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 0)
    
    if callback.data == "test_q3_reg":
        score += 1
        
    await state.clear()
    
    if score >= 2:
        username = callback.from_user.full_name
        cert_text = (
            "🎓 <b>СЕРТИФИКАТ ВЫПУСКНИКА</b> 🎓\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"Настоящий сертификат подтверждает, что\n"
            f"<b>{username}</b>\n"
            "успешно прошел(ла) базовый курс\n"
            "по безопасности полетов БПЛА в\n"
            "Национальной экосистеме «Горизонт».\n\n"
            f"Оценка ИИ-теста: {score}/3 балла.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>(Вы можете сохранить этот сертификат)</i>"
        )
        await callback.message.edit_text(cert_text, parse_mode="HTML")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Сдать заново", callback_data="edu_test_start")]
        ])
        await callback.message.edit_text(
            f"К сожалению, вы не прошли тест ({score}/3).\nИзучите Базу Знаний и попробуйте еще раз!",
            reply_markup=kb
        )
    await callback.answer()

@router.message(F.text == "📜 Правила и условия")
async def rules_main(message: types.Message):
    """Раздел Правил и рекомендаций"""
    text = (
        "📜 <b>Правила и рекомендации</b>\n\n"
        "⚠️ <b>Отказ от ответственности:</b>\n"
        "Наш бот является информационным ресурсом (доской объявлений). "
        "Мы берем плату исключительно за услуги размещения объявлений. "
        "<b>Мы не являемся стороной сделки и не несем ответственности за действия пользователей.</b>\n\n"
        "💡 <b>Рекомендации:</b>\n\n"
        "👤 <b>Для тех, кто сдает:</b>\n"
        "• Всегда проверяйте документы арендатора.\n"
        "• Составляйте акт приема-передачи оборудования.\n"
        "• Берите залог (денежный или паспортный, если это законно в вашем регионе).\n"
        "• Снимайте видео работы оборудования при выдаче.\n\n"
        "🔍 <b>Для тех, кто арендует:</b>\n"
        "• Проверяйте оборудование при получении.\n"
        "• Уточняйте условия ответственности при поломке.\n"
        "• Не переводите предоплату незнакомым лицам без гарантий."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu())
