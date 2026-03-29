import uvicorn
import logging
import os
import sys
import secrets
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select, func, or_
from aiogram.types import Update

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

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RentBot Admin Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class NotAuthenticatedException(Exception):
    pass

@app.exception_handler(NotAuthenticatedException)
async def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    return RedirectResponse(url="/login", status_code=303)

active_sessions = {} # session_token -> {"role": ..., "user_id": ...}
magic_tokens = {} # single_use_token -> {"user_id": 123, "role": "..."}

async def get_current_session_data(request: Request) -> dict | None:
    token = request.cookies.get("admin_token")
    if not token:
        return None
    if ADMIN_DASHBOARD_PASSWORD and secrets.compare_digest(token, ADMIN_DASHBOARD_PASSWORD):
        return {"role": "admin", "user_id": 0} # 0 is system admin
    return active_sessions.get(token)

async def verify_admin(request: Request):
    """Cookie-based auth guard for admin and moderators."""
    data = await get_current_session_data(request)
    if not data:
        raise NotAuthenticatedException()
    request.state.role = data.get("role")
    request.state.user_id = data.get("user_id")

async def verify_superadmin(request: Request):
    """Guard only for full admins."""
    data = await get_current_session_data(request)
    if not data or data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Только Администратор!")
    request.state.role = data.get("role")
    request.state.user_id = data.get("user_id")

@app.get("/auth/magic")
async def magic_auth(request: Request, token: str):
    if token not in magic_tokens:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Ссылка устарела или недействительна."})
    
    data = magic_tokens.pop(token)
    session_token = secrets.token_hex(32)
    active_sessions[session_token] = data
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="admin_token", value=session_token, httponly=True, max_age=86400*30)
    return response

@app.get("/login")
async def login_get(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
async def login_post(request: Request, password: str = Form(...)):
    if not ADMIN_DASHBOARD_PASSWORD or secrets.compare_digest(password, ADMIN_DASHBOARD_PASSWORD):
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="admin_token", value=password, httponly=True, max_age=86400*30)
        return response
    return templates.TemplateResponse(request=request, name="login.html", context={"error": "Неверный пароль"})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("admin_token")
    return response

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
            from db.models.job import Job
            new_jobs = await session.scalar(
                select(func.count()).select_from(Job).where(Job.status == "pending")
            )
            
        return templates.TemplateResponse(
            request=request, name="index.html", context={
                "role": getattr(request.state, "role", "admin"),
                "stats": {
                    "users_count": users_count or 0, 
                    "active_listings": listings_count or 0,
                    "new_applications": new_apps or 0,
                    "new_feedback": new_feedback or 0,
                    "total_emergencies": total_emergencies or 0,
                    "new_jobs": new_jobs or 0
                }
            }
        )

    except Exception as e:
        logger.error(f"Error rendering home: {e}", exc_info=True)
        raise e

@app.get("/listings", dependencies=[Depends(verify_admin)])
async def listings_page(request: Request, page: int = 1, query: str = ""):
    """Страница со всеми объявлениями"""
    try:
        limit = 50
        offset = (page - 1) * limit
        async with async_session() as session:
            from sqlalchemy.orm import selectinload
            stmt = select(Listing).options(selectinload(Listing.photos)).order_by(Listing.created_at.desc())
            
            if query:
                stmt = stmt.where(or_(
                    Listing.title.ilike(f"%{query}%"),
                    Listing.description.ilike(f"%{query}%")
                ))
            
            # Count total
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt)
            
            # Fetch page
            result = await session.execute(stmt.offset(offset).limit(limit))
            listings = result.scalars().all()
            
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            
        return templates.TemplateResponse(
            request=request, name="listings.html", context={
                "role": getattr(request.state, "role", "admin"),
                "listings": listings,
                "page": page,
                "total_pages": total_pages,
                "query": query,
                "total": total
            }
        )
    except Exception as e:
        logger.error(f"Error rendering listings: {e}", exc_info=True)
        raise e

@app.post("/listings/{listing_id}/approve", dependencies=[Depends(verify_admin)])
async def approve_listing_web(request: Request, listing_id: int):
    """Одобрение объявления через веб"""
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(Listing).where(Listing.id == listing_id).values(status="active")
            )
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "approve_listing", "listing", listing_id)
            await session.commit()
            
        return RedirectResponse(url="/listings", status_code=303)
    except Exception as e:
        logger.error(f"Error approving listing {listing_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/listings/{listing_id}/reject", dependencies=[Depends(verify_admin)])
