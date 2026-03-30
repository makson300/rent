import uvicorn
import logging
import os
import sys
import secrets
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from aiogram.types import Update

# Add project root to path to import db and bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.base import async_session, init_db
from db.models.user import User
from db.models.listing import Listing
from db.models.education import EducationApplication
from db.models.emergency import EmergencyAlert
from db.models.flight_plan import FlightPlan
from db.models.job import Job

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

async def get_session():
    async with async_session() as session:
        yield session

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
    """Guard only for full admins. Redirects to /login if unauthenticated."""
    data = await get_current_session_data(request)
    if not data:
        raise NotAuthenticatedException()
    if data.get("role") != "admin":
        # Authenticated as moderator but not superadmin — redirect to dashboard root
        raise NotAuthenticatedException()
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
            from sqlalchemy.orm import selectinload
            alert = await session.get(EmergencyAlert, alert_id, options=[selectinload(EmergencyAlert.reporter)])
            if not alert:
                return JSONResponse(status_code=404, content={"error": "Not found"})
                
            alert.status = "approved"
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "approve_emergency", "emergency", alert_id)
            await session.commit()
            
            # --- Push Notifications to Operators ---
            from db.models.category import Category
            stmt = (
                select(User)
                .join(Listing, Listing.user_id == User.id)
                .join(Category, Listing.category_id == Category.id)
                .where(Category.name == "Операторы")
            )
            if alert.city and alert.city != "Неизвестно":
                stmt = stmt.where(Listing.city.ilike(f"%{alert.city}%"))
                
            result = await session.execute(stmt)
            operators = result.scalars().unique().all()
            
            bot = getattr(request.app.state, 'bot', None)
            if bot:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                from bot.services.emergency_monitor import monitor_service
                
                keywords = await monitor_service.get_emergency_keywords(alert.raw_text)
                
                dispatch_kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🙋‍♂️ Я готов помочь (Связь)", callback_data=f"alert_respond_{alert_id}")]
                ])
                for op in operators:
                    # Считываем оборудование
                    op_result = await session.execute(select(Listing).where(Listing.user_id == op.id))
                    op_listings = op_result.scalars().all()
                    all_equipment = " ".join([l.title + " " + (l.description or "") for l in op_listings]).lower()
                    
                    is_priority = False
                    if keywords:
                        for k in keywords:
                            if k.lower() in all_equipment:
                                is_priority = True
                                break
                    
                    if is_priority:
                        dispatch_text = (
                            f"🔴 <b>КРИТИЧЕСКИЙ ПРИОРИТЕТ: ВАШЕ ОБОРУДОВАНИЕ ИДЕАЛЬНО ПОДХОДИТ!</b> 🔴\n\n"
                            f"<b>Локация:</b> {alert.city}\n"
                            f"<b>Ситуация:</b> {alert.problem_type}\n"
                            f"<b>Нужен:</b> {alert.required_equipment}\n\n"
                            f"<i>{alert.raw_text}</i>\n\n"
                            f"Нажмите кнопку ниже для получения контактов штаба."
                        )
                    else:
                        dispatch_text = (
                            f"🚨 <b>КРАСНЫЙ КОД: ТРЕБУЕТСЯ БПЛА</b> 🚨\n\n"
                            f"<b>Локация:</b> {alert.city}\n"
                            f"<b>Ситуация:</b> {alert.problem_type}\n"
                            f"<b>Нужен:</b> {alert.required_equipment}\n\n"
                            f"<i>{alert.raw_text}</i>\n\n"
                            f"Нажмите кнопку ниже для получения контактов штаба."
                        )
                
                    try:
                        await bot.send_message(op.telegram_id, dispatch_text, parse_mode="HTML", reply_markup=dispatch_kb)
                    except Exception:
                        pass
                
                if alert.reporter:
                    try:
                        await bot.send_message(
                            alert.reporter.telegram_id,
                            f"✅ Ваша экстренная заявка одобрена модератором через веб-панель. Разослано {len(operators)} операторам."
                        )
                    except Exception:
                        pass
                        
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
    """Одобрение работы через веб с Push-рассылкой"""
    try:
        async with async_session() as session:
            from sqlalchemy.orm import selectinload
            from db.models.job import Job
            job = await session.get(Job, job_id, options=[selectinload(Job.employer)])
            if not job:
                return JSONResponse(status_code=404, content={"error": "Not found"})
                
            job.status = "active"
            from db.crud.log import create_moderation_log
            await create_moderation_log(session, getattr(request.state, "user_id", None), "approve_job", "job", job_id)
            await session.commit()
            
            # --- Push Notifications to Operators for Freelance Job ---
            from db.models.category import Category
            stmt = (
                select(Listing)
                .join(Category)
                .where(Category.name == "Операторы")
                .where(Listing.status == "active")
            )
            if job.city:
                stmt = stmt.where(Listing.city.ilike(f"%{job.city}%"))
                
            op_result = await session.execute(stmt)
            operators_listings = op_result.scalars().all()
            
            notified_set = set()
            for l in operators_listings:
                notified_set.add(l.user_id) # Using User IDs
                
            bot = getattr(request.app.state, 'bot', None)
            if bot:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💼 Подробнее", callback_data=f"job_view_{job.id}")]
                ])
                for user_db_id in notified_set:
                    # We need the user's telegram_id
                    user = await session.get(User, user_db_id)
                    if not user: continue
                    try:
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text=f"🎬 <b>НОВАЯ ЗАДАЧА В ВАШЕМ ГОРОДЕ!</b>\n\n"
                                 f"<b>Задача:</b> {job.title}\n"
                                 f"<b>Бюджет:</b> {job.budget}\n\n"
                                 f"Откликнитесь первым!",
                            parse_mode="HTML",
                            reply_markup=kb
                        )
                    except Exception as e:
                        pass
                        
                # Notify employer
                if job.employer:
                    try:
                        await bot.send_message(
                            job.employer.telegram_id,
                            f"✅ Ваш заказ '{job.title}' успешно опубликован модератором!\n\n"
                            f"🔔 Прямо сейчас мы отправили пуш-уведомления {len(notified_set)} операторам рядом с вами.",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
            
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

@app.get("/system")
async def system_page(request: Request):
    """Placeholder view for existing system."""
    return {"status": "ok"}

# --- SUPERAPP NEW ENDPOINTS ---

@app.get("/vision", dependencies=[Depends(verify_admin)])
async def vision_page(request: Request):
    return templates.TemplateResponse("vision.html", {"request": request, "role": getattr(request.state, "role", "admin")})

@app.post("/api/vision/analyze", dependencies=[Depends(verify_admin)])
async def api_vision_analyze(request: Request, file: UploadFile = File(...)):
    try:
        content = await file.read()
        from bot.config import GEMINI_API_KEY
        if not GEMINI_API_KEY:
            return JSONResponse({"status": "error", "message": "API ключ не настроен"}, status_code=500)
            
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
        
        prompt = (
            "SYSTEM ROLE: You are Gorizont AI-Vision. Analyze this drone photo for B2B inspection. "
            "Report defects, measurements, or anomalies. Format as clean HTML without backticks or markdown code blocks."
        )
        
        response = await client.aio.models.generate_content(
            model='gemini-1.5-pro',
            contents=[
                genai.types.Part.from_bytes(data=content, mime_type=file.content_type),
                prompt
            ]
        )
        return JSONResponse({"status": "ok", "report": response.text})
    except Exception as e:
        logger.error(f"Vision error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/fleet", dependencies=[Depends(verify_admin)])
async def fleet_page(request: Request):
    try:
        async with async_session() as session:
            from db.models.fleet import FleetDrone, FleetBattery
            drones_res = await session.execute(select(FleetDrone))
            drones = drones_res.scalars().all()
            
            bats_res = await session.execute(select(FleetBattery))
            batteries = bats_res.scalars().all()
            
        return templates.TemplateResponse("fleet.html", {
            "request": request, 
            "role": getattr(request.state, "role", "admin"),
            "drones": drones,
            "batteries": batteries
        })
    except Exception as e:
        logger.error(e)
        raise e

@app.get("/radar", dependencies=[Depends(verify_admin)])
async def radar_page(request: Request):
    try:
        import re
        async with async_session() as db:
            sales_res = await db.execute(select(Listing).where(Listing.listing_type == "sale", Listing.status == "active"))
            sales = sales_res.scalars().all()
            
        def extract_price(plist):
            nums = re.findall(r'\d+', str(plist).replace(" ", ""))
            if nums: return int(nums[0])
            return 0
            
        models_prices = {}
        for s in sales:
            clean_title = s.title.strip().lower()
            price = extract_price(s.price_list)
            if price > 5000:
                if clean_title not in models_prices:
                    models_prices[clean_title] = []
                models_prices[clean_title].append({"id": s.id, "price": price, "title": s.title, "city": s.city, "link": f"/listings?query={s.id}"})
                
        arbitrage_deals = []
        for model, items in models_prices.items():
            if len(items) >= 2:
                avg_price = sum([i["price"] for i in items]) / len(items)
                for i in items:
                    if i["price"] < avg_price * 0.8:
                        arbitrage_deals.append({
                            "id": i["id"],
                            "title": i["title"],
                            "price": i["price"],
                            "avg": avg_price,
                            "city": i["city"],
                            "link": i["link"],
                            "discount_percent": round(100 - (i["price"] / avg_price)*100)
                        })
                        
        mock_tenders = [
            {"id": "0373100000124000055", "title": "Аэрофотосъемка (ЛЭП 15км)", "price": 145000, "region": "Свердловская обл.", "link": "#"},
            {"id": "32413480112", "title": "Мониторинг теплосетей с БПЛА", "price": 380000, "region": "Новосибирск", "link": "#"},
            {"id": "0173200001424000112", "title": "Кадастровые работы (RTK)", "price": 550000, "region": "Московская обл.", "link": "#"}
        ]
        
        # Мокируем Внешние сделки (Авито) как просил юзер!
        external_deals = [
            {"title": "DJI Mavic 3 Enterprise (Срочно)", "price": 140000, "avg": 210000, "discount": 33, "source": "Внешняя Доска (Avito)"},
            {"title": "Matrice 30T", "price": 380000, "avg": 500000, "discount": 24, "source": "Внешний Каталог"}
        ]
                        
        return templates.TemplateResponse("radar.html", {
            "request": request, 
            "role": getattr(request.state, "role", "admin"),
            "arbitrage_deals": arbitrage_deals,
            "external_deals": external_deals,
            "b2g_tenders": mock_tenders
        })
    except Exception as e:
        logger.error(e)
        raise e

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

from pydantic import BaseModel

class FlightPlanCreate(BaseModel):
    user_id: int # Temporary passed from client until full JWT is unified
    coords: str
    radius: str
    alt_min: str
    alt_max: str
    time_start: str
    time_end: str
    task_desc: str
    operator_name: str
    phone: str
    shr_code: str
    is_emergency: bool = False

@app.post("/api/v1/flight_plans")
async def create_flight_plan(plan: FlightPlanCreate):
    """Сохранение плана полетов из интерфейса Web"""
    try:
        from db.models.flight_plan import FlightPlan
        async with async_session() as session:
            new_plan = FlightPlan(
                user_id=plan.user_id,
                coords=plan.coords,
                radius=plan.radius,
                alt_min=plan.alt_min,
                alt_max=plan.alt_max,
                time_start=plan.time_start,
                time_end=plan.time_end,
                task_desc=plan.task_desc,
                operator_name=plan.operator_name,
                phone=plan.phone,
                shr_code=plan.shr_code,
                is_emergency=plan.is_emergency,
                status="pending"
            )
            session.add(new_plan)
            await session.commit()
            
            # TODO: trigger telegram notification to Admin/Moderator here
            
            return JSONResponse(content={"ok": True, "flight_plan_id": new_plan.id})
    except Exception as e:
        logger.error(f"Error creating flight plan: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/api/v1/flight_plans/{user_id}")
async def get_flight_plans(user_id: int):
    """Получить список планов пользователя"""
    try:
        from db.models.flight_plan import FlightPlan
        async with async_session() as session:
            result = await session.execute(
                select(FlightPlan).where(FlightPlan.user_id == user_id).order_by(FlightPlan.created_at.desc())
            )
            plans = result.scalars().all()
            
            data = []
            for p in plans:
                data.append({
                    "id": p.id,
                    "task_desc": p.task_desc,
                    "coords": p.coords,
                    "status": p.status,
                    "is_emergency": p.is_emergency,
                    "created_at": p.created_at.isoformat()
                })
            return JSONResponse(content={"ok": True, "flight_plans": data})
    except Exception as e:
        logger.error(f"Error fetching flight plans: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/api/v1/radar/markers")
async def get_radar_markers(session: AsyncSession = Depends(get_session)):
    """
    Returns a unified array of markers for the Live Map.
    Combines: Jobs (category='job'), Emergencies (category='emergency'), and active Flight Plans (category='nofly' or 'flight').
    """
    markers = []
    
    # 1. Active Jobs
    result_jobs = await session.execute(
        select(Job).where(Job.status == "active", Job.lat != None, Job.lng != None)
    )
    for j in result_jobs.scalars().all():
        markers.append({
            "id": f"job_{j.id}",
            "lat": j.lat,
            "lng": j.lng,
            "type": "job",
            "title": j.title,
            "desc": j.category,
            "budget": j.budget
        })
        
    # 2. Emergencies (SAR)
    result_em = await session.execute(
        select(EmergencyAlert).where(EmergencyAlert.status == "pending", EmergencyAlert.lat != None, EmergencyAlert.lng != None)
    )
    for e in result_em.scalars().all():
        markers.append({
            "id": f"em_{e.id}",
            "lat": e.lat,
            "lng": e.lng,
            "type": "emergency",
            "title": "Поиск пропавшего человека (SAR)" if not e.problem_type else e.problem_type,
            "desc": e.raw_text[:100] + ("..." if len(e.raw_text) > 100 else "")
        })
        
    # 3. Flight Plans (OrVD)
    result_fp = await session.execute(
        select(FlightPlan).where(FlightPlan.status.in_(["pending", "approved"]), FlightPlan.lat != None, FlightPlan.lng != None)
    )
    for f in result_fp.scalars().all():
        try:
            radius_km = float(f.radius)
        except:
            radius_km = 1.0  # default fallback
            
        markers.append({
            "id": f"fp_{f.id}",
            "lat": f.lat,
            "lng": f.lng,
            "type": "nofly" if f.status == "approved" else "pending_flight",
            "title": "Согласованный полет ИВП" if f.status == "approved" else "Заявка на ИВП",
            "desc": f"С {f.time_start} по {f.time_end} | Задание: {f.task_desc}",
            "radius_km": radius_km,
            "alt_min": f.alt_min,
            "alt_max": f.alt_max,
            "time_start": f.time_start,
            "time_end": f.time_end,
            "operator_name": f.operator_name
        })
        
    # 4. Danger Zones (UAV alerts)
    try:
        from bot.services.emergency_monitor import monitor_service
        danger_zones = monitor_service.get_danger_zones()
        markers.extend(danger_zones)
    except Exception as e:
        logger.error(f"Error fetching danger zones: {e}")
        
    return markers

@app.get("/api/v1/weather")
async def get_weather_api(lat: float, lon: float):
    from bot.services.weather import get_weather
    data = await get_weather(lat, lon)
    if data:
        return JSONResponse(content={"ok": True, "weather": data})
    return JSONResponse(status_code=500, content={"ok": False, "error": "Не удалось получить погоду"})

@app.get("/api/v1/momoa/flight_risk")
async def get_momoa_flight_risk(task_desc: str, lat: float, lon: float):
    from bot.services.weather import get_weather
    from bot.services.emergency_monitor import monitor_service
    
    weather_data = await get_weather(lat, lon)
    if not weather_data:
        weather_data = {"risk_level": "unknown", "risk_reasons": []}
        
    analysis = await monitor_service.evaluate_flight_risk(task_desc, weather_data)
    
    return JSONResponse(content={
        "ok": True,
        "weather": weather_data,
        "momoa_analysis": analysis
    })

class RegistrationLeadCreate(BaseModel):
    user_id: int
    drone_brand_model: str
    serial_number: str

@app.post("/api/v1/lead_registration")
async def create_registration_lead(lead: RegistrationLeadCreate):
    """Логирование факта генерации бланка Росавиации для дальнейшего прогрева лида"""
    try:
        from db.models.log import UserActionLog
        async with async_session() as session:
            # Логируем как обычное действие (или создали бы отдельную таблицу, но пока хватит лога)
            new_log = UserActionLog(
                user_id=lead.user_id,
                action_type="rosaviatsiya_pdf_generated",
                details=f"Сгенерировано заявление на постановку на учет: {lead.drone_brand_model} (SN: {lead.serial_number})"
            )
            session.add(new_log)
            await session.commit()
            
            # TODO: Можно отправить уведомление менеджеру в Telegram.
            
            return JSONResponse(content={"ok": True})
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


class FlightPlanCreate(BaseModel):
    user_id: int
    coords: str
    radius: str
    alt_min: str
    alt_max: str
    time_start: str
    time_end: str
    task_desc: str
    operator_name: str
    phone: str
    shr_code: str
    is_emergency: bool = False
    lat: float | None = None
    lng: float | None = None


from bot.handlers.airspace import MOCK_NFZ_ZONES

@app.get("/api/v1/nfz_zones")
async def get_nfz_zones():
    """Возвращает список запретных зон из единого источника."""
    zones = []
    for idx, (lat, lng, radius, z_type, name) in enumerate(MOCK_NFZ_ZONES):
        zones.append({
            "id": f"nfz_{idx}",
            "lat": lat,
            "lng": lng,
            "radiusKm": radius,
            "type": "prohibited" if z_type in ("UAV_BAN", "MILITARY") else "airport",
            "name": name,
            "description": f"Ограничение полетов. Тип: {z_type}"
        })
    return {"ok": True, "zones": zones}

@app.post("/api/v1/flight_plans")
async def create_flight_plan(plan: FlightPlanCreate):
    """
    Создание плана полёта через веб-форму (ОрВД).
    Симуляция отправки в СППИ (Главный Центр).
    После сохранения — уведомление всех админов через бота.
    """
    try:
        # Mocking SPPI Integration delay
        import asyncio
        await asyncio.sleep(1.0)
        logger.info(f"SPPI Integration Mock: Flight Plan {plan.coords} successfully sent to Zonal Center.")

        async with async_session() as session:
            # Находим пользователя по telegram_id (user_id из фронта — это Telegram ID)
            result = await session.execute(
                select(User).where(User.telegram_id == plan.user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return JSONResponse(status_code=404, content={"ok": False, "error": "User not found"})

            new_plan = FlightPlan(
                user_id=user.id,
                coords=plan.coords,
                radius=plan.radius,
                alt_min=plan.alt_min,
                alt_max=plan.alt_max,
                time_start=plan.time_start,
                time_end=plan.time_end,
                task_desc=plan.task_desc,
                operator_name=plan.operator_name,
                phone=plan.phone,
                shr_code=plan.shr_code,
                is_emergency=plan.is_emergency,
                lat=plan.lat,
                lng=plan.lng,
                status="pending_sppi", # SPPI Mock Status
            )
            session.add(new_plan)
            await session.commit()
            await session.refresh(new_plan)
            
            # Отправляем уведомление админам через бота (если бот запущен)
            try:
                bot = request.app.state.bot
                if bot:
                    from bot.handlers.admin_flight import notify_admins_flight_plan
                    await notify_admins_flight_plan(bot, new_plan.id)
            except Exception as e:
                logger.warning(f"Could not notify admins about new flight plan: {e}")

        return JSONResponse(content={"ok": True, "plan_id": new_plan.id, "sppi_status": "submitted"})

    except Exception as e:
        logger.error(f"Error creating flight plan: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


from db.models.tender import Tender
from db.models.tender_bid import TenderBid
from db.models.wallet import Wallet

class TenderBidCreate(BaseModel):
    tender_id: int
    contractor_id: int
    price_offer: int
    comment: str | None = None

@app.get("/api/v1/tenders")
async def get_tenders(session: AsyncSession = Depends(get_session)):
    """Получение активных B2B/B2G Тендеров и Госконтрактов."""
    result = await session.execute(select(Tender).where(Tender.status == "active").order_by(Tender.created_at.desc()))
    tenders = result.scalars().all()
    out = []
    if not tenders:
        # Инъекция Демо-госконтрактов для презентации
        out.append({
            "id": 9991, 
            "employer_id": 0, 
            "title": "Аэрофотосъемка нефтепровода 'Восток' (участок 150 км)",
            "description": "Требуется проведение мультиспектральной съемки с применением БПЛА самолетного типа. Наличие лицензии обязательно.",
            "category": "Мониторинг", "budget": 1250000, "deadline": "2026-05-10T12:00:00Z",
            "status": "active", "region": "ХМАО", "created_at": "2026-03-30T00:00:00Z"
        })
        out.append({
            "id": 9992, 
            "employer_id": 0, 
            "title": "Опрыскивание кукурузных полей, 500 Гектар",
            "description": "Агрохолдинг ищет подрядчиков с тяжелыми агродронами (бак от 30л) для внесения пестицидов. Обеспечение контракта 5%.",
            "category": "Агро", "budget": 950000, "deadline": "2026-04-15T12:00:00Z",
            "status": "active", "region": "Краснодарский край", "created_at": "2026-03-29T10:00:00Z"
        })
    else:
        for t in tenders:
            out.append({
                "id": t.id, "employer_id": t.employer_id, "title": t.title, "description": t.description,
                "category": t.category, "budget": t.budget, "deadline": t.deadline.isoformat() if t.deadline else "",
                "status": t.status, "region": t.region, "created_at": t.created_at.isoformat() if t.created_at else ""
            })
    return JSONResponse(content={"ok": True, "tenders": out})

@app.get("/api/v1/tenders/map")
async def get_tenders_for_map(telegram_id: int = 0, session: AsyncSession = Depends(get_session)):
    """API Радара. Доступен только для B2B пользователей (с ИНН)."""
    from db.models.tender import Tender
    
    # 1. Загружаем юзера и проверяем B2B статус
    if telegram_id > 0:
        ures = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = ures.scalar_one_or_none()
        if not user or not user.inn:
            # Значит, юзер не заполнил ИНН = блокируем доступ
            return JSONResponse(content={"ok": False, "error": "b2b_locked", "map_tenders": []})
    else:
        # Для публичного просмотра тоже лочим
        return JSONResponse(content={"ok": False, "error": "b2b_locked", "map_tenders": []})

    # 2. Если все Ок - отдаем карту
    res = await session.execute(select(Tender).where(Tender.status == "active").where(Tender.lat.isnot(None)))
    tenders = res.scalars().all()
    
    out = []
    # Демо-маркеры, если БД пуста
    if not tenders:
        out.append({"id": 9991, "title": "Аэрофотосъемка нефтепровода 'Восток'", "budget": 1250000, "category": "Мониторинг", "region": "ХМАО", "lat": 61.0, "lng": 69.0})
        out.append({"id": 9992, "title": "Опрыскивание полей 500 Га", "budget": 950000, "category": "Агро", "region": "Краснодарский край", "lat": 45.03, "lng": 38.97})
        
    for t in tenders:
        out.append({
            "id": t.id, "title": t.title, "budget": t.budget,
            "category": t.category, "region": t.region, "lat": t.lat, "lng": t.lng
        })
    return JSONResponse(content={"ok": True, "map_tenders": out})

@app.post("/api/v1/tenders/bid")
async def place_tender_bid(bid: TenderBidCreate, session: AsyncSession = Depends(get_session)):
    """Участие в тендере с заморозкой 5% средств (обеспечение заявки) и проверкой AI на демпинг."""
    from bot.services.smart_arbitrage import smart_arbitrator
    try:
        # 1. Получаем тендер для сравнения цены
        tender_res = await session.execute(select(Tender).where(Tender.id == bid.tender_id))
        tender = tender_res.scalar_one_or_none()
        if not tender:
            return JSONResponse(status_code=404, content={"ok": False, "error": "Tender not found"})
            
        # 2. Проверка на Искусственный Демпинг (Скидка > 30%)
        is_dumping = False
        ai_reason = ""
        if bid.price_offer < tender.budget * 0.7:
            dump_verdict = await smart_arbitrator.check_dumping(tender.title, tender.budget, bid.price_offer)
            if dump_verdict.get("is_dumping", False):
                is_dumping = True
                ai_reason = dump_verdict.get("reason", "Заблокировано ИИ из-за неадекватного занижения цены.")

        if is_dumping:
            # Создаем отклик со статусом rejected_by_ai без заморозки средств
            new_bid = TenderBid(
                tender_id=bid.tender_id,
                contractor_id=bid.contractor_id,
                price_offer=bid.price_offer,
                comment=bid.comment,
                status="rejected_by_ai",
                ai_reason=ai_reason
            )
            session.add(new_bid)
            await session.commit()
            
            # Уведомляем пилота
            try:
                alert = f"⚠️ <b>Ваш отклик на тендер #{tender.id} заблокирован!</b>\n\n🤖 <b>Вердикт AI:</b> {ai_reason}"
                await app.state.bot.send_message(bid.contractor_id, alert, parse_mode="HTML")
            except: pass
            
            return JSONResponse(content={"ok": False, "error": "Ваш отклик отклонен AI-Модератором по причине демпинга цены.", "ai_reason": ai_reason})

        # --- Стандартный флоу подачи (если не демпинг) ---
        # Проверяем баланс
        required_security = bid.price_offer * 0.05
        
        wallet_res = await session.execute(select(Wallet).where(Wallet.user_id == bid.contractor_id))
        wallet = wallet_res.scalar_one_or_none()
        
        if not wallet or wallet.balance < required_security:
            return JSONResponse(
                status_code=400, 
                content={"ok": False, "error": f"Недостаточно средств. Для обеспечения заявки нужно заморозить {required_security:,.2f} ₽ (5%). На вашем балансе: {wallet.balance if wallet else 0} ₽"}
            )
            
        # Замораживаем средства
        wallet.balance -= required_security
        wallet.hold_balance += required_security
        
        # Создаем Bid
        new_bid = TenderBid(
            tender_id=bid.tender_id,
            contractor_id=bid.contractor_id,
            price_offer=bid.price_offer,
            comment=bid.comment,
            status="pending"
        )
        session.add(new_bid)
        await session.commit()
        
        return JSONResponse(content={"ok": True, "message": "Заявка успешно подана. Средства заморожены на балансе Гаранта."})
    except Exception as e:
        logger.error(f"Tender Bid Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": "Internal Server Error"})


class WebListingCreate(BaseModel):
    user_telegram_id: int
    category_id: int
    city: str
    title: str
    description: str
    price_list: str
    contacts: str
    listing_type: str = "rental"

@app.post("/api/v1/listings/web")
async def create_web_listing(data: WebListingCreate, session: AsyncSession = Depends(get_session)):
    """API создания объявления через WEB с интеграцией ИИ-Модератора."""
    try:
        from bot.services.smart_moderator import smart_moderator
        from db.crud.listing import create_listing
        from db.crud.user import get_user_by_telegram_id
        
        user = await get_user_by_telegram_id(session, data.user_telegram_id)
        if not user:
            return JSONResponse(status_code=403, content={"ok": False, "error": "User not found"})
        
        # Проверяем текст через ИИ-модератор (единый движок для Telegram и Web)
        ai_result = await smart_moderator.auto_moderate_listing(
            title=data.title,
            description=data.description,
            category=str(data.category_id),
            price=data.price_list
        )
        
        final_status = "active" if ai_result.get("status") == "APPROVED" else "moderation"
        
        listing = await create_listing(
            session=session,
            user_id=user.id,
            category_id=data.category_id,
            city=data.city,
            title=data.title,
            description=data.description,
            deposit_terms="Не требуется (Web)",
            delivery_terms="Самовывоз (Web)",
            price_list=data.price_list,
            contacts=data.contacts,
            photo_ids=[], # Web uploads implementation pending
            listing_type=data.listing_type,
            status=final_status
        )
        
        if final_status == "moderation":
            # Уведомляем админов, так как требуется ручная проверка
            from bot.handlers.admin import ADMIN_IDS
            admin_text = (
                f"🆕 <b>Новое WEB-объявление на модерации!</b>\n\n"
                f"🏙 Город: {data.city}\n"
                f"📦 Название: {data.title}\n"
                f"🤖 <b>Вердикт ИИ:</b> <i>{ai_result.get('reason', 'Требует ручной проверки')}</i>"
            )
            for admin_id in ADMIN_IDS:
                try:
                    await app.state.bot.send_message(admin_id, admin_text, parse_mode="HTML")
                except Exception:
                    pass
                    
        return JSONResponse(content={"ok": True, "listing_id": listing.id, "status": final_status, "ai_reason": ai_result.get("reason")})
    except Exception as e:
        logger.error(f"Web Listing Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/api/v1/dadata/company")
async def get_dadata_company(inn: str):
    """
    Интеграция DaData (KYC) для автозаполнения реквизитов бизнеса по ИНН.
    В продакшене используется API: https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party
    """
    import asyncio
    await asyncio.sleep(0.8) # Имитация сетевой задержки API DaData
    
    inn = inn.strip()
    # Mock-возврат для самых популярных ИНН России + fallback:
    if inn == "7736207543":
        return JSONResponse(content={"ok": True, "company_name": 'ООО "ЯНДЕКС"', "address": "г Москва, ул Льва Толстого, д 16", "status": "ACTIVE", "director": "Савиновский Артем Анатольевич"})
    elif inn == "7707083893":
        return JSONResponse(content={"ok": True, "company_name": 'ПАО "СБЕРБАНК"', "address": "г Москва, ул Вавилова, д 19", "status": "ACTIVE", "director": "Греф Герман Оскарович"})
    elif len(inn) in [10, 12] and inn.isdigit():
        return JSONResponse(content={
            "ok": True, 
            "company_name": f'ООО "АэроТех-{inn[:4]}"', 
            "address": "г Москва, Инновационный центр Сколково", 
            "status": "ACTIVE",
            "director": "Иванов И. И."
        })
        
    return JSONResponse(status_code=404, content={"ok": False, "error": "Организация по ИНН не найдена. Проверьте правильность ввода."})


@app.get("/api/v1/my_flight_plans/{telegram_id}")
async def get_my_flight_plans(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """Получение списка своих планов полётов по Telegram ID."""
    try:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return JSONResponse(content=[])

        result = await session.execute(
            select(FlightPlan)
            .where(FlightPlan.user_id == user.id)
            .order_by(FlightPlan.created_at.desc())
            .limit(20)
        )
        plans = result.scalars().all()

        return [
            {
                "id": p.id,
                "coords": p.coords,
                "radius": p.radius,
                "task_desc": p.task_desc,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
                "is_emergency": p.is_emergency,
            }
            for p in plans
        ]
    except Exception as e:
        logger.error(f"Error fetching flight plans: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


# --- Tenders B2B Module ---
from db.models.tender import Tender
from db.models.tender_bid import TenderBid
from datetime import datetime
from sqlalchemy.orm import joinedload

@app.get("/api/v1/tenders")
async def get_tenders(session: AsyncSession = Depends(get_session)):
    """Returns a list of all public B2B tenders"""
    try:
        result = await session.execute(
            select(Tender).order_by(Tender.created_at.desc())
        )
        tenders = result.scalars().all()
        return [
            {
                "id": t.id,
                "employer_id": t.employer_id,
                "title": t.title,
                "description": t.description,
                "budget": t.budget,
                "deadline": t.deadline.isoformat() if t.deadline else None,
                "status": t.status,
                "region": t.region,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tenders
        ]
    except Exception as e:
        logger.error(f"Error fetching tenders: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/api/v1/tenders/{tender_id}")
async def get_tender_detail(tender_id: int, session: AsyncSession = Depends(get_session)):
    """Returns details of a tender and its anonymous bids"""
    try:
        result = await session.execute(
            select(Tender).options(joinedload(Tender.bids)).where(Tender.id == tender_id)
        )
        t = result.scalars().first()
        if not t:
            return JSONResponse(status_code=404, content={"ok": False, "error": "Tender not found"})
        
        # We only expose price offers and dates (closed envelope simulation for public view)
        anon_bids = []
        for b in t.bids:
            anon_bids.append({
                "id": b.id,
                "price_offer": b.price_offer,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "status": b.status,
                "ai_reason": getattr(b, "ai_reason", "")
            })
            
        # Cross-sell: fetch up to 3 active listings for equipment recommendations
        from db.models.listing import Listing
        from sqlalchemy import func as sql_func
        rec_result = await session.execute(
            select(Listing)
            .where(Listing.status == "active")
            .order_by(sql_func.random())
            .limit(3)
        )
        rec_listings = rec_result.scalars().all()
        recommended_drones = [
            {
                "id": l.id,
                "title": l.title,
                "price_list": l.price_list,
                "listing_type": l.listing_type,
                "city": l.city,
            }
            for l in rec_listings
        ]

        return {
            "id": t.id,
            "employer_id": t.employer_id,
            "title": t.title,
            "description": t.description,
            "budget": t.budget,
            "deadline": t.deadline.isoformat() if t.deadline else None,
            "status": t.status,
            "region": t.region,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "bids": anon_bids,
            "total_bids": len(anon_bids),
            "recommended_drones": recommended_drones
        }
    except Exception as e:
        logger.error(f"Error fetching tender detail: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.post("/api/v1/tenders")
async def create_tender(request: Request, session: AsyncSession = Depends(get_session)):
    """Creates a new tender"""
    try:
        data = await request.json()
        deadline_str = data.get("deadline")
        deadline_dt = datetime.fromisoformat(deadline_str.replace("Z", "+00:00")) if deadline_str else datetime.utcnow()
        
        tender = Tender(
            employer_id=int(data.get("employer_id", 0)),
            title=data.get("title", "Без названия"),
            description=data.get("description", ""),
            category=data.get("category", ""),
            budget=int(data.get("budget", 0)),
            deadline=deadline_dt,
            region=data.get("region", "РФ"),
            status="active"
        )
        session.add(tender)
        await session.commit()
        await session.refresh(tender)
        return {"ok": True, "tender_id": tender.id}
    except Exception as e:
        logger.error(f"Error creating tender: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.post("/api/v1/tenders/{tender_id}/bid")
async def create_tender_bid(tender_id: int, request: Request, session: AsyncSession = Depends(get_session)):
    """Creates a bid on a tender"""
    try:
        data = await request.json()
        bid = TenderBid(
            tender_id=tender_id,
            contractor_id=int(data.get("contractor_id", 0)),
            price_offer=int(data.get("price_offer", 0)),
            comment=data.get("comment", ""),
            status="pending"
        )
        session.add(bid)
        await session.commit()
        return {"ok": True, "bid_id": bid.id}
    except Exception as e:
        logger.error(f"Error creating tender bid: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@app.get("/reports", dependencies=[Depends(verify_admin)])
async def reports_page(request: Request):
    """Сводный отчёт по платформе — статистика и аналитика."""
    try:
        async with async_session() as session:
            # Users
            total_users = await session.scalar(select(func.count()).select_from(User)) or 0
            new_users_7d = await session.scalar(
                select(func.count()).select_from(User).where(
                    User.created_at >= (datetime.utcnow().replace(hour=0, minute=0, second=0) - __import__('datetime').timedelta(days=7))
                )
            ) or 0
            admins_count = await session.scalar(
                select(func.count()).select_from(User).where(User.is_admin == True)
            ) or 0
            banned_count = await session.scalar(
                select(func.count()).select_from(User).where(User.is_banned == True)
            ) or 0

            # Listings
            from db.models.listing import Listing
            total_listings = await session.scalar(select(func.count()).select_from(Listing)) or 0
            active_listings = await session.scalar(
                select(func.count()).select_from(Listing).where(Listing.status == "active")
            ) or 0
            pending_listings = await session.scalar(
                select(func.count()).select_from(Listing).where(Listing.status == "pending")
            ) or 0
            rejected_listings = await session.scalar(
                select(func.count()).select_from(Listing).where(Listing.status == "rejected")
            ) or 0

            # Listings by category
            from db.models.category import Category
            from sqlalchemy import text
            cat_result = await session.execute(
                select(Category.name, func.count(Listing.id).label("cnt"))
                .join(Listing, Listing.category_id == Category.id, isouter=True)
                .group_by(Category.name)
                .order_by(text("cnt DESC"))
            )
            by_category = [{"name": r[0], "count": r[1]} for r in cat_result.all()]

            # Jobs
            from db.models.job import Job
            total_jobs = await session.scalar(select(func.count()).select_from(Job)) or 0
            active_jobs = await session.scalar(
                select(func.count()).select_from(Job).where(Job.status == "active")
            ) or 0

            # Tenders
            from db.models.tender import Tender
            total_tenders = await session.scalar(select(func.count()).select_from(Tender)) or 0
            active_tenders = await session.scalar(
                select(func.count()).select_from(Tender).where(Tender.status == "active")
            ) or 0
            total_tender_budget = await session.scalar(
                select(func.sum(Tender.budget)).where(Tender.status == "active")
            ) or 0

            # Emergencies
            total_emergencies = await session.scalar(select(func.count()).select_from(EmergencyAlert)) or 0
            open_emergencies = await session.scalar(
                select(func.count()).select_from(EmergencyAlert).where(EmergencyAlert.status == "pending")
            ) or 0

        return templates.TemplateResponse(
            request=request, name="reports.html", context={
                "role": getattr(request.state, "role", "admin"),
                "users": {
                    "total": total_users,
                    "new_7d": new_users_7d,
                    "admins": admins_count,
                    "banned": banned_count,
                },
                "listings": {
                    "total": total_listings,
                    "active": active_listings,
                    "pending": pending_listings,
                    "rejected": rejected_listings,
                    "by_category": by_category,
                },
                "jobs": {"total": total_jobs, "active": active_jobs},
                "tenders": {
                    "total": total_tenders,
                    "active": active_tenders,
                    "total_budget": total_tender_budget,
                },
                "emergencies": {"total": total_emergencies, "open": open_emergencies},
            }
        )
    except Exception as e:
        logger.error(f"Error rendering reports: {e}", exc_info=True)
        raise e


# --- WALLET & ESCROW API ---

from db.models.wallet import Wallet, Transaction

@app.get("/api/wallet/{user_id}")
async def get_wallet(user_id: int):
    """Возвращает баланс кошелька пользователя, создает если нет."""
    try:
        async with async_session() as session:
            wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
            if not wallet:
                wallet = Wallet(user_id=user_id, balance=0.0, hold_balance=0.0)
                session.add(wallet)
                await session.commit()
                await session.refresh(wallet)
                
            return {
                "ok": True,
                "wallet": {
                    "id": wallet.id,
                    "user_id": wallet.user_id,
                    "balance": wallet.balance,
                    "hold_balance": wallet.hold_balance,
                    "currency": wallet.currency
                }
            }
    except Exception as e:
        logger.error(f"Error fetching wallet: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/api/wallet/{user_id}/transactions")
async def get_wallet_transactions(user_id: int, limit: int = 10):
    """Возвращает историю транзакций пользователя."""
    try:
        async with async_session() as session:
            wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
            if not wallet:
                return {"ok": True, "transactions": []}
                
            stmt = select(Transaction).where(Transaction.wallet_id == wallet.id).order_by(Transaction.created_at.desc()).limit(limit)
            results = await session.execute(stmt)
            transactions = results.scalars().all()
            
            return {
                "ok": True,
                "transactions": [
                    {
                        "id": t.id,
                        "amount": t.amount,
                        "transaction_type": t.transaction_type,
                        "status": t.status,
                        "description": t.description,
                        "created_at": t.created_at.isoformat() if t.created_at else None
                    } for t in transactions
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/api/v1/auth/gosuslugi_login")
async def gosuslugi_mock_login(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """Модуль-заглушка для ЕСИА авторизации. Привязывает бейдж Госуслуг к юзеру."""
    try:
        from db.models.certificate import PilotCertificate
        # Create a mock verified identity certificate
        cert = PilotCertificate(
            user_id=telegram_id,
            cert_type="ЕСИА (Госуслуги)",
            document_number="Подтвержденная учетная запись",
            is_verified=True
        )
        session.add(cert)
        
        # Also let's grant them a mock drone license
        cert2 = PilotCertificate(
            user_id=telegram_id,
            cert_type="Свидетельство внешнего пилота (до 30кг)",
            document_number="Р-12345/26",
            is_verified=True
        )
        session.add(cert2)
        await session.commit()
        return JSONResponse(content={"ok": True, "message": "Авторизация через ЕСИА успешно пройдена!"})
    except Exception as e:
        logger.error(f"Gosuslugi Mock Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.get("/api/v1/pilots/{telegram_id}")
async def get_pilot_profile(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """Получение публичного профиля пилота с его сертификатами."""
    try:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return JSONResponse(status_code=404, content={"ok": False, "error": "Pilot not found"})
            
        from db.models.certificate import PilotCertificate
        certs_res = await session.execute(select(PilotCertificate).where(PilotCertificate.user_id == telegram_id))
        certs = certs_res.scalars().all()
        
        cert_data = []
        is_gosuslugi = False
        for c in certs:
            if "ЕСИА" in c.cert_type:
                is_gosuslugi = True
            cert_data.append({
                "type": c.cert_type,
                "document": c.document_number,
                "verified": c.is_verified,
                "date": c.created_at.isoformat() if c.created_at else None
            })
            
        return JSONResponse(content={
            "ok": True,
            "pilot": {
                "id": user.telegram_id,
                "name": f"{user.first_name} {user.last_name or ''}".strip() or "Аноним",
                "username": user.username,
                "company_name": getattr(user, "company_name", None),
                "is_gosuslugi_verified": is_gosuslugi,
                "verified_flight_hours": user.verified_flight_hours,
                "certificates": cert_data
            }
        })
    except Exception as e:
        logger.error(f"Pilot fetching error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": "Database Error"})

@app.post("/api/v1/pilots/{telegram_id}/telemetry/upload")
async def upload_dji_telemetry(telegram_id: int, file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    """Загрузка полетного лога DJI (.txt/.csv) для верификации часов налета."""
    try:
        content = await file.read()
        
        # Для MVP: простая моковая эвристика. Настоящие DJI логи зашифрованы ключами.
        # Вскрывать их нужно через специализированную библиотеку, пока делаем оценку по размеру файла:
        # В среднем 1 час логов = 1.5 МБ.
        size_bytes = len(content)
        if size_bytes < 512:
            return JSONResponse(status_code=400, content={"ok": False, "error": "Файл слишком мал для полётного лога DJI."})
            
        calculated_hours = round(size_bytes / (1.5 * 1024 * 1024), 2)
        if calculated_hours < 0.1:
            calculated_hours = 0.5 # Минимум полчаса для теста MVP
            
        # Обновляем БД
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            return JSONResponse(status_code=404, content={"ok": False, "error": "Пилот не найден"})
            
        # Прибавляем часы
        current_hours = user.verified_flight_hours if user.verified_flight_hours else 0.0
        user.verified_flight_hours = round(current_hours + calculated_hours, 2)
        await session.commit()
        
        return JSONResponse(content={
            "ok": True,
            "message": f"Телеметрия успешно обработана. Распознан налёт: {calculated_hours} час(ов).",
            "total_hours": user.verified_flight_hours
        })
    except Exception as e:
        logger.error(f"Telemetry Parsing Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": "Ошибка обработки лога телеметрии."})

class DisputeCreate(BaseModel):
    tender_id: int
    plaintiff_id: int
    defendant_id: int
    reason: str
    evidence: str

@app.post("/api/v1/tenders/dispute")
async def open_tender_dispute(data: DisputeCreate, session: AsyncSession = Depends(get_session)):
    """Открытие спора по тендеру и вызов ИИ-Арбитра для формирования отчета."""
    try:
        from db.models.dispute import EscrowDispute
        from db.models.tender import Tender
        from bot.services.smart_arbitrage import smart_arbitrator
        from bot.handlers.admin import ADMIN_IDS
        
        tender_res = await session.execute(select(Tender).where(Tender.id == data.tender_id))
        tender = tender_res.scalar_one_or_none()
        if not tender:
            return JSONResponse(status_code=404, content={"ok": False, "error": "Tender not found"})
            
        dispute = EscrowDispute(
            tender_id=data.tender_id,
            plaintiff_id=data.plaintiff_id,
            defendant_id=data.defendant_id,
            reason=data.reason,
            evidence_text=data.evidence,
            status="ai_reviewed"
        )
        
        # Получаем саммари от ИИ
        ai_verdict = await smart_arbitrator.analyze_dispute(
            tender_title=tender.title,
            tender_desc=tender.description,
            plaintiff_claim=data.reason,
            evidence=data.evidence
        )
        
        dispute.ai_summary = ai_verdict
        session.add(dispute)
        await session.commit()
        
        # Уведомляем админов
        admin_text = (
            f"⚖️ <b>НОВЫЙ АРБИТРАЖ (Tender #{tender.id})</b>\n\n"
            f"<b>Жалоба:</b> {data.reason[:100]}...\n\n"
            f"🤖 <b>Вердикт ИИ-Ассистента:</b>\n<i>{ai_verdict}</i>\n\n"
            f"Ожидает решения: Выплатить или Вернуть деньги."
        )
        for admin_id in ADMIN_IDS:
            try:
                await app.state.bot.send_message(admin_id, admin_text, parse_mode="HTML")
            except Exception:
                pass

        return JSONResponse(content={"ok": True, "message": "Спор открыт, ИИ-сводка отправлена модераторам."})
    except Exception as e:
        logger.error(f"Dispute Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

class TelegramAuthRequest(BaseModel):

    init_data: str

def validate_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    import hmac, hashlib
    from urllib.parse import parse_qsl
    try:
        parsed_data = dict(parse_qsl(init_data))
        if "hash" not in parsed_data:
            return False
            
        hash_received = parsed_data.pop("hash")
        
        # Сортируем ключи в алфавитном порядке
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
        
        # Создаем секретный ключ
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        
        # Вычисляем подпись
        hash_calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(hash_calculated, hash_received)
    except Exception:
        return False

@app.post("/api/v1/auth/telegram")
async def telegram_webapp_login(data: TelegramAuthRequest, session: AsyncSession = Depends(get_session)):
    """Верификация подписи WebApp initData для секьюрной авторизации в Горизонт Web."""
    import json
    from urllib.parse import parse_qsl
    from bot.config import BOT_TOKEN
    from db.crud.user import get_user_by_telegram_id
    
    is_valid = validate_telegram_webapp_data(data.init_data, BOT_TOKEN)
    if not is_valid:
        return JSONResponse(status_code=403, content={"ok": False, "error": "Invalid auth signature"})
        
    try:
        parsed = dict(parse_qsl(data.init_data))
        user_json = json.loads(parsed.get("user", "{}"))
        tg_id = user_json.get("id")
        
        if not tg_id:
            return JSONResponse(status_code=400, content={"ok": False, "error": "User ID missing from initData"})
            
        user = await get_user_by_telegram_id(session, tg_id)
        if not user:
            # Registration flow handles telegram bot /start command mostly.
            # Here we just inform the frontend. 
            return JSONResponse(content={"ok": True, "registered": False, "telegram_id": tg_id})
            
        return JSONResponse(content={
            "ok": True, 
            "registered": True,
            "user": {
                "id": user.id,
                "telegram_id": tg_id, 
                "first_name": user.first_name,
                "is_admin": user.is_admin
            }
        })
    except Exception as e:
        logger.error(f"Telegram Auth API Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

# --- P2P Messenger (Phase 22) ---

class ChatSendRequest(BaseModel):
    tender_id: int
    sender_id: int
    receiver_id: int
    content: str

@app.get("/api/v1/chat/history")
async def get_chat_history(tender_id: int, user1: int, user2: int, session: AsyncSession = Depends(get_session)):
    """История переписки двух пилотов по конкретному тендеру."""
    from db.models.message import Message
    try:
        res = await session.execute(
            select(Message)
            .where(Message.tender_id == tender_id)
            .where(
                ((Message.sender_id == user1) & (Message.receiver_id == user2)) |
                ((Message.sender_id == user2) & (Message.receiver_id == user1))
            )
            .order_by(Message.created_at.asc())
        )
        msgs = res.scalars().all()
        
        out = []
        for m in msgs:
            out.append({
                "id": m.id,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "content": m.content,
                "is_read": m.is_read,
                "created_at": m.created_at.isoformat()
            })
        return JSONResponse(content={"ok": True, "messages": out})
    except Exception as e:
        logger.error(f"Chat History Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.post("/api/v1/chat/send")
async def send_chat_message(data: ChatSendRequest, session: AsyncSession = Depends(get_session)):
    """Отправка сообщения и Telegram-уведомление партнеру."""
    from db.models.message import Message
    try:
        new_msg = Message(
            sender_id=data.sender_id,
            receiver_id=data.receiver_id,
            tender_id=data.tender_id,
            content=data.content
        )
        session.add(new_msg)
        await session.commit()
        
        # Отправка Telegram Уведомления получателю
        alert_text = (
            f"💬 <b>Новое сообщение в B2B-чате!</b>\n"
            f"По тендеру #{data.tender_id}\n\n"
            f"<i>{data.content[:100]}</i>"
        )
        from bot.config import WEBAPP_URL
        btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть Чат", web_app=WebAppInfo(url=f"{WEBAPP_URL}/dashboard/chat/{data.tender_id}"))]])
        try:
            await app.state.bot.send_message(data.receiver_id, alert_text, reply_markup=btn, parse_mode="HTML")
        except Exception as e:
            logger.warning(f"Could not notify {data.receiver_id} about new chat message: {e}")
            
        return JSONResponse(content={"ok": True, "message_id": new_msg.id})
    except Exception as e:
        logger.error(f"Chat Send Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

# --- Payments & Checkout (Phase 22) ---

class CheckoutRequest(BaseModel):
    telegram_id: int
    amount: float

@app.post("/api/v1/payments/checkout")
async def process_yookassa_checkout(data: CheckoutRequest, session: AsyncSession = Depends(get_session)):
    """Создает платеж в ЮKassa и возвращает URL для оплаты."""
    from bot.config import WEBAPP_URL
    import uuid
    import os
    from yookassa import Configuration, Payment
    
    Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID", "123456")
    Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY", "test_xxxxx")
    
    try:
        if data.amount <= 0:
            return JSONResponse(status_code=400, content={"ok": False, "error": "Amount must be positive"})
            
        # Формируем счет
        payment = Payment.create({
            "amount": {
                "value": f"{data.amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{WEBAPP_URL}/dashboard/wallet"
            },
            "capture": True,
            "description": f"Пополнение кошелька Горизонт (user_id: {data.telegram_id})",
            "metadata": {
                "telegram_id": data.telegram_id
            }
        }, str(uuid.uuid4()))
        
        # Получаем URL для редиректа
        confirmation_url = payment.confirmation.confirmation_url
        
        return JSONResponse(content={"ok": True, "confirmation_url": confirmation_url})
    except Exception as e:
        logger.error(f"Yookassa Checkout Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

from fastapi import Request

@app.post("/api/v1/payments/webhook")
async def yookassa_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    """Вебхук от ЮKassa (срабатывает при payment.succeeded)."""
    from db.models.wallet import Wallet, Transaction
    import json
    try:
        event_json = await request.json()
        
        if event_json.get("event") == "payment.succeeded":
            payment_obj = event_json.get("object", {})
            metadata = payment_obj.get("metadata", {})
            telegram_id = int(metadata.get("telegram_id", 0))
            amount = float(payment_obj.get("amount", {}).get("value", 0))
            
            if telegram_id > 0 and amount > 0:
                wallet_res = await session.execute(select(Wallet).where(Wallet.user_id == telegram_id))
                wallet = wallet_res.scalar_one_or_none()
                
                if not wallet:
                    wallet = Wallet(user_id=telegram_id, balance=0, hold_balance=0)
                    session.add(wallet)
                    await session.commit()
                    await session.refresh(wallet)
                    
                wallet.balance += amount
                
                tx = Transaction(
                    wallet_id=wallet.id,
                    amount=amount,
                    type="deposit",
                    description=f"Эквайринг ЮKassa (ID: {payment_obj.get('id', 'unknown')})",
                    status="completed"
                )
                session.add(tx)
                await session.commit()
                
                # Уведомляем пользователя
                alert_text = f"💰 <b>Зачисление от ЮKassa!</b>\nБаланс пополнен на <b>{amount:,.2f} ₽</b>"
                try:
                    await app.state.bot.send_message(telegram_id, alert_text, parse_mode="HTML")
                except:
                    pass
                    
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Yookassa Webhook Error: {e}")
        return Response(status_code=500)

# --- Insurance (Phase 24) ---

class InsuranceBuyRequest(BaseModel):
    telegram_id: int
    drone_model: str
    serial_number: str
    coverage_amount: float

@app.get("/api/v1/insurance")
async def get_user_insurance(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """Получение активных полисов пользователя"""
    from db.models.insurance import InsurancePolicy
    try:
        res = await session.execute(
            select(InsurancePolicy)
            .where(InsurancePolicy.user_id == telegram_id)
            .order_by(InsurancePolicy.created_at.desc())
        )
        policies = res.scalars().all()
        
        out = []
        for p in policies:
            out.append({
                "id": p.id,
                "drone_model": p.drone_model,
                "serial_number": p.serial_number,
                "coverage_amount": p.coverage_amount,
                "premium": p.premium,
                "status": p.status,
                "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat()
            })
        return JSONResponse(content={"ok": True, "policies": out})
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@app.post("/api/v1/insurance/buy")
async def buy_insurance(data: InsuranceBuyRequest, session: AsyncSession = Depends(get_session)):
    """Оформление КАСКО за счет внутреннего баланса"""
    from db.models.insurance import InsurancePolicy
    from db.models.wallet import Wallet, Transaction
    from datetime import datetime, timedelta
    
    try:
        if data.coverage_amount < 50000:
            return JSONResponse(status_code=400, content={"ok": False, "error": "Минимальная стоимость БПЛА 50 000 ₽"})
            
        premium = data.coverage_amount * 0.05 # 5% тариф
        
        # Списываем баланс
        wallet_res = await session.execute(select(Wallet).where(Wallet.user_id == data.telegram_id))
        wallet = wallet_res.scalar_one_or_none()
        
        if not wallet or wallet.balance < premium:
            return JSONResponse(status_code=400, content={"ok": False, "error": "Недостаточно средств на балансе. Пополните кошелек."})
            
        wallet.balance -= premium
        
        # Создаем Транзакцию
        tx = Transaction(
            wallet_id=wallet.id,
            amount=premium,
            type="payment",
            description=f"Оплата КАСКО ({data.drone_model})",
            status="completed"
        )
        session.add(tx)
        
        # Создаем Полис
        policy = InsurancePolicy(
            user_id=data.telegram_id,
            drone_model=data.drone_model,
            serial_number=data.serial_number,
            coverage_amount=data.coverage_amount,
            premium=premium,
            status="active",
            end_date=datetime.utcnow() + timedelta(days=30)
        )
        session.add(policy)
        await session.commit()
        
        # Отправляем чек в Телеграм
        alert_text = (
            f"🛡 <b>Электронный полис КАСКО активирован!</b>\n\n"
            f"<b>БПЛА:</b> {data.drone_model}\n"
            f"<b>С/Н:</b> {data.serial_number}\n"
            f"<b>Покрытие:</b> {data.coverage_amount:,.0f} ₽\n"
            f"<b>Списано:</b> {premium:,.0f} ₽\n\n"
            f"✅ Полис действует 30 дней."
        )
        try:
            await app.state.bot.send_message(data.telegram_id, alert_text, parse_mode="HTML")
        except:
            pass
            
        return JSONResponse(content={"ok": True, "premium": premium, "new_balance": wallet.balance})
        
    except Exception as e:
        logger.error(f"Insurance Buy Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

# --- Airspace Auth (Phase 26) ---

class AirspacePlanRequest(BaseModel):
    telegram_id: int
    lat: float
    lng: float
    radius: int
    height: int
    start_time: str
    end_time: str
    drone_model: str

@app.post("/api/v1/airspace/plan/generate")
async def generate_airspace_plan(data: AirspacePlanRequest, session: AsyncSession = Depends(get_session)):
    """
    Генерирует заявку на Использование Воздушного Пространства (ИВП)
    в формате телеграфного сообщения для подачи в ФГИС ОрВД.
    """
    try:
        from datetime import datetime
        # Парсим время
        start_dt = datetime.fromisoformat(data.start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(data.end_time.replace('Z', '+00:00'))
        
        # Формат даты для ОрВД (ГГММДД и ЧЧММ)
        date_str = start_dt.strftime("%y%m%d")
        time_start = start_dt.strftime("%H%M")
        time_end = end_dt.strftime("%H%M")
        
        # Конвертация координат (пример: 5545С03737В)
        lat_dg = int(abs(data.lat))
        lat_mn = int((abs(data.lat) - lat_dg) * 60)
        lng_dg = int(abs(data.lng))
        lng_mn = int((abs(data.lng) - lng_dg) * 60)
        lat_dir = "С" if data.lat >= 0 else "Ю"
        lng_dir = "В" if data.lng >= 0 else "З"
        
        coord_str = f"{lat_dg:02d}{lat_mn:02d}{lat_dir}{lng_dg:03d}{lng_mn:02d}{lng_dir}"
        
        # Формирование телеграфного сообщения (упрощенный формат СППИ)
        # 1-й блок: Вид плана (SHR - Предварительный)
        # 2-й блок: Опознавательный индекс или модель
        # 3-й блок: Правила полетов (V - визуальные)
        # 4-й блок: Тип и количество
        flight_msg = (
            f"(ПЛН-БПЛА{data.telegram_id[-4:] if str(data.telegram_id).isdigit() else '0000'}-У\n"
            f"-{data.drone_model[:4].upper()}/Л-С/К\n"
            f"-{coord_str}{time_start}\n"
            f"-ДОФ/{date_str} РМК/АЭРОФОТОСЪЕМКА РАДИУС {data.radius}М ВЫСОТА ДО {data.height}М "
            f"РАСЧЕТНОЕ ВРЕМЯ ОКОНЧАНИЯ {time_end})"
        )
        
        # Отправляем в Телеграм пилоту
        alert_text = (
            f"✈️ <b>Ваш план полета ИВП Готов!</b>\n\n"
            f"Район: <b>{coord_str}</b>\n"
            f"Высота: до <b>{data.height} м</b>\n"
            f"Время: с <b>{start_dt.strftime('%H:%M')}</b> до <b>{end_dt.strftime('%H:%M')}</b>\n\n"
            f"Скопируйте текст ниже для подачи в Систему Представления Планов Полетов (СППИ):\n\n"
            f"<code>{flight_msg}</code>\n\n"
            f"⚠️ <b>Важно:</b> Не забудьте позвонить диспетчеру местного центра ОрВД за 2 часа до начала выполнения работ!"
        )
        try:
            await app.state.bot.send_message(data.telegram_id, alert_text, parse_mode="HTML")
        except:
            pass
            
        return JSONResponse(content={"ok": True, "message_format": flight_msg, "coord_str": coord_str})
        
    except Exception as e:
        logger.error(f"Airspace Plan Error: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

if __name__ == "__main__":
    # Use the filename "dashboard" for uvicorn string reference
    uvicorn.run("dashboard:app", host="0.0.0.0", port=8000, reload=True)
