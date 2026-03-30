import logging
from aiogram import Router, types, F
from aiogram.types import FSInputFile
from db.base import async_session
from sqlalchemy import select
from db.models.job import Job
from db.models.user import User
from bot.services.documents import generate_b2b_contract

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.startswith("hire_pilot_"))
async def process_hire_pilot(callback: types.CallbackQuery):
    """
    Обработчик выбора пилота Заказчиком.
    Генерирует PDF-Договор подряда и отправляет его обеим сторонам.
    """
    await callback.answer("Подготовка договора...", show_alert=False)
    
    parts = callback.data.split("_")
    job_id = int(parts[2])
    pilot_id = int(parts[3])
    employer_id = callback.from_user.id
    
    async with async_session() as session:
        # Get Job
        job = await session.scalar(select(Job).where(Job.id == job_id))
        if not job:
            await callback.message.answer("Заказ не найден.")
            return
            
        # Get Employer
        employer = await session.scalar(select(User).where(User.telegram_id == employer_id))
        
        # Get Pilot
        pilot = await session.scalar(select(User).where(User.telegram_id == pilot_id))
        
        if not employer or not pilot:
            await callback.message.answer("Ошибка: пользователь не найден в базе.")
            return

        if job.status != "active":
            await callback.message.answer("Этот заказ уже закрыт или в процессе.")
            return

        # Update Job Status
        job.status = "in_progress"
        job.pilot_id = pilot.id
        await session.commit()
        
        employer_name = employer.first_name + (f" {employer.last_name}" if employer.last_name else "")
        pilot_name = pilot.first_name + (f" {pilot.last_name}" if pilot.last_name else "")
        
        # Call PDF Generator
        try:
            contract_path = generate_b2b_contract(
                job_id=job.id,
                employer_name=employer_name,
                pilot_name=pilot_name,
                job_title=job.title,
                budget=str(job.budget),
                city=job.city
            )
        except Exception as e:
            logger.error(f"Error generating PDF contract: {e}")
            await callback.message.answer("❌ Произошла ошибка при генерации PDF договора.")
            return
            
    # Send PDF to Employer
    try:
        pdf_file1 = FSInputFile(contract_path, filename=f"Договор_Заказ_SkyRent_{job.id}.pdf")
        await callback.message.answer_document(
            document=pdf_file1,
            caption="🎉 <b>Сделка начата!</b>\n\nСгенерирован автоматический Договор об оказании услуг.\nСвяжитесь с пилотом для начала работ.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error sending PDF to employer: {e}")
        
    # Send PDF to Pilot
    try:
        pdf_file2 = FSInputFile(contract_path, filename=f"Договор_Заказ_SkyRent_{job.id}.pdf")
        pilot_msg = (
            f"🎉 <b>Вас выбрали исполнителем!</b>\n\n"
            f"<b>Заказчик:</b> {employer_name}\n"
            f"<b>Задача:</b> {job.title}\n\n"
            f"Автоматический Договор подряда прикреплен ниже. Свяжитесь с заказчиком."
        )
        # Assuming pilot's telegram_id is pilot_id
        await callback.bot.send_document(
            chat_id=pilot.telegram_id,
            document=pdf_file2,
            caption=pilot_msg,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error sending PDF to pilot: {e}")

    # Remove inline buttons from the original message so they can't click it again
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith("job_view_"))
async def process_job_view(callback: types.CallbackQuery):
    """
    Обработчик просмотра вакансии (Аналитика кликов + MoMoA).
    """
    try:
        job_id = int(callback.data.split("_")[2])
    except IndexError:
        await callback.answer("Ошибка данных", show_alert=True)
        return
        
    async with async_session() as session:
        job = await session.get(Job, job_id)
        if not job:
            await callback.answer("Вакансия не найдена.", show_alert=True)
            return
            
        # Аналитика: Записываем +1 клик
        job.clicks_count = (job.clicks_count or 0) + 1
        await session.commit()
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        if job.source_url: # Парсинг с HH.ru
            url = job.source_url
            text = (
                f"🌐 <b>Вакансия агрегатора</b>\n\n"
                f"Для отклика перейдите по официальной ссылке ниже.\n"
                f"💡 <i>Совет: Перед откликом сгенерируйте Идеальное Сопроводительное Письмо с помощью нашего ИИ MoMoA на основе вашего профиля пилота!</i>"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Откликнуться на сайте", url=url)],
                [InlineKeyboardButton(text="🤖 Идеальный Отклик (MoMoA)", callback_data=f"momoa_cover_{job.id}")]
            ])
        else: # Внутренняя вакансия Горизонт
            text = (
                f"💼 <b>Внутренний Заказ Горизонт</b>\n\n"
                f"Откликнуться на этот коммерческий заказ можно через Web-App Экосистемы.\n"
                f"💡 <i>Совет: Используйте MoMoA для составления питча заказчику!</i>"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📲 Открыть WebApp", web_app=types.WebAppInfo(url=f"https://skyrent.pro/webapp"))],
                [InlineKeyboardButton(text="🤖 Идеальный Отклик (MoMoA)", callback_data=f"momoa_cover_{job.id}")]
            ])
            
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("momoa_cover_"))
async def generate_momoa_cover(callback: types.CallbackQuery):
    """
    Генерирует умное сопроводительное письмо отклика через MoMoA (Gemini AI).
    """
    try:
        job_id = int(callback.data.split("_")[2])
    except IndexError:
        await callback.answer("Ошибка данных", show_alert=True)
        return
        
    await callback.message.edit_text("⏳ <i>MoMoA изучает ваш профиль оборудования и требования работы...</i>", parse_mode="HTML")
    
    from db.models.listing import Listing
    
    async with async_session() as session:
        job = await session.get(Job, job_id)
        if not job:
            await callback.message.edit_text("Вакансия уже закрыта.")
            return
            
        pilot = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
        if not pilot:
            await callback.message.edit_text("Пройдите регистрацию как Пилот-оператор.")
            return
            
        result = await session.execute(select(Listing).where(Listing.user_id == pilot.id))
        pilot_listings = result.scalars().all()
        equipment = "\n".join([f"- {l.title}: {l.description[:300]}" for l in pilot_listings])
        
        from bot.config import GEMINI_API_KEY
        if not GEMINI_API_KEY:
            await callback.message.edit_text("❌ Функция MoMoA недоступна (не настроен ИИ ключ).")
            return
            
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
            
            prompt = (
                f"Твоя роль: MoMoA, профессиональный ИИ-карьерный консультант на рынке беспилотников и авиации.\n"
                f"Напиши идеальное, уверенное, краткое сопроводительное письмо для отклика пилота на эту вакансию заказчику:\n\n"
                f"Вакансия: {job.title}\n"
                f"Требования и Описание работы: {job.description}\n\n"
                f"Профиль Пилота:\n"
                f"Имя: {pilot.first_name}\n"
                f"Доступное оборудование и навыки: {equipment if equipment else 'Общие технические знания БПЛА, быстрая обучаемость'}\n\n"
                "Выдай только готовый текст самого письма. Убедительно свяжи оборудования пилота (если есть) с задачами вакансии. Текст должен быть готов к копированию (без приветствий от лица ИИ)."
            )
            
            response = await client.aio.models.generate_content(
                model='gemini-1.5-pro',
                contents=prompt
            )
            
            cover_letter = response.text
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="К заказам", web_app=types.WebAppInfo(url=f"https://skyrent.pro/webapp"))]
            ])
            if job.source_url:
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Отправить отклик", url=job.source_url)]
                ])
                
            text = (
                f"👨‍🚀 <b>MoMoA: Ваш Идеальный Отклик готов!</b>\n\n"
                f"<code>{cover_letter}</code>\n\n"
                f"<i>💡 Нажмите на текст в рамке выше, чтобы скопировать его, а затем перейдите по ссылке к отклику!</i>"
            )
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"MoMoA Error Cover Letter: {e}")
            await callback.message.edit_text("❌ Произошла ошибка связи с серверами MoMoA.")
