import asyncio
import logging
import json
from datetime import datetime
from bot.config import GEMINI_API_KEY

try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

logger = logging.getLogger(__name__)

class EmergencyMonitor:
    """
    Система автоматического мониторинга ЧП.
    Использует принципы Agentic Research (на базе MoMoA-Researcher)
    для поиска ситуаций, где требуются операторы БПЛА.
    """

    def __init__(self, check_interval_hours: int = 6):
        self.check_interval = check_interval_hours * 3600
        self.is_running = False
        
        if has_genai and GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
            self.model_name = 'gemini-1.5-pro'
        else:
            self.client = None
            logger.warning("google-genai не установлен или GEMINI_API_KEY пуст. Используются заглушки!")

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        logger.info("Emergency Monitor started")

        while self.is_running:
            await self.run_research()
            await asyncio.sleep(self.check_interval)

    async def run_research(self):
        """
        Процесс исследования (MoMoA Framework):
        1. Системный оркестратор собирает данные.
        2. Комнаты экспертов (Аналитик + Скептик) обсуждают новость.
        3. Оркестратор принимает финальное решение и создает алерт.
        """
        logger.info(f"Research cycle started at {datetime.now()}")
        
        # 1. Orchestrator: Сбор данных
        raw_news = await self._orchestrator_gather_news()
        if not raw_news:
            logger.info("Research cycle completed: No new data.")
            return
            
        # 2. MoMoA Work Phase Rooms
        for news_item in raw_news:
            logger.info(f"[Orchestrator] Assigned research task for: {news_item['title']}")
            
            # Phase 1: Analyst Expert
            analysis = await self._expert_analyst(news_item)
            
            # Phase 2: Skeptic Expert (Debate & review)
            validation = await self._expert_skeptic(news_item, analysis)
            
            # Phase 3: Orchestrator executes outcome
            if validation and validation.get("is_valid_emergency"):
                await self._trigger_alert(news_item, validation)
                
        logger.info("Research cycle completed")

    async def _orchestrator_gather_news(self):
        """Оркестратор: Сбор информации (Заглушка для RSS/Telegram)"""
        # В будущем здесь будет реальный вызов парсеров
        return [
            {
                "id": "test-news-1",
                "title": "Пожар в лесном массиве", 
                "content": "Сильное задымление в 15 км от города, требуется оценка площади возгорания.", 
                "source": "MCHS_RSS"
            }
        ]

    async def _expert_analyst(self, news_item):
        """Эксперт 1 (Аналитик): Оценивает необходимость дронов (Вызов Gemini)"""
        logger.debug(f"[Эксперт Аналитик] Анализирую: {news_item['title']}")
        
        if not self.client:
            await asyncio.sleep(1)
            return {
                "needs_drone": True,
                "hypothesis": "Заглушка: Пожар на большой территории. Дрон нужен для разведки очагов возгорания (термовизор).",
                "urgency": "high"
            }
            
        prompt = (
            f"Ты строгий ГИС-аналитик МЧС.\n"
            f"Проанализируй новость и скажи, нужен ли гражданский БПЛА (дрон) для помощи.\n"
            f"Новость: {news_item['title']}. {news_item['content']}\n"
            f"Верни СТРОГИЙ JSON без маркдауна: {{\n"
            f'  "needs_drone": true/false,\n'
            f'  "hypothesis": "коротко почему нужен или не нужен",\n'
            f'  "urgency": "high"/"medium"/"low"\n'
            f"}}"
        )
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Analyst error: {e}")
            return {"needs_drone": False, "hypothesis": f"Ошибка AI: {e}", "urgency": "low"}


    async def _expert_skeptic(self, news_item, analysis_result):
        """Эксперт 2 (Скептик): Критикует вывод Аналитика во избежание ложных вызовов"""
        logger.debug(f"[Эксперт Скептик] Проверяю гипотезу: {analysis_result.get('hypothesis')}")
        
        if not analysis_result.get("needs_drone"):
            return {"is_valid_emergency": False, "final_consensus": "Аналитик решил, что дрон не нужен.", "recommended_action": "none"}
            
        if not self.client:
            await asyncio.sleep(1)
            return {
                "is_valid_emergency": True,
                "final_consensus": "Заглушка: Аналитик прав. Задымление требует БПЛА, наземной технике трудно оценить масштабы.",
                "recommended_action": "alert_operators"
            }
            
        prompt = (
            f"Ты критический ревьюер (Скептик).\n"
            f"Аналитик МЧС решил, что требуется БПЛА по новости: '{news_item['title']} - {news_item['content']}'.\n"
            f"Его гипотеза: {analysis_result.get('hypothesis')}\n"
            f"Оцени, нет ли логической ошибки (возможно, это учения, нет реальной угрозы и т.д.).\n"
            f"Верни СТРОГИЙ JSON без маркдауна: {{\n"
            f'  "is_valid_emergency": true/false,\n'
            f'  "final_consensus": "твое финальное решение как старшего офицера",\n'
            f'  "recommended_action": "alert_operators"/"ignore"\n'
            f"}}"
        )
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Skeptic error: {e}")
            return {"is_valid_emergency": False, "final_consensus": f"Ошибка AI: {e}", "recommended_action": "error"}

    async def act_as_analyst(self, raw_text: str):
        """Публичный метод Аналитика для обработки заявки от юзера"""
        logger.debug(f"[User Analyst] Анализирую текст: {raw_text}")
        if not self.client:
            await asyncio.sleep(1)
            return {
                "location": "Тестовый Город",
                "incident_type": "Тестовое ЧП",
                "required_drone_type": "Тепловизор",
                "urgency": "medium",
                "needs_drone": True,
                "hypothesis": "Заглушка"
            }
            
        prompt = (
            f"Пользователь сообщает об экстренной ситуации:\n'{raw_text}'\n"
            f"Извлеки из текста (или сделай вывод) следующие данные.\n"
            f"Верни СТРОГИЙ JSON без маркдауна: {{\n"
            f'  "location": "город или локация",\n'
            f'  "incident_type": "тип происшествия (поиск человека, пожар и т.д.)",\n'
            f'  "required_drone_type": "какой дрон лучше подойдет (тепловизор, fpv и тд)",\n'
            f'  "urgency": "high"/"medium"/"low",\n'
            f'  "needs_drone": true/false,\n'
            f'  "hypothesis": "почему дрон здесь поможет"\n'
            f"}}"
        )
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Act Analyst error: {e}")
            return {"needs_drone": False, "hypothesis": f"Error: {e}"}
            
    async def act_as_skeptic(self, raw_text: str, analysis: str):
        """Публичный метод Скептика для проверки заявки юзера"""
        logger.debug("[User Skeptic] Проверяю на спам...")
        if not self.client:
            await asyncio.sleep(1)
            return True # In development mode without API, trust incoming reports
            
        prompt = (
            f"Пользователь отправил заявку на помощь дронов: '{raw_text}'\n"
            f"Аналитик разобрал её так: {analysis}\n"
            f"Твоя задача — оценить текст пользователя. Похоже ли это на спам, шутку, пранк? "
            f"Это реально экстренная ситуация, где нужен БПЛА?\n"
            f"Верни СТРОГИЙ JSON без маркдауна: {{\n"
            f'  "is_authentic_emergency": true/false,\n'
            f'  "reason": "короткое обоснование"\n'
            f"}}"
        )
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            res = json.loads(response.text)
            return res.get("is_authentic_emergency", False)
        except Exception as e:
            logger.error(f"Act Skeptic error: {e}")
            return False

    async def _trigger_alert(self, news_item, consensus):
        """Оркестратор: Отправка алерта по достижению консенсуса"""
        if consensus.get("recommended_action") != "alert_operators":
            return
            
        logger.warning(
            f"\n🚨 [MoMoA EMERGENCY ALERT] 🚨\n"
            f"Тема: {news_item['title']}\n"
            f"Обоснование ИИ: {consensus['final_consensus']}\n"
            f"Рекомендуемое действие: Рассылка операторам БПЛА."
        )
        # TODO: Интеграция с aiogram для рассылки операторам из БД

    def stop(self):
        self.is_running = False
        logger.info("Emergency Monitor stopped")

# Синглтон сервиса
monitor_service = EmergencyMonitor()