async def reject_listing_web(request: Request, listing_id: int):
    """Отклонение объявления через веб"""
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(Listing).where(Listing.id == listing_id).values(status="rejected")
            )
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "reject_listing", "listing", listing_id)
            await session.commit()
            
        return RedirectResponse(url="/listings", status_code=303)
    except Exception as e:
        logger.error(f"Error rejecting listing {listing_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/feedback", dependencies=[Depends(verify_admin)])
async def feedback_page(request: Request, page: int = 1):
    """Страница с обратной связью"""
    try:
        limit = 50
        offset = (page - 1) * limit
        async with async_session() as session:
            from db.models.feedback import Feedback
            from sqlalchemy.orm import selectinload
            stmt = select(Feedback).options(selectinload(Feedback.user)).order_by(Feedback.created_at.desc())
            
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt)
            
            result = await session.execute(stmt.offset(offset).limit(limit))
            feedbacks = result.scalars().all()
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            
        return templates.TemplateResponse(
            request=request, name="feedback.html", context={
                "role": getattr(request.state, "role", "admin"),
                "feedbacks": feedbacks,
                "page": page,
                "total_pages": total_pages,
                "total": total
            }
        )
    except Exception as e:
        logger.error(f"Error rendering feedback: {e}", exc_info=True)
        raise e

@app.post("/feedback/{feedback_id}/process", dependencies=[Depends(verify_admin)])
async def process_feedback_web(request: Request, feedback_id: int):
    """Отметка обратной связи как обработанной"""
    try:
        async with async_session() as session:
            from db.models.feedback import Feedback
            from sqlalchemy import update
            await session.execute(
                update(Feedback).where(Feedback.id == feedback_id).values(status="processed")
            )
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "process_feedback", "feedback", feedback_id)
            
            await session.commit()
        return RedirectResponse(url="/feedback", status_code=303)
    except Exception as e:
        logger.error(f"Error processing feedback {feedback_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/applications", dependencies=[Depends(verify_admin)])
async def applications(request: Request, page: int = 1):
    try:
        limit = 50
        offset = (page - 1) * limit
        async with async_session() as session:
            stmt = select(EducationApplication).order_by(EducationApplication.created_at.desc())
            
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt)
            
            result = await session.execute(stmt.offset(offset).limit(limit))
            apps = result.scalars().all()
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            
        return templates.TemplateResponse(
            request=request, name="applications.html", context={
                "role": getattr(request.state, "role", "admin"),
                "applications": apps,
                "page": page,
                "total_pages": total_pages,
                "total": total
            }
        )
    except Exception as e:
        logger.error(f"Error rendering applications: {e}", exc_info=True)
        raise e

@app.get("/emergencies", dependencies=[Depends(verify_admin)])
async def emergencies_page(request: Request, page: int = 1):
    """Страница Центра ЧС"""
    try:
        limit = 50
        offset = (page - 1) * limit
        async with async_session() as session:
            from sqlalchemy.orm import selectinload
            stmt = select(EmergencyAlert).options(selectinload(EmergencyAlert.reporter)).order_by(EmergencyAlert.created_at.desc())
            
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt)
            
            result = await session.execute(stmt.offset(offset).limit(limit))
            emergencies = result.scalars().all()
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            
        return templates.TemplateResponse(
            request=request, name="emergencies.html", context={
                "role": getattr(request.state, "role", "admin"),
                "emergencies": emergencies,
                "page": page,
                "total_pages": total_pages,
                "total": total
            }
        )
    except Exception as e:
        logger.error(f"Error rendering emergencies: {e}", exc_info=True)
        raise e
        
@app.get("/users", dependencies=[Depends(verify_superadmin)])
async def users_page(request: Request, page: int = 1, query: str = ""):
    """Страница пользователей"""
    try:
        limit = 50
        offset = (page - 1) * limit
        async with async_session() as session:
            stmt = select(User).order_by(User.created_at.desc())
            if query:
                stmt = stmt.where(or_(
                    User.first_name.ilike(f"%{query}%"),
                    User.username.ilike(f"%{query}%"),
                    User.phone_number.ilike(f"%{query}%")
                ))
                
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt)
            
            result = await session.execute(stmt.offset(offset).limit(limit))
            users = result.scalars().all()
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            
        return templates.TemplateResponse(
            request=request, name="users.html", context={
                "role": getattr(request.state, "role", "admin"),
                "users": users,
                "page": page,
                "total_pages": total_pages,
                "total": total,
                "query": query
            }
        )
    except Exception as e:
        logger.error(f"Error rendering users: {e}", exc_info=True)
        raise e

