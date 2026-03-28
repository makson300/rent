import uvicorn
import logging
import os
import sys
import secrets
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select, func

# Add project root to path to import db and bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.base import async_session, init_db
from db.models.user import User
from db.models.listing import Listing
from db.models.education import EducationApplication
from db.models.emergency import EmergencyAlert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RentBot Admin Dashboard")

# Setup templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Web Dashboard...")
    try:
        await init_db()
        logger.info("Database initialized for web dashboard.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log full details server-side, but never expose internals to the client
    logger.error(f"Global error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )

# --- Admin Auth Middleware ---
from bot.config import ADMIN_DASHBOARD_PASSWORD, WEBHOOK_SECRET

security = HTTPBasic(auto_error=False)

async def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Basic auth guard for admin routes. Skipped if ADMIN_DASHBOARD_PASSWORD is empty (dev mode)."""
    if not ADMIN_DASHBOARD_PASSWORD:
        return  # No password set — dev mode, allow all
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not secrets.compare_digest(credentials.password, ADMIN_DASHBOARD_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/health")
async def health_check():
    """Health check for Docker and monitoring — no auth required."""
    db_ok = False
    try:
        async with async_session() as session:
            await session.execute(select(func.count()).select_from(User))
            db_ok = True
    except Exception:
        pass
    return {"status": "ok" if db_ok else "degraded", "db": db_ok}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Прием обновлений от Telegram (Webhook) с валидацией секретного токена"""
    # Validate the secret token if configured — prevents spoofed webhook calls
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not secrets.compare_digest(token, WEBHOOK_SECRET):
            logger.warning(f"Webhook rejected: invalid secret token from {request.client.host}")
            return JSONResponse(status_code=403, content={"ok": False})
    try:
        from aiogram.types import Update
        bot = request.app.state.bot
        dp = request.app.state.dp
        
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse(status_code=500, content={"ok": False})

@app.get("/", dependencies=[Depends(verify_admin)])
async def home(request: Request):
    try:
        async with async_session() as session:
            users_count = await session.scalar(select(func.count()).select_from(User))
            listings_count = await session.scalar(
                select(func.count()).select_from(Listing).where(Listing.status == "active")
            )
            new_apps = await session.scalar(
                select(func.count()).select_from(EducationApplication).where(EducationApplication.status == "new")
            )
            from db.models.feedback import Feedback
            new_feedback = await session.scalar(
                select(func.count()).select_from(Feedback).where(Feedback.status == "new")
            )
            total_emergencies = await session.scalar(
                select(func.count()).select_from(EmergencyAlert)
            )
            
        return templates.TemplateResponse(
            request=request, name="index.html", context={
                "stats": {
                    "users_count": users_count or 0, 
                    "active_listings": listings_count or 0,
                    "new_applications": new_apps or 0,
                    "new_feedback": new_feedback or 0,
                    "total_emergencies": total_emergencies or 0
                }
            }
        )

    except Exception as e:
        logger.error(f"Error rendering home: {e}", exc_info=True)
        raise e

@app.get("/listings", dependencies=[Depends(verify_admin)])
async def listings_page(request: Request):
    """Страница со всеми объявлениями"""
    try:
        async with async_session() as session:
            # Префетчим фотографии
            from sqlalchemy.orm import selectinload
            result = await session.execute(
                select(Listing).options(selectinload(Listing.photos)).order_by(Listing.created_at.desc())
            )
            listings = result.scalars().all()
            
        return templates.TemplateResponse(
            request=request, name="listings.html", context={"listings": listings}
        )
    except Exception as e:
        logger.error(f"Error rendering listings: {e}", exc_info=True)
        raise e

@app.post("/listings/{listing_id}/approve", dependencies=[Depends(verify_admin)])
async def approve_listing_web(listing_id: int):
    """Одобрение объявления через веб"""
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(Listing).where(Listing.id == listing_id).values(status="active")
            )
            await session.commit()
        return RedirectResponse(url="/listings", status_code=303)
    except Exception as e:
        logger.error(f"Error approving listing {listing_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/listings/{listing_id}/reject", dependencies=[Depends(verify_admin)])
async def reject_listing_web(listing_id: int):
    """Отклонение объявления через веб"""
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(Listing).where(Listing.id == listing_id).values(status="rejected")
            )
            await session.commit()
        return RedirectResponse(url="/listings", status_code=303)
    except Exception as e:
        logger.error(f"Error rejecting listing {listing_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/feedback", dependencies=[Depends(verify_admin)])
async def feedback_page(request: Request):
    """Страница с обратной связью"""
    try:
        async with async_session() as session:
            from db.models.feedback import Feedback
            from sqlalchemy.orm import selectinload
            result = await session.execute(
                select(Feedback).options(selectinload(Feedback.user)).order_by(Feedback.created_at.desc())
            )
            feedbacks = result.scalars().all()
            
        return templates.TemplateResponse(
            request=request, name="feedback.html", context={"feedbacks": feedbacks}
        )
    except Exception as e:
        logger.error(f"Error rendering feedback: {e}", exc_info=True)
        raise e

@app.post("/feedback/{feedback_id}/process", dependencies=[Depends(verify_admin)])
async def process_feedback_web(feedback_id: int):
    """Отметка обратной связи как обработанной"""
    try:
        async with async_session() as session:
            from db.models.feedback import Feedback
            from sqlalchemy import update
            await session.execute(
                update(Feedback).where(Feedback.id == feedback_id).values(status="processed")
            )
            await session.commit()
        return RedirectResponse(url="/feedback", status_code=303)
    except Exception as e:
        logger.error(f"Error processing feedback {feedback_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/applications", dependencies=[Depends(verify_admin)])
