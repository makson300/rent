import logging
import asyncio
import google.generativeai as genai
from bot.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

async def ask_support_agent(user_text: str) -> str:
    if not GEMINI_API_KEY:
        return ""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        prompt = f"""
Ты — бот-саппорт (MoMoA Support Agent) маркетплейса аренды и продажи дронов/БПЛА.
Твоя задача — вежливо, профессионально и коротко ответить на вопрос пользователя. 
Если вопрос о правилах размещения, монетизации (оплата Stars или ЮKassa), удалении объявлений или поиске — отвечай уверенно.
Если вопрос касается возврата средств, бана, жалобы на мошенника или технических сбоев, напиши инструкцию и предложи нажать кнопку вызова человека.

Ни в коем случае не придумывай то, чего нет. Не выдумывай несуществующие функции. Будь лаконичен.

Текст запроса юзера: {user_text}
Отвечай ТОЛЬКО готовым текстом для отправки пользователю, без приветствий типа "Привет, я бот".
"""
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        logger.error(f"Support Agent error: {e}")
        return ""
