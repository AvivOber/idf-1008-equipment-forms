"""
Core PDF generation: overlays soldier + issuer details onto the scanned
Form 1008 (Plas"am) template and merges the overlay with the original scan.
"""
import io
import os
import re
from datetime import date

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import config

_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("HebrewSans", config.FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("HebrewSans-Bold", config.FONT_BOLD))
    _FONTS_REGISTERED = True


def _rtl(text):
    """Reverse Hebrew text for visual LTR rendering (numbers stay untouched by callers)."""
    return text[::-1]


def split_full_name(full_name):
    parts = full_name.strip().split()
    if not parts:
        return "", ""
    first = parts[0]
    last = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first, last


def validate_soldier(full_name, personal_number, rank):
    errors = []
    if not full_name or not full_name.strip():
        errors.append("שם מלא חסר")
    if not personal_number or not re.fullmatch(r"\d{5,8}", str(personal_number).strip()):
        errors.append("מספר אישי לא תקין")
    if not rank or not rank.strip():
        errors.append("דרגה חסרה")
    return errors


def _fit_font_size(c, font_name, text, max_width, base_size, min_size=5.5):
    size = base_size
    while size > min_size and pdfmetrics.stringWidth(text, font_name, size) > max_width:
        size -= 0.5
    return size


def _draw_overlay(buf, full_name, personal_number, rank, issue_date=None):
    _register_fonts()
    issue_date = issue_date or date.today().strftime("%d.%m.%Y")
    first_name, last_name = split_full_name(full_name)

    c = canvas.Canvas(buf, pagesize=(config.PAGE_WIDTH, config.PAGE_HEIGHT))
    C = config.COORDS

    def hebrew(key, text, size=12, bold=False):
        x, y, max_width = C[key]
        font_name = "HebrewSans-Bold" if bold else "HebrewSans"
        fitted = _fit_font_size(c, font_name, text, max_width, size)
        c.setFont(font_name, fitted)
        c.drawRightString(x, y, _rtl(text))

    def number(key, text, size=11):
        # Helvetica, not the Hebrew font: NotoSansHebrew has no visible digit glyphs.
        x, y, max_width = C[key]
        fitted = _fit_font_size(c, "Helvetica", text, max_width, size)
        c.setFont("Helvetica", fitted)
        c.drawRightString(x, y, text)

    # Top names
    hebrew("issuer_top_name", f"{config.ISSUER['first_name']} {config.ISSUER['last_name']}", size=13, bold=True)
    hebrew("receiver_top_name", full_name.strip(), size=13, bold=True)

    # Bottom identity block - issuer (fixed)
    hebrew("issuer_first_name", config.ISSUER["first_name"])
    hebrew("issuer_last_name", config.ISSUER["last_name"])
    hebrew("issuer_rank", config.ISSUER["rank"])
    number("issuer_personal_number", config.ISSUER["personal_number"])

    # Bottom identity block - receiver (dynamic)
    hebrew("receiver_first_name", first_name)
    hebrew("receiver_last_name", last_name)
    hebrew("receiver_rank", rank.strip())
    number("receiver_personal_number", str(personal_number).strip())

    # Signature + date
    hebrew("issuer_signature", f"{config.ISSUER['first_name']} {config.ISSUER['last_name']}", size=12, bold=True)
    number("issuer_date", issue_date)
    hebrew("receiver_signature", full_name.strip(), size=12, bold=True)
    number("receiver_date", issue_date)

    # Checkmarks - helmet + vest are the only items reissued/confirmed per form.
    # Uses Helvetica (not the Hebrew font, which has no Latin glyphs).
    c.setFont("Helvetica-Bold", 13)
    for key in ("helmet_check", "vest_check"):
        x, y = C[key]
        c.drawCentredString(x, y, "V")

    c.save()


def generate_form(full_name, personal_number, rank, issue_date=None, output_path=None):
    """Generate a single signed Form 1008 PDF for one soldier.

    Returns the bytes of the generated PDF, and writes it to output_path if given.
    """
    errors = validate_soldier(full_name, personal_number, rank)
    if errors:
        raise ValueError("; ".join(errors))

    overlay_buf = io.BytesIO()
    _draw_overlay(overlay_buf, full_name, personal_number, rank, issue_date)
    overlay_buf.seek(0)

    overlay_reader = PdfReader(overlay_buf)
    base_reader = PdfReader(config.TEMPLATE_PDF)
    writer = PdfWriter()

    page = base_reader.pages[0]
    page.merge_page(overlay_reader.pages[0])
    writer.add_page(page)

    out_buf = io.BytesIO()
    writer.write(out_buf)
    pdf_bytes = out_buf.getvalue()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes


def safe_filename(full_name, personal_number):
    name = re.sub(r"[^\w\-]", "_", full_name.strip(), flags=re.UNICODE)
    return f"1008_{name}_{personal_number}.pdf"