async def applications(request: Request):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(EducationApplication).order_by(EducationApplication.created_at.desc())
            )
            apps = result.scalars().all()
            
        return templates.TemplateResponse(
            request=request, name="applications.html", context={"applications": apps}
        )
    except Exception as e:
        logger.error(f"Error rendering applications: {e}", exc_info=True)
        raise e

@app.get("/emergencies", dependencies=[Depends(verify_admin)])
async def emergencies_page(request: Request):
    """Страница Центра ЧС"""
    try:
        async with async_session() as session:
            from sqlalchemy.orm import selectinload
            # Загружаем с данными репортера
            result = await session.execute(
                select(EmergencyAlert).options(selectinload(EmergencyAlert.reporter)).order_by(EmergencyAlert.created_at.desc())
            )
            emergencies = result.scalars().all()
            
        return templates.TemplateResponse(
            request=request, name="emergencies.html", context={"emergencies": emergencies}
        )
    except Exception as e:
        logger.error(f"Error rendering emergencies: {e}", exc_info=True)
        raise e

@app.post("/emergencies/{alert_id}/approve", dependencies=[Depends(verify_admin)])
async def approve_emergency_web(alert_id: int):
    """Одобрение ЧС (интерфейс)"""
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(EmergencyAlert).where(EmergencyAlert.id == alert_id).values(status="approved")
            )
            await session.commit()
            # В идеале здесь должен быть вызов функции массовой рассылки операторам
            # но пока ограничимся сменой статуса в БД через ВЕБ интерфейс.
        return RedirectResponse(url="/emergencies", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/emergencies/{alert_id}/reject", dependencies=[Depends(verify_admin)])
async def reject_emergency_web(alert_id: int):
    """Отклонение ЧС"""
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(EmergencyAlert).where(EmergencyAlert.id == alert_id).values(status="rejected")
            )
            await session.commit()
        return RedirectResponse(url="/emergencies", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

import random

CITY_COORDS = {
    "Москва": [55.7558, 37.6173],
    "Санкт-Петербург": [59.9343, 30.3351],
    "Казань": [55.7963, 49.1088],
    "Новосибирск": [55.0302, 82.9204],
    "Екатеринбург": [56.8389, 60.6057],
    "Нижний Новгород": [56.3269, 44.0059],
    "Краснодар": [45.0355, 38.9753],
    "Сочи": [43.5855, 39.7231],
    "Ростов-на-Дону": [47.2220, 39.7196],
}

@app.get("/map")
async def map_page(request: Request):
    """Страница TMA-Карты"""
    return templates.TemplateResponse(request=request, name="map.html", context={})

@app.get("/webapp/catalog")
async def webapp_catalog(request: Request):
    """Страница TMA-Каталога для Telegram Mini App"""
    try:
        async with async_session() as session:
            from sqlalchemy.orm import selectinload
            result = await session.execute(
                select(Listing).where(Listing.status == "active").options(selectinload(Listing.photos)).order_by(Listing.created_at.desc())
            )
            listings = result.scalars().all()
            
        return templates.TemplateResponse(
            request=request, name="webapp_catalog.html", context={"listings": listings}
        )
    except Exception as e:
        logger.error(f"Error rendering webapp catalog: {e}", exc_info=True)
        raise e

@app.get("/api/map_data")
async def map_data_api():
    """Возвращает точки для карты"""
    async with async_session() as session:
        # Load active listings
        from sqlalchemy.orm import selectinload
        result = await session.execute(
            select(Listing).where(Listing.status == 'active').options(selectinload(Listing.user))
        )
        listings = result.scalars().all()
        
        # Load active emergencies
        em_res = await session.execute(
            select(EmergencyAlert).where(EmergencyAlert.status == 'approved')
        )
        emergencies = em_res.scalars().all()
        
    points = []
    
    for lst in listings:
        base_coords = CITY_COORDS.get(lst.city, CITY_COORDS["Москва"])
        # Add a tiny random offset to avoid overlapping identical pins
        lat = base_coords[0] + (random.random() - 0.5) * 0.05
        lon = base_coords[1] + (random.random() - 0.5) * 0.05
        
        cat_map = {1: "rental", 2: "sale", 6: "operator"}
        m_type = cat_map.get(lst.category_id, "other")
        
        points.append({
            "type": "listing",
            "id": lst.id,
            "lat": lat,
            "lon": lon,
            "title": lst.title,
            "price": lst.price_list[:50] + ("..." if len(lst.price_list)>50 else ""),
            "owner": lst.user.first_name,
            "marker_type": m_type,
            "is_sponsored": getattr(lst, "is_sponsored", False)
        })
        
    for em in emergencies:
        base_coords = CITY_COORDS.get(em.city, CITY_COORDS["Москва"])
        lat = base_coords[0] + (random.random() - 0.5) * 0.02
        lon = base_coords[1] + (random.random() - 0.5) * 0.02
        points.append({
            "type": "emergency",
            "id": em.id,
            "lat": lat,
            "lon": lon,
            "title": "🚨 ЭКСТРЕННЫЙ СБОР",
            "price": em.problem_type,
            "owner": "АДМИНИСТРАЦИЯ",
            "marker_type": "emergency"
        })

    return JSONResponse(content={"points": points})


if __name__ == "__main__":
    # Use the filename "dashboard" for uvicorn string reference
    uvicorn.run("dashboard:app", host="0.0.0.0", port=8000, reload=True)
