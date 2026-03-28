import logging
import json
from datetime import datetime
from bot.config import GEMINI_API_KEY
import asyncio

try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

logger = logging.getLogger(__name__)

class AdvisorService:
    """
    Интеграция MoMoA для Админ-панели (Chief Advisor).
    Анализирует статистику и выдает ежедневные планы/отвечает на вопросы.
    """
    def __init__(self):
        if hasattr(self, 'client'):
            return
            
        if has_genai and GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
            self.model_name = 'gemini-1.5-pro'
        else:
            self.client = None
            logger.warning("google-genai не установлен или GEMINI_API_KEY пуст. Advisor работает в режиме заглушки!")

    def _build_context_prompt(self, stats: dict) -> str:
        date_str = datetime.now().strftime("%d.%m.%Y")
        ctx = (
            f"Текущая дата: {date_str}\n"
            f"Статистика платформы аренды БПЛА и ЧП:\n"
            f"- Всего пользователей: {stats.get('total_users', 0)}\n"
            f"- Новых за месяц: {stats.get('new_users_month', 0)}\n"
            f"- Активных объявлений (Аренда): {stats.get('rent_listings', 0)}\n"
            f"- Активных объявлений (Продажа): {stats.get('sale_listings', 0)}\n"
            f"- Зарегистрировано Операторов: {stats.get('operators_count', 0)}\n"
            f"- Всего заявок на ЧП (Emergency): {stats.get('total_emergencies', 0)}\n"
            f"- Доход платформы (примерно): {stats.get('revenue', 0)} руб.\n\n"
        )
        return ctx

    async def generate_daily_plan(self, stats: dict) -> str:
        """Генерует проактивный ежедневный план развития на базе свежей статистики"""
        if not self.client:
            await asyncio.sleep(1)
            return "🤖 Заглушка: API ключ не настроен. Сегодня сфокусируйтесь на привлечении операторов!"

        sys_prompt = (
            "Ты — Главный Советник и Продакт-менеджер (Chief Advisor) развивающегося стартапа "
            "в сфере аренды беспилотников и помощи при ЧС в Telegram.\n"
            "Твоя задача: анализировать свежую статистику и выдавать ЧЕТКИЙ, практичный ЕЖЕДНЕВНЫЙ ПЛАН "
            "развития для фаундера (админа).\n"
            "План должен состоять из 3-4 конкретных и выполнимых пунктов (маркетинг, улучшение монетизации, работа с комьюнити)."
        )
        
        prompt = sys_prompt + "\n\n" + self._build_context_prompt(stats) + "\nСоставь ежедневный план развития на сегодня:"
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.error(f"Advisor daily plan error: {e}")
            return f"❌ Ошибка ИИ: {e}"

    async def answer_question(self, question: str, stats: dict, history: str = "") -> str:
        """Отвечает на конкретный вопрос администратора"""
        if not self.client:
            await asyncio.sleep(1)
            return f"🤖 Заглушка ответа на: {question}"

        sys_prompt = (
            "Ты — Главный Советник (Chief Advisor) Telegram-платформы по аренде БПЛА и ЧС.\n"
            "Отвечай на вопрос фаундера кратко, по делу и с максимальной практической пользой, "
            "учитывая текущую статистику."
        )
        
        ctx = self._build_context_prompt(stats)
        prompt = (
            f"{sys_prompt}\n\n{ctx}\n"
            f"История предыдущих сообщений (если есть):\n{history}\n\n"
            f"Вопрос фаундера: {question}\n\n"
            f"Твой подробный, но без 'воды' бизнес-ответ:"
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.error(f"Advisor answer error: {e}")
            return f"❌ Ошибка ИИ: {e}"

advisor_service = AdvisorService()
