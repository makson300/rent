import uvicorn
import logging
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select, func

# Add project root to path to import db and bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import DASHBOARD_PASSWORD
from db.base import async_session, init_db
from db.models.user import User
from db.models.listing import Listing
from db.models.education import EducationApplication
from bot.services.ai_growth_advisor import get_growth_insights

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RentBot Admin Dashboard")
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != DASHBOARD_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

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
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

@app.get("/")
@app.head("/")
async def home(request: Request, _ = Depends(authenticate)):
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
            
        return templates.TemplateResponse(
            request=request, name="index.html", context={
                "stats": {
                    "users_count": users_count or 0, 
                    "active_listings": listings_count or 0,
                    "new_applications": new_apps or 0,
                    "new_feedback": new_feedback or 0
                }
            }
        )

    except Exception as e:
        logger.error(f"Error rendering home: {e}", exc_info=True)
        raise e

@app.get("/listings")
async def listings_page(request: Request, _ = Depends(authenticate)):
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

@app.post("/listings/{listing_id}/approve")
async def approve_listing_web(listing_id: int, _ = Depends(authenticate)):
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

@app.post("/listings/{listing_id}/reject")
async def reject_listing_web(listing_id: int, _ = Depends(authenticate)):
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

@app.get("/feedback")
async def feedback_page(request: Request, _ = Depends(authenticate)):
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

@app.post("/feedback/{feedback_id}/process")
async def process_feedback_web(feedback_id: int, _ = Depends(authenticate)):
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

@app.get("/applications")
async def applications(request: Request, _ = Depends(authenticate)):
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

@app.get("/ai-insights")
@app.head("/ai-insights")
async def ai_insights_page(request: Request, _ = Depends(authenticate)):
    """Страница с ИИ-рекомендациями по росту"""
    try:
        recommendations = await get_growth_insights()
        return templates.TemplateResponse(
            request=request, name="ai_advisor.html", context={"recommendations": recommendations}
        )
    except Exception as e:
        logger.error(f"Error rendering AI insights: {e}", exc_info=True)
        raise e

if __name__ == "__main__":
    # Use the filename "dashboard" for uvicorn string reference
    uvicorn.run("dashboard:app", host="0.0.0.0", port=8000, reload=True)
