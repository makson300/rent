import os
import json
import logging

try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

logger = logging.getLogger(__name__)

class SmartArbitrator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.has_genai = has_genai
        if self.has_genai and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Arbitrator: {e}")
                self.has_genai = False
        else:
            self.has_genai = False

    async def analyze_dispute(self, tender_title: str, tender_desc: str, plaintiff_claim: str, evidence: str) -> str:
        """
        Отдает Gemini спорные данные для вынесения саммари.
        Возвращает текстовый рапорт для Администратора.
        """
        if not self.has_genai:
            return "ИИ недоступен (GEMINI_API_KEY отсутствует). Требуется полный ручной разбор."

        prompt = f"""
        Ты — беспристрастный ИИ-помощник модератора (Арбитраж платформы "Горизонт").
        Твоя задача — проанализировать конфликт между Заказчиком и Исполнителем (пилотом БПЛА) и составить краткую, сухую выжимку фактов для администратора. Ты НЕ принимаешь финальное решение, ты только помогаешь живому человеку быстрее понять суть спора.

        ДАННЫЕ О КОНТРАКТЕ:
        Название: {tender_title}
        Описание ТЗ: {tender_desc}

        ВХОДНАЯ ЖАЛОБА (Суть спора):
        {plaintiff_claim}

        ДОКАЗАТЕЛЬСТВА (Переписка, логи, аргументы сторон):
        {evidence}

        Сформируй ответ строго по структуре:
        1. 📌 Суть претензии (1-2 предложения)
        2. 🔍 Аргументы сторон (кто на что ссылается)
        3. ⚖️ Зона нарушения ТЗ (было ли нарушение оригинального ТЗ?)
        4. 🤖 Рекомендация для Админа (например: "Рекомендуется выплата пилоту, так как ТЗ формально выполнено", или "Рекомендуется возврат 50% заказчику из-за брака").
        """
        
        try:
            import asyncio
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini Arbitrage Error: {e}")
            return f"Ошибка ИИ-анализа: {str(e)[:100]}. Ознакомьтесь с материалами вручную."

    async def check_dumping(self, tender_title: str, tender_budget: int, bid_amount: int) -> dict:
        """Анализирует отклик на предмет искусственного демпинга цены."""
        if not self.has_genai:
            return {"is_dumping": False, "reason": "AI offline"}

        prompt = f"""
        Ты - безжалостный B2B-модератор платформы аренды дронов "Горизонт".
        Твоя задача: проанализировать ценник пилота и определить, является ли он Искусственным Демпингом (преднамеренное сильное занижение цены для обвала рынка или мошенничества).

        ДАННЫЕ:
        Название задачи: {tender_title}
        Бюджет заказчика (НМЦК): {tender_budget} рублей
        Предложенная цена пилотом: {bid_amount} рублей

        УСЛОВИЕ:
        Если цена пилота экономически абсурдна для такой задачи на рынке БПЛА (например, скидка от бюджета составляет 40-50% и более, и цена ниже себестоимости амортизации дронов типа Matrice/Mavic 3E) - верни "is_dumping": true.
        Если это терпимая скидка (до 20-30%) - верни "is_dumping": false.
        
        Верни ТОЛЬКО валидный JSON (без маркдауна):
        {{"is_dumping": true, "reason": "Краткая аргументация, почему цена неадекватна"}}
        или
        {{"is_dumping": false, "reason": ""}}
        """
        
        try:
            import asyncio
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            t = response.text.strip()
            if t.startswith('```json'): t = t[7:]
            if t.endswith('```'): t = t[:-3]
            data = json.loads(t.strip())
            return {
                "is_dumping": data.get("is_dumping", False),
                "reason": data.get("reason", "")
            }
        except Exception as e:
            logger.error(f"Gemini Anti-Dumping Error: {e}")
            return {"is_dumping": False, "reason": f"AI Error: {e}"}

    async def open_auto_dispute(self, session, bot, dispute: 'EscrowDispute', tender, bid):
        """Открывает спор, анализирует ИИ, и рассылает вердикт админам платформы."""
        ai_summary = await self.analyze_dispute(
            tender_title=tender.title,
            tender_desc=tender.description,
            plaintiff_claim=dispute.reason,
            evidence=dispute.evidence_text or "Дополнительных доказательств не предоставлено"
        )
        
        dispute.ai_summary = ai_summary
        dispute.status = "ai_reviewed"
        session.add(dispute)
        await session.commit()
        
        # Отправка администраторам (Уведомление ИИ Судьи)
        from bot.config import ADMIN_IDS
        admin_text = (
            f"⚖️ <b>DISPUTE ALERT (ИИ Арбитр)</b>\n\n"
            f"<b>Тендер:</b> <i>{tender.title}</i> (ID: {tender.id})\n"
            f"<b>Заказчик ID:</b> <code>{tender.employer_id}</code>\n"
            f"<b>Подрядчик ID:</b> <code>{bid.contractor_id}</code>\n\n"
            f"<b>Жалоба:</b> {dispute.reason}\n\n"
            f"🤖 <b>Вывод ИИ:</b>\n{ai_summary}\n\n"
            f"🛠 <b>Действие:</b> Администратору необходимо вручную закрыть сделку в Дашборде."
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, admin_text, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Не удалось отправить алерт арбитража админу {admin_id}: {e}")

smart_arbitrator = SmartArbitrator()
