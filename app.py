#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEM Studios Invoice Generator — Streamlit Cloud Version
Password protected, deployable to Streamlit Community Cloud.
"""

import streamlit as st
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import base64
import tempfile
import os
import urllib.request
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ═══════════════════════════════════════════════════════════════
# PASSWORD PROTECTION
# ═══════════════════════════════════════════════════════════════
PASSWORD = os.environ.get("INVOICE_PWD", "changeme")  # Set INVOICE_PWD in Streamlit Secrets

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🎵 NEM Studios Invoice Generator")
    st.markdown("---")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.markdown("<div style='text-align:center;color:#888;margin-top:40px'>NEM Studios © 2026</div>", unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════
# LOGO (base64 embedded for portability)
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# CHINESE FONT (download once, cache in /tmp)
# ═══════════════════════════════════════════════════════════════
FONT_DIR = os.path.join(tempfile.gettempdir(), 'fonts')
FONT_PATH = os.path.join(FONT_DIR, 'NotoSansSC-Regular.ttf')
FONT_NAME = 'NotoSansSC'

if not os.path.exists(FONT_PATH):
    os.makedirs(FONT_DIR, exist_ok=True)
    url = 'https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf'
    urllib.request.urlretrieve(url, FONT_PATH)

if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

LOGO_B64 = None  # Will load from file if exists

def get_logo_bytes():
    """Load logo bytes from local file or return None."""
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return f.read()
    return None

# ═══════════════════════════════════════════════════════════════
# PDF GENERATION
# ═══════════════════════════════════════════════════════════════

MARGIN_LEFT = 54
MARGIN_RIGHT = 54
MARGIN_TOP = 50
CONTENT_WIDTH = letter[0] - MARGIN_LEFT - MARGIN_RIGHT
LOGO_SIZE = 72

def generate_invoice_pdf(client_name, client_address, date_str, due_date_str, item_desc, amount_val):
    """Generate invoice PDF and return bytes."""
    
    # Parse date
    date_obj = datetime.strptime(date_str, "%b %d, %Y")
    inv_num = f"{date_obj.month:02d}{date_obj.day:02d}{str(date_obj.year)[2:]}"
    due_date = due_date_str
    fmt_amount = f"${amount_val:,.2f}"
    
    # Create PDF in memory
    buf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(buf.name, pagesize=letter)
    W, H = letter
    
    # Colors
    PRIMARY   = colors.HexColor('#1a1a2e')
    SECONDARY = colors.HexColor('#16213e')
    GRAY      = colors.HexColor('#888888')
    LIGHT     = colors.HexColor('#f0f0f4')
    BORDER    = colors.HexColor('#d0d0d8')
    
    L = MARGIN_LEFT
    R = W - MARGIN_RIGHT
    CW = CONTENT_WIDTH
    
    # ══ SECTION 1: Logo + Title ══
    y = H - MARGIN_TOP - LOGO_SIZE
    
    logo_bytes = get_logo_bytes()
    if logo_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(logo_bytes)
            tmp_path = tmp.name
        c.drawImage(tmp_path, L, y, width=LOGO_SIZE, height=LOGO_SIZE, mask='auto')
        os.unlink(tmp_path)
    
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(PRIMARY)
    c.drawRightString(R, H - MARGIN_TOP - 24, "INVOICE")
    
    c.setFont("Helvetica", 13)
    c.setFillColor(GRAY)
    c.drawRightString(R, H - MARGIN_TOP - 44, f"No. {inv_num}")
    
    y_line = y - 14
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(2)
    c.line(L, y_line, R, y_line)
    
    # ══ SECTION 2: From / Bill To ══
    y = y_line - 24
    col_mid = L + CW * 0.38
    
    # Bill To
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(GRAY)
    c.drawString(L, y, "BILL TO")
    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRIMARY)
    c.drawString(L, y, client_name)
    y -= 16
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    for line in client_address.split('\n'):
        c.drawString(L, y, line.strip())
        y -= 14
    
    # From + Dates
    ry = y_line - 24
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(GRAY)
    c.drawString(col_mid, ry, "FROM")
    ry -= 16
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(PRIMARY)
    c.drawString(col_mid, ry, "NEM Studios")
    ry -= 14
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(col_mid, ry, "620 Hacienda Dr, Monrovia, CA 91016")
    ry -= 14
    c.drawString(col_mid, ry, "Info@nemstudios.com")
    
    ry -= 26
    label_w = 65
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(col_mid, ry, "Date")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(col_mid + label_w, ry, date_str)
    
    ry -= 18
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(col_mid, ry, "Due Date")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(col_mid + label_w, ry, due_date)
    
    ry -= 32
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(col_mid, ry, "Balance Due")
    ry -= 12
    box_x = col_mid
    box_w = CW * 0.62
    c.setFillColor(LIGHT)
    c.roundRect(box_x, ry - 16, box_w, 22, 3, fill=True, stroke=False)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(PRIMARY)
    c.drawString(box_x + 12, ry - 9, fmt_amount)
    
    y_sep = min(y, ry - 30)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(L, y_sep, R, y_sep)
    
    # ══ SECTION 3: Items Table ══
    table_top = y_sep - 16
    item_w  = CW * 0.48
    qty_w   = CW * 0.12
    rate_w  = CW * 0.20
    amt_w   = CW * 0.20
    
    header = ["Description", "Qty", "Rate", "Amount"]
    row    = [item_desc, "1", fmt_amount, fmt_amount]
    
    t = Table([header, row], colWidths=[item_w, qty_w, rate_w, amt_w])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), SECONDARY),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.white),
        ('FONTNAME',    (0, 0), (-1, 0), 'NotoSansSC'),
        ('FONTSIZE',    (0, 0), (-1, 0), 10),
        ('TOPPADDING',  (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 8),
        ('FONTNAME',    (0, 1), (-1, -1), 'NotoSansSC'),
        ('FONTSIZE',    (0, 1), (-1, -1), 10),
        ('TOPPADDING',  (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 1), (-1, -1), 10),
        ('GRID',        (0, 0), (-1, -1), 0.4, BORDER),
        ('LINEBELOW',   (0, 0), (-1, 0), 1.5, SECONDARY),
        ('BOX',         (0, 0), (-1, -1), 0.8, SECONDARY),
        ('ALIGN',       (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN',       (0, 0), (0, -1), 'LEFT'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',(0, 0), (-1, -1), 8),
    ]))
    t.wrapOn(c, CW, 200)
    t.drawOn(c, L, table_top - 52)
    
    # ══ SECTION 4: Summary ══
    sum_x = R
    sum_y = table_top - 82
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawRightString(sum_x, sum_y, "Subtotal")
    c.drawRightString(sum_x - 75, sum_y, fmt_amount)
    
    sum_y -= 18
    c.setFillColor(GRAY)
    c.drawRightString(sum_x, sum_y, "Tax (0%)")
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawRightString(sum_x - 75, sum_y, "$0.00")
    
    sum_y -= 32
    total_bar_x = sum_x - 160
    total_bar_w = 160
    c.setFillColor(SECONDARY)
    c.roundRect(total_bar_x, sum_y - 3, total_bar_w, 20, 3, fill=True, stroke=False)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.white)
    c.drawString(total_bar_x + 10, sum_y + 3, "Total")
    c.drawRightString(total_bar_x + total_bar_w - 10, sum_y + 3, fmt_amount)
    
    # ══ SECTION 5: Notes ══
    notes_y = table_top - 140
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(GRAY)
    c.drawString(L, notes_y, "NOTES")
    notes_y -= 14
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor('#555555'))
    max_chars = int(CW / 5)
    words = item_desc.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if len(test) <= max_chars:
            line = test
        else:
            c.drawString(L, notes_y, line)
            notes_y -= 13
            line = w
    if line:
        c.drawString(L, notes_y, line)
    
    # ══ SECTION 6: Payment Info ══
    terms_y = notes_y - 26
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(L, terms_y + 10, R, terms_y + 10)
    
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(GRAY)
    c.drawString(L, terms_y, "PAYMENT INFORMATION")
    
    terms_y -= 16
    terms_lines = [
        "Wire Transfer — Bank of America",
        "Account: NEM Studios  |  Email: xueranmusic@gmail.com",
        "Account No.: 3250 1667 0219",
        "Routing: 122000661 / 121000358 (paper & electronic)  |  026009593 (wires)",
        "SWIFT: BOFAUS3N  |  Branch: Foothill-Rosemead",
        "Bank Address: 3555 E Foothill Blvd, Pasadena, CA 91107, US",
    ]
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor('#444444'))
    for line in terms_lines:
        c.drawString(L, terms_y, line)
        terms_y -= 12
    
    # Footer
    c.setFont("Helvetica", 7)
    c.setFillColor(GRAY)
    c.drawCentredString(W / 2, 28, "NEM Studios  •  620 Hacienda Dr, Monrovia, CA 91016  •  Info@nemstudios.com")
    
    c.save()
    
    with open(buf.name, "rb") as f:
        pdf_bytes = f.read()
    os.unlink(buf.name)
    
    return pdf_bytes, inv_num


# ═══════════════════════════════════════════════════════════════
# STREAMLIT UI
# ═══════════════════════════════════════════════════════════════

st.set_page_config(page_title="NEM Invoice", page_icon="🎵", layout="centered")

st.title("🎵 NEM Studios Invoice Generator")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    client_name = st.text_input("Client Company Name", placeholder="Hexany Audio")
    date_val = st.date_input("Date", value=datetime.today())
    amount_str = st.text_input("Amount ($)", placeholder="105000")

with col2:
    client_address = st.text_area("Client Address", placeholder="Street address\nCity, State ZIP\nCountry", height=90)
    item_desc = st.text_area("Project Description", placeholder="电视剧《凤凰台上》BGM音乐制作费", height=90)

# Convert date
date_str = date_val.strftime("%b %d, %Y")
due_date_str = due_date_val.strftime("%b %d, %Y")
inv_num_preview = f"{date_val.month:02d}{date_val.day:02d}{str(date_val.year)[2:]}"

st.info(f"📄 Invoice Number: **{inv_num_preview}**")

if st.button("📥 Generate Invoice PDF", type="primary", use_container_width=True):
    if not client_name or not amount_str or not item_desc:
        st.error("Please fill in all required fields")
    else:
        try:
            amount_val = float(amount_str.replace(',', '').replace('$', ''))
        except:
            st.error("Invalid amount")
            st.stop()
        
        with st.spinner("Generating..."):
            pdf_bytes, inv_num = generate_invoice_pdf(
                client_name, client_address, date_str, due_date_str, item_desc, amount_val
            )
        
        st.success(f"✅ Invoice #{inv_num} ready!")
        
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=f"Invoice_{inv_num}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("---")
st.markdown("<div style='text-align:center;color:#888'>NEM Studios © 2026</div>", unsafe_allow_html=True)