@app.post("/users/{user_id}/ban", dependencies=[Depends(verify_superadmin)])
async def ban_user_web(user_id: int):
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(update(User).where(User.id == user_id).values(is_banned=True))
            await session.commit()
        return RedirectResponse(url="/users", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/users/{user_id}/unban", dependencies=[Depends(verify_superadmin)])
async def unban_user_web(user_id: int):
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(update(User).where(User.id == user_id).values(is_banned=False))
            await session.commit()
        return RedirectResponse(url="/users", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/emergencies/{alert_id}/approve", dependencies=[Depends(verify_admin)])
async def approve_emergency_web(request: Request, alert_id: int):
    """Одобрение ЧС (интерфейс)"""
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(EmergencyAlert).where(EmergencyAlert.id == alert_id).values(status="approved")
            )
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "approve_emergency", "emergency", alert_id)
            await session.commit()
        return RedirectResponse(url="/emergencies", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/emergencies/{alert_id}/reject", dependencies=[Depends(verify_admin)])
async def reject_emergency_web(request: Request, alert_id: int):
    """Отклонение ЧС"""
    try:
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(EmergencyAlert).where(EmergencyAlert.id == alert_id).values(status="rejected")
            )
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "reject_emergency", "emergency", alert_id)
            await session.commit()
        return RedirectResponse(url="/emergencies", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/logs", dependencies=[Depends(verify_superadmin)])
async def logs_page(request: Request, page: int = 1):
    """Журнал модерации"""
    try:
        limit = 50
        offset = (page - 1) * limit
        async with async_session() as session:
            from db.models.log import ModerationLog
            from sqlalchemy.orm import selectinload
            stmt = select(ModerationLog).options(selectinload(ModerationLog.admin)).order_by(ModerationLog.created_at.desc())
            
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt)
            
            result = await session.execute(stmt.offset(offset).limit(limit))
            logs = result.scalars().all()
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            
        return templates.TemplateResponse(
            request=request, name="logs.html", context={
                "role": getattr(request.state, "role", "admin"),
                "logs": logs,
                "page": page,
                "total_pages": total_pages,
                "total": total
            }
        )
    except Exception as e:
        logger.error(f"Error rendering logs: {e}", exc_info=True)
        raise e

@app.get("/jobs", dependencies=[Depends(verify_admin)])
async def jobs_page(request: Request, page: int = 1):
    """Страница модерации вакансий и заказов"""
    try:
        limit = 50
        offset = (page - 1) * limit
        async with async_session() as session:
            from db.models.job import Job
            from sqlalchemy.orm import selectinload
            stmt = select(Job).options(selectinload(Job.employer)).order_by(Job.created_at.desc())
            
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt)
            
            result = await session.execute(stmt.offset(offset).limit(limit))
            jobs = result.scalars().all()
            total_pages = (total + limit - 1) // limit if total > 0 else 1
            
        return templates.TemplateResponse(
            request=request, name="jobs_admin.html", context={
                "role": getattr(request.state, "role", "admin"),
                "jobs": jobs,
                "page": page,
                "total_pages": total_pages,
                "total": total
            }
        )
    except Exception as e:
        logger.error(f"Error rendering jobs: {e}", exc_info=True)
        raise e

