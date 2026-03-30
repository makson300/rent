import os
import logging
import json
from google import genai
import io

logger = logging.getLogger(__name__)

async def analyze_photo_with_vision(bot, file_id: str) -> dict:
    """
    Скачивает фото из Telegram и проверяет его через Gemini Vision.
    Возвращает словарь: {'is_valid': bool, 'reason': str}
    """
    try:
        # 1. Скачиваем файл из телеграм
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Скачиваем в память
        downloaded = await bot.download_file(file_path)
        image_bytes = downloaded.read()
        
        # 2. Инициализируем Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY не установлен. Пропускаем ИИ модерацию.")
            return {"is_valid": True, "reason": "AI Moderation disabled"}
            
        client = genai.Client(api_key=api_key)
        
        # 3. Промпт для проверки
        prompt = '''
        Ты — строгий ИИ-модератор маркетплейса аренды БПЛА (дронов) и оборудования.
        Твоя задача — проверить фото. Допустимо: дроны, пульты, камеры, тепловизоры, кейсы с техникой, операторы за работой.
        Недопустимо: мемы, скриншоты, порнография, насилие, рандомные лица без техники, пейзажи без дронов.
        
        Верни ТОЛЬКО JSON строго по этой схеме:
        {
            "is_valid": true,
            "reason": "" 
        }
        Если фото недопустимо, is_valid: false, а в reason кратко опиши(на русском), что на фото не так.
        '''
        
        # 4. Отправляем запрос (Inline Bytes)
        # В genai bytes передаются через словарь с mime_type или напрямую list of parts
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=[
                prompt, 
                {'mime_type': 'image/jpeg', 'data': image_bytes}
            ],
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        result_text = response.text.strip()
        data = json.loads(result_text)
        return {"is_valid": data.get("is_valid", True), "reason": data.get("reason", "")}
        
    except Exception as e:
        logger.error(f"Vision moderation failed: {e}")
        # Если ИИ упал (Rate limit, no key etc), пропускаем объявление
        return {"is_valid": True, "reason": f"System Error: {e}"}

async def analyze_emergency_photo(bot, file_id: str) -> dict:
    """
    Анализ фото повреждений/ЧС для команды /assess
    Возвращает JSON с оценкой риска и сводкой.
    """
    try:
        file = await bot.get_file(file_id)
        downloaded = await bot.download_file(file.file_path)
        image_bytes = downloaded.read()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"danger_level": "unknown", "summary": "AI API Key not configured."}
            
        client = genai.Client(api_key=api_key)
        
        prompt = '''
        Ты — 'MoMoA Vision', ИИ-аналитик службы спасения и мониторинга экосистемы 'Горизонт'.
        Проанализируй фотографию с дрона или земли. Оцени степень разрушений, наличие открытого огня, задымления, статус инфраструктуры или людей, нуждающихся в помощи.
        
        Сформируй сухой, профессиональный рапорт для штаба МЧС/Службы безопасности.
        
        Верни ТОЛЬКО JSON строго по этой схеме:
        {
            "danger_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
            "summary": "Краткая сводка (2-3 предложения) о том, что видно на фото",
            "details": "Детализированный список проблем (очаги возгорания, разрушения, люди и т.д.)",
            "recommendation": "Рекомендация для спасателей/операторов дронов"
        }
        '''
        
        # Используем асинхронный вызов для исключения блокировки event loop
        response = await client.aio.models.generate_content(
            model='gemini-1.5-pro',
            contents=[prompt, {'mime_type': 'image/jpeg', 'data': image_bytes}],
            config={'response_mime_type': 'application/json'}
        )
        
        data = json.loads(response.text.strip())
        return data
        
    except Exception as e:
        logger.error(f"Emergency Vision Analysis failed: {e}")
        return {"danger_level": "ERROR", "summary": f"Ошибка ИИ анализа: {e}", "details": "-", "recommendation": "-"}
