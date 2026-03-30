import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def get_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Получает текущую погоду (ветер, порывы, осадки) с OpenMeteo.
    Возвращает dict с данными, или None при ошибке.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation&wind_speed_unit=ms&timezone=auto"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    current = data.get("current", {})
                    
                    wind_speed = current.get("wind_speed_10m", 0)
                    wind_gusts = current.get("wind_gusts_10m", 0)
                    precipitation = current.get("precipitation", 0)
                    
                    # Оценка риска для гражданских БПЛА (значения можно перенастроить)
                    risk_level = "low"
                    risk_reasons = []
                    
                    if wind_speed > 10 or wind_gusts > 15:
                        risk_level = "high"
                        risk_reasons.append("Шквальный ветер (опасно для полета)")
                    elif wind_speed > 7 or wind_gusts > 10:
                        risk_level = "medium"
                        risk_reasons.append("Сильный ветер (повышенный износ/вероятность сноса)")
                        
                    if precipitation > 2.0:
                        risk_level = "high"
                        risk_reasons.append("Сильные осадки (угроза электронике)")
                    elif precipitation > 0.0:
                        risk_level = "medium" if risk_level != "high" else "high"
                        risk_reasons.append("Осадки (возможно обледенение/намокание)")
                        
                    return {
                        "temperature": current.get("temperature_2m"),
                        "wind_speed_ms": wind_speed,
                        "wind_direction": current.get("wind_direction_10m"),
                        "wind_gusts": wind_gusts,
                        "precipitation_mm": precipitation,
                        "risk_level": risk_level,
                        "risk_reasons": risk_reasons
                    }
                else:
                    logger.error(f"Weather API error: {resp.status}")
                    return None
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        return None