@app.post("/jobs/{job_id}/approve", dependencies=[Depends(verify_admin)])
async def approve_job_web(request: Request, job_id: int):
    """Одобрение работы через веб"""
    try:
        async with async_session() as session:
            from db.models.job import Job
            from sqlalchemy import update
            await session.execute(
                update(Job).where(Job.id == job_id).values(status="active")
            )
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "approve_job", "job", job_id)
            await session.commit()
            
        return RedirectResponse(url="/jobs", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/jobs/{job_id}/reject", dependencies=[Depends(verify_admin)])
async def reject_job_web(request: Request, job_id: int):
    """Отклонение работы через веб"""
    try:
        async with async_session() as session:
            from db.models.job import Job
            from sqlalchemy import update
            await session.execute(
                update(Job).where(Job.id == job_id).values(status="rejected")
            )
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "reject_job", "job", job_id)
            await session.commit()
            
        return RedirectResponse(url="/jobs", status_code=303)
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
            from db.models.job import Job
            
            # Get listings
            result = await session.execute(
                select(Listing).where(Listing.status == "active").options(selectinload(Listing.photos)).order_by(Listing.created_at.desc())
            )
            listings = result.scalars().all()
            
            # Get active jobs
            result_jobs = await session.execute(
                select(Job).where(Job.status == "active").order_by(Job.created_at.desc())
            )
            jobs = result_jobs.scalars().all()
            
        return templates.TemplateResponse(
            request=request, name="webapp_catalog.html", context={
                "listings": listings,
                "jobs": jobs
            }
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

@app.get("/api/v1/public/listings")
async def public_listings_api(
    category_id: int | None = None,
    city: str | None = None,
    q: str | None = None
):
    """Публичный API для получения активных объявлений (Next.js)"""
    async with async_session() as session:
        from sqlalchemy.orm import selectinload
        stmt = select(Listing).where(Listing.status == 'active').options(selectinload(Listing.photos), selectinload(Listing.user)).order_by(Listing.created_at.desc())
        
        if category_id:
            stmt = stmt.where(Listing.category_id == category_id)
        if city:
            stmt = stmt.where(Listing.city.ilike(f"%{city}%"))
        if q:
            from sqlalchemy import or_
            stmt = stmt.where(or_(Listing.title.ilike(f"%{q}%"), Listing.description.ilike(f"%{q}%")))
            
        result = await session.execute(stmt)
        listings = result.scalars().all()
        
        data = []
        for lst in listings:
            data.append({
                "id": lst.id,
                "title": lst.title,
                "description": lst.description,
                "city": lst.city,
                "address": lst.address,
                "price": lst.price_list,
                "category_id": lst.category_id,
                "is_sponsored": getattr(lst, "is_sponsored", False),
                "seller_name": lst.user.first_name,
                "photos": [p.file_id for p in lst.photos]
            })
            
    return JSONResponse(content={"ok": True, "listings": data})

@app.get("/api/v1/public/listings/{listing_id}")
async def public_listing_detail_api(listing_id: int):
    """Публичный API для получения одного объявления (Next.js)"""
    async with async_session() as session:
        from sqlalchemy.orm import selectinload
        result = await session.execute(
            select(Listing).where(Listing.id == listing_id, Listing.status == 'active')
            .options(selectinload(Listing.photos), selectinload(Listing.user))
        )
        lst = result.scalar_one_or_none()
        
        if not lst:
            return JSONResponse(status_code=404, content={"ok": False, "error": "Not Found"})
            
        data = {
            "id": lst.id,
            "title": lst.title,
            "description": lst.description,
            "city": lst.city,
            "address": lst.address,
            "price": lst.price_list,
            "category_id": lst.category_id,
            "is_sponsored": getattr(lst, "is_sponsored", False),
            "seller_name": lst.user.first_name,
            "seller_id": lst.user.id,
            "photos": [p.file_id for p in lst.photos],
            "created_at": lst.created_at.isoformat()
        }
            
    return JSONResponse(content={"ok": True, "listing": data})

@app.get("/api/v1/public/jobs")
async def public_jobs_api(
    city: str | None = None,
    q: str | None = None
):
    """Публичный API для получения активных заказов (Next.js)"""
    async with async_session() as session:
        from db.models.job import Job
        from sqlalchemy.orm import selectinload
        stmt = select(Job).where(Job.status == 'active').options(selectinload(Job.employer)).order_by(Job.created_at.desc())
        
        if city:
            stmt = stmt.where(Job.city.ilike(f"%{city}%"))
        if q:
            from sqlalchemy import or_
            stmt = stmt.where(or_(Job.title.ilike(f"%{q}%"), Job.description.ilike(f"%{q}%")))
            
        result = await session.execute(stmt)
        jobs = result.scalars().all()
        
        data = []
        for j in jobs:
            data.append({
                "id": j.id,
                "title": j.title,
                "description": j.description,
                "city": j.city,
                "budget": j.budget,
                "category": j.category,
                "employer_name": j.employer.first_name,
                "created_at": j.created_at.isoformat()
            })
            
    return JSONResponse(content={"ok": True, "jobs": data})


if __name__ == "__main__":
    # Use the filename "dashboard" for uvicorn string reference
    uvicorn.run("dashboard:app", host="0.0.0.0", port=8000, reload=True)
