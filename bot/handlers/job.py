from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.job import JobCreationState
from db.base import async_session
from db.models.job import Job
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config import ADMIN_IDS

router = Router()

def get_job_categories_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌾 Агро-дроны", callback_data="job_cat_Агро")],
            [InlineKeyboardButton(text="🎬 Кино и Реклама", callback_data="job_cat_Кино")],
            [InlineKeyboardButton(text="🗺 Картография", callback_data="job_cat_Карта")],
            [InlineKeyboardButton(text="🎉 Мероприятия", callback_data="job_cat_Ивенты")],
            [InlineKeyboardButton(text="🔍 Инспекция (ЛЭП, Трубы)", callback_data="job_cat_Инспекция")],
            [InlineKeyboardButton(text="🚁 FPV-съемка", callback_data="job_cat_FPV")]
        ]
    )

@router.message(F.text == "📝 Разместить Вакансию")
async def start_job_creation(message: types.Message, state: FSMContext):
    await message.answer(
        "💼 <b>Размещение Заказа на полет</b>\n\n"
        "Введите краткий заголовок задачи.\n"
        "<i>Например: Съемка фасада дома в Подмосковье</i>",
        parse_mode="HTML"
    )
    await state.set_state(JobCreationState.waiting_for_title)

@router.message(JobCreationState.waiting_for_title, F.text)
async def process_job_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(
        "📝 <b>Опишите задачу подробнее</b>\n\n"
        "Что именно нужно снять? Какое оборудование требуется (если знаете)? Сколько смен?",
        parse_mode="HTML"
    )
    await state.set_state(JobCreationState.waiting_for_description)

@router.message(JobCreationState.waiting_for_description, F.text)
async def process_job_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "Выберите категорию вашей задачи:",
        reply_markup=get_job_categories_keyboard()
    )
    await state.set_state(JobCreationState.waiting_for_category)

@router.callback_query(JobCreationState.waiting_for_category, F.data.startswith("job_cat_"))
async def process_job_category(callback: types.CallbackQuery, state: FSMContext):
    category_name = callback.data.split("_")[2]
    await state.update_data(category=category_name)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"✅ Категория: <b>{category_name}</b>\n\n"
        "📍 В каком городе или локации нужно выполнить работу?",
        parse_mode="HTML"
    )
    await state.set_state(JobCreationState.waiting_for_city)

@router.message(JobCreationState.waiting_for_city, F.text)
async def process_job_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(
        "💰 Какой бюджет вы закладываете за эту работу?\n\n"
        "<i>Укажите точную сумму или напишите 'По договоренности'</i>",
        parse_mode="HTML"
    )
    await state.set_state(JobCreationState.waiting_for_budget)

@router.message(JobCreationState.waiting_for_budget, F.text)
async def process_job_budget(message: types.Message, state: FSMContext):
    budget = message.text
    data = await state.get_data()
    
    # Save to db
    async with async_session() as session:
        new_job = Job(
            employer_id=message.from_user.id,
            title=data['title'],
            description=data['description'],
            category=data['category'],
            city=data['city'],
            budget=budget,
            status="pending"
        )
        session.add(new_job)
        await session.commit()
    
    await state.clear()
    
    # Text for user
    await message.answer(
        "✅ <b>Ваш заказ успешно создан!</b>\n\n"
        "Он отправлен на проверку модераторам. Как только он будет одобрен, пилоты увидят его в Web-Каталоге и смогут откликнуться.",
        parse_mode="HTML"
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"🆕 <b>Новая заявка на работу (Job)!</b>\n\n"
                     f"<b>Заголовок:</b> {data['title']}\n"
                     f"<b>Бюджет:</b> {budget}\n\n"
                     "<i>Перейдите в веб-панель администратора, чтобы одобрить ее.</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass
