import logging
import json
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func

from bot.config import GEMINI_API_KEY
from db.models.listing import Listing
from db.models.user import User

try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

logger = logging.getLogger(__name__)

class SmartModerator:
    """
    Умный ИИ-Модератор для автоматической модерации объявлений и создания ежедневных отчетов.
    Использует библиотеку google-genai.
    """
    def __init__(self):
        if has_genai and GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
            self.model_name = 'gemini-2.5-flash'
        else:
            self.client = None
            logger.warning("google-genai не установлен или GEMINI_API_KEY пуст. Smart Moderator работает в режиме заглушки!")

    async def auto_moderate_listing(self, title: str, description: str, category: str, price: str) -> Dict[str, str]:
        """
        Анализирует текст объявления.
        Возвращает: {"status": "APPROVED" | "MANUAL_REVIEW", "reason": "..."}
        """
        if not self.client:
            await asyncio.sleep(1)
            # В режиме заглушки отправляем на ручную проверку
            return {"status": "MANUAL_REVIEW", "reason": "API ключ не настроен, ручная проверка."}

        system_instruction = (
            "You are an AI Moderator for a Drone/UAV rental and sales marketplace. "
            "Your job is to read the listing details and decide if it can be automatically published or requires manual admin review.\n"
            "Rules for AUTO-APPROVAL (100% confidence):\n"
            "- It's clearly about drones, cameras, UAV accessories, or operator services.\n"
            "- No profanity, spam, illegal items (weapons, drugs), or suspicious links.\n"
            "- Description makes sense.\n\n"
            "If it meets all rules, respond EXACTLY with:\n"
            '{"status": "APPROVED", "reason": "Looks good and safe."}\n\n'
            "If you have ANY doubts (weapons, spam, completely unrelated garbage), respond EXACTLY with:\n"
            '{"status": "MANUAL_REVIEW", "reason": "Mentioned [reason for doubt]."}\n\n'
            "Respond ONLY with valid JSON."
        )

        prompt = (
            f"Please analyze the following new listing:\n"
            f"Category: {category}\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Price: {price}\n"
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0
                )
            )
            
            raw_text = response.text.strip()
            # Clean up markdown JSON block if present
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                
            result = json.loads(raw_text)
            status = result.get("status", "MANUAL_REVIEW")
            reason = result.get("reason", "Parsed JSON successfully.")
            return {"status": status, "reason": reason}
            
        except Exception as e:
            logger.error(f"Smart Moderator AI Error: {e}")
            return {"status": "MANUAL_REVIEW", "reason": f"AI Parsing Error: {str(e)}"}

    async def generate_daily_report(self, session) -> str:
        """
        Генерирует умный ежедневный отчет (Daily Digest) для Администратора.
        """
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Получаем статистику за последние 24 часа
        new_users_query = await session.execute(select(func.count()).select_from(User).where(User.created_at >= yesterday))
        new_users = new_users_query.scalar() or 0
        
        new_listings_query = await session.execute(select(func.count()).select_from(Listing).where(Listing.created_at >= yesterday))
        total_listings_24h = new_listings_query.scalar() or 0
        
        auto_approved_query = await session.execute(
            select(func.count()).select_from(Listing)
            .where(Listing.created_at >= yesterday, Listing.status == 'active')
        )
        auto_approved = auto_approved_query.scalar() or 0
        
        manual_review = total_listings_24h - auto_approved

        if not self.client:
            return (
                f"📊 <b>Суточный Отчет (Заглушка)</b>\n\n"
                f"👥 Новых пользователей: {new_users}\n"
                f"📦 Новых объявлений: {total_listings_24h}\n"
                f"🤖 Авто-одобрено ИИ: {auto_approved}\n"
                f"✋ На ручной проверке: {manual_review}"
            )

        system_instruction = (
            "You are the SkyRent AI Analytics Assistant. "
            "Write a short, engaging daily digest for the platform administrator in Russian. "
            "Use emojis. Keep it concise (1-2 paragraphs)."
        )

        prompt = (
            f"Напиши суточный отчет (Daily Digest) на основе следующих данных:\n"
            f"- Новых регистраций за сутки: {new_users}\n"
            f"- Всего подано новых объявлений: {total_listings_24h}\n"
            f"- Из них Умный Модератор автоматически пропустил: {auto_approved}\n"
            f"- Отправлено админу на ручную проверку: {manual_review}\n\n"
            "Добавь короткий ободряющий комментарий."
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Daily Digest AI Error: {e}")
            return f"❌ Ошибка генерации отчета: {e}"

smart_moderator = SmartModerator()
