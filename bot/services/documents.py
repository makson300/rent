import os
import urllib.request
from datetime import datetime
from fpdf import FPDF
import logging

logger = logging.getLogger(__name__)

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "fonts")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "docs_out")

# Ensure directories exist
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

FONT_PATH = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")

def ensure_fonts():
    """Download fonts if they run missing, for PDF Cyrillic support."""
    if not os.path.exists(FONT_PATH):
        logger.info("Downloading Cyrillic font DejaVuSans.ttf...")
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        urllib.request.urlretrieve(url, FONT_PATH)
    if not os.path.exists(FONT_BOLD_PATH):
        logger.info("Downloading Cyrillic font DejaVuSans-Bold.ttf...")
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf"
        urllib.request.urlretrieve(url, FONT_BOLD_PATH)

def generate_b2b_contract(job_id: int, employer_name: str, pilot_name: str, 
                          job_title: str, budget: str, city: str) -> str:
    """Генерация PDF Договора подряда для конкретной задачи"""
    ensure_fonts()
    
    pdf = FPDF()
    pdf.add_page()
    
    # Регистрация шрифтов
    pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
    pdf.add_font("DejaVu", "B", FONT_BOLD_PATH, uni=True)
    
    # Title
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, f"ДОГОВОР ОКАЗАНИЯ УСЛУГ (ПОДРЯДА) № {job_id}", ln=True, align="C")
    pdf.ln(5)
    
    # City and Date
    pdf.set_font("DejaVu", "", 12)
    current_date = datetime.now().strftime("%d %B %Y г.")
    pdf.cell(100, 10, f"г. {city}")
    pdf.cell(0, 10, current_date, ln=True, align="R")
    pdf.ln(10)
    
    # Preamble
    preamble = (
        f"Заказчик: {employer_name}, с одной стороны, и "
        f"Исполнитель: {pilot_name}, с другой стороны, "
        f"далее совместно именуемые «Стороны», заключили настоящий Договор о нижеследующем:"
    )
    pdf.multi_cell(0, 8, preamble)
    pdf.ln(5)
    
    # Section 1
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "1. ПРЕДМЕТ ДОГОВОРА", ln=True)
    pdf.set_font("DejaVu", "", 12)
    content1 = (
        f"1.1. Исполнитель обязуется оказать Заказчику услуги по заданию: «{job_title}», "
        "а Заказчик обязуется принять и оплатить оказанные услуги."
    )
    pdf.multi_cell(0, 8, content1)
    pdf.ln(5)
    
    # Section 2
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "2. СТОИМОСТЬ И ПОРЯДОК ОПЛАТЫ", ln=True)
    pdf.set_font("DejaVu", "", 12)
    content2 = (
        f"2.1. Согласованная стоимость услуг составляет: {budget}.\n"
        "2.2. Заказчик резервирует указанную сумму на расчетном счете платформы «Sky Rent AI» "
        "(Безопасная сделка) до полного выполнения работ Исполнителем.\n"
        "2.3. Денежные средства переводятся Исполнителю по факту передачи материалов."
    )
    pdf.multi_cell(0, 8, content2)
    pdf.ln(5)
    
    # Section 3
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "3. ОТВЕТСТВЕННОСТЬ", ln=True)
    pdf.set_font("DejaVu", "", 12)
    content3 = (
        "3.1. Исполнитель гарантирует соблюдение правил использования воздушного пространства "
        "(ИВП) и несет полную ответственность за безопасность своего БПЛА.\n"
        "3.2. Если полет требует разрешения ОрВД, Исполнитель берет его оформление на себя."
    )
    pdf.multi_cell(0, 8, content3)
    pdf.ln(15)
    
    # Signatures
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(95, 10, "ЗАКАЗЧИК")
    pdf.cell(95, 10, "ИСПОЛНИТЕЛЬ", ln=True, align="R")
    
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(95, 10, f"____________ / {employer_name}")
    pdf.cell(95, 10, f"____________ / {pilot_name}", ln=True, align="R")
    
    # Save the PDF
    filepath = os.path.join(DOCS_DIR, f"Contract_Job_{job_id}.pdf")
    pdf.output(filepath)
    logger.info(f"Generated PDF contract saving to {filepath}")
    return filepath
