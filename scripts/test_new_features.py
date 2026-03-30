import asyncio
import logging
from unittest.mock import MagicMock
import io
import datetime

logging.basicConfig(level=logging.INFO)

async def test_modules():
    print("--- TESTING TENDER MATCHER ---")
    try:
        from bot.services.tender_matcher import create_b2b_proposal
        
        # Мокаем сессию базы данных
        class MockListing:
            title = "DJI Matrice 300 RTK"
            description = "Профессиональный дрон с тепловизором"
            city = "Москва"
            seller_type = "company"
            price_list = "По запросу (B2B)"
            
        mock_session = MagicMock()
        
        # Патчим импорт внутри функции
        import db.crud.listing
        db.crud.listing.get_listings = MagicMock(return_value=asyncio.sleep(0, result=[MockListing()]))
        
        msg, file_io = await create_b2b_proposal(mock_session, "Тендерный тест", "Нужен Matrice")
        print("Tender message:", msg)
        if file_io:
            print("Tender file name:", file_io.name)
            print("Tender content length:", len(file_io.getvalue()))
        print("✅ Tender Matcher OK")
    except Exception as e:
        print(f"❌ Tender Matcher failed: {e}")

    print("\n--- TESTING ORVD EXPORTER ---")
    try:
        from bot.services.orvd_exporter import generate_orvd_document
        
        class MockFlightPlan:
            id = 999
            user_id = 12345
            task_description = "Съемка трубопровода"
            coords = "12.345, 67.890"
            radius_m = 500
            max_altitude_m = 150
            start_time = datetime.datetime.now()
            end_time = datetime.datetime.now() + datetime.timedelta(hours=2)
            
        file_io = await generate_orvd_document(MockFlightPlan())
        print("ORVD File:", file_io.name)
        print("Lines count:", len(file_io.getvalue().decode('utf-8').split('\n')))
        print("✅ ORVD Exporter OK")
    except Exception as e:
        print(f"❌ ORVD Exporter failed: {e}")

    print("\n--- TESTING VISION ANALYST IMPORTS ---")
    try:
        from bot.services.vision_moderator import analyze_emergency_photo
        print("Vision analyzer imported:", analyze_emergency_photo.__name__)
        print("✅ Vision Analyzer OK")
    except Exception as e:
        print(f"❌ Vision analyzer imports failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_modules())
