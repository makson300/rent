import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# Populating with a font that supports Cyrillic if possible, otherwise standard
# Note: In a real environment we would bundle a TTF file.
# For this sandbox, we'll try to use a standard one and hope for the best or use ASCII stubs.

def generate_rental_contract(listing, owner, tenant, output_path):
    """Генерация PDF договора аренды"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 50, "DOGOVOR ARENDY OBORUDOVANIYA")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Date: {datetime.now().strftime('%d.%m.%Y')}")
    c.drawString(50, height - 100, f"City: {listing.city}")

    # Parties
    c.drawString(50, height - 140, "1. PARTIES")
    c.drawString(70, height - 160, f"OWNER: {owner.full_name or owner.first_name}")
    c.drawString(70, height - 180, f"TENANT: {tenant.full_name or tenant.first_name}")

    # Subject
    c.drawString(50, height - 220, "2. SUBJECT OF THE AGREEMENT")
    c.drawString(70, height - 240, f"Equipment: {listing.title}")
    c.drawString(70, height - 260, f"Description: {listing.description[:100]}...")

    # Financials
    c.drawString(50, height - 300, "3. PRICE AND DEPOSIT")
    c.drawString(70, height - 320, f"Price terms: {listing.price_list}")
    c.drawString(70, height - 340, f"Deposit: {listing.deposit_terms}")

    # Footer
    c.drawString(50, height - 400, "SIGNATURES:")
    c.line(50, height - 450, 200, height - 450)
    c.drawString(50, height - 465, "Owner")

    c.line(300, height - 450, 450, height - 450)
    c.drawString(300, height - 465, "Tenant")

    c.save()
    return output_path
