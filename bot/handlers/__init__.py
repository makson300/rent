from bot.handlers.start import router as start_router
from bot.handlers.profile import router as profile_router
from bot.handlers.menu import router as menu_router
from bot.handlers.listing_create import router as listing_create_router
from bot.handlers.catalog import router as catalog_router
from bot.handlers.admin import router as admin_router
from bot.handlers.admin_moderation import router as admin_moderation_router
from bot.handlers.my_listings import router as my_listings_router
from bot.handlers.education import router as education_router
from bot.handlers.sales import router as sales_router
from bot.handlers.packages import router as packages_router
from bot.handlers.search import router as search_router
from bot.handlers.seller_profile import router as seller_profile_router
from bot.handlers.operators import router as operators_router
from bot.handlers.support import router as support_router
from bot.handlers.emergency import router as emergency_router
from bot.handlers.admin_emergency import router as admin_emergency_router
from bot.handlers.admin_advisor import router as admin_advisor_router
from bot.handlers.admin_flight import router as admin_flight_router
from bot.handlers.booking import router as booking_router
from bot.handlers.contract import router as contract_router
from bot.handlers.job import router as job_router
from bot.handlers.job_hiring import router as job_hiring_router
from bot.handlers.orvd import router as orvd_router
from bot.handlers.tariffs import router as tariffs_router
from bot.handlers.tenders import router as tenders_router
from bot.handlers.momoa_assessment import router as momoa_assessment_router
from bot.handlers.store_ai import router as store_ai_router
__all__ = [
    "start_router", "profile_router", "menu_router", 
    "listing_create_router", "catalog_router", "admin_router", 
    "admin_moderation_router", "my_listings_router", 
    "education_router", "sales_router", "packages_router",
    "search_router", "seller_profile_router", "operators_router",
    "support_router", "emergency_router", "admin_emergency_router",
    "admin_advisor_router", "admin_flight_router",
    "booking_router", "contract_router",
    "job_router", "job_hiring_router", "orvd_router",
    "tariffs_router", "tenders_router", "momoa_assessment_router", "store_ai_router"
]
