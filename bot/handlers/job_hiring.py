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
