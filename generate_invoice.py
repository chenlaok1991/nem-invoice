#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEM Studios Invoice PDF Generator — Redesigned Layout v2
Clean, modern invoice with proper spacing and margins.
"""

import sys
import os
import json
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from PIL import Image as PILImage


# ── Layout constants ──
MARGIN_LEFT = 54          # 0.75 inch
MARGIN_RIGHT = 54         # 0.75 inch
MARGIN_TOP = 50
CONTENT_WIDTH = letter[0] - MARGIN_LEFT - MARGIN_RIGHT  # ~504pt
LOGO_SIZE = 72


def _draw_text_block(c, x, y, text, font="Helvetica", size=10, color=colors.black):
    """Draw multi-line text and return the final y position."""
    c.setFont(font, size)
    c.setFillColor(color)
    lines = text.split('\n')
    for line in lines:
        c.drawString(x, y, line.strip())
        y -= (size * 1.35)
    return y


def generate_invoice(data):
    """Generate a professional invoice PDF."""

    # ── Parse input ──
    client_name    = data.get('client_name', '')
    client_address = data.get('client_address', '')
    date_str       = data.get('date', '')
    item_desc      = data.get('item_description', '')
    amount_str     = data.get('amount', '0')

    try:
        amount = float(amount_str.replace(',', '').replace('$', ''))
    except ValueError:
        amount = 0.0

    fmt_amount = f"${amount:,.2f}"

    # ── Dates ──
    date_obj    = datetime.strptime(date_str, "%b %d, %Y")
    inv_num     = f"{date_obj.month:02d}{date_obj.day:02d}{str(date_obj.year)[2:]}"
    due_date    = (date_obj + timedelta(days=30)).strftime("%b %d, %Y")

    # ── Output path ──
    output_path = os.path.join(os.path.expanduser("~/Desktop"), f"Invoice_{inv_num}.pdf")

    # ── Canvas setup ──
    c = canvas.Canvas(output_path, pagesize=letter)
    W, H = letter

    # ── Colors ──
    PRIMARY   = colors.HexColor('#1a1a2e')
    SECONDARY = colors.HexColor('#16213e')
    GRAY      = colors.HexColor('#888888')
    LIGHT     = colors.HexColor('#f0f0f4')
    BORDER    = colors.HexColor('#d0d0d8')

    # ── Spacing ──
    L = MARGIN_LEFT
    R = W - MARGIN_RIGHT
    CW = CONTENT_WIDTH

    # ═══════════════════════════════════════
    # SECTION 1: Logo + Invoice Title
    # ═══════════════════════════════════════
    y = H - MARGIN_TOP - LOGO_SIZE

    # Logo — prefer local logo.png (portable), fallback to desktop reference
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.expanduser("~/Desktop"), "invoice 参考", "Logo NEM_Tranparent.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, L, y, width=LOGO_SIZE, height=LOGO_SIZE, mask='auto')

    # "INVOICE" title — right-aligned
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(PRIMARY)
    c.drawRightString(R, H - MARGIN_TOP - 24, "INVOICE")

    # Invoice number — right-aligned, below title
    c.setFont("Helvetica", 13)
    c.setFillColor(GRAY)
    c.drawRightString(R, H - MARGIN_TOP - 44, f"No. {inv_num}")

    # ── Thin accent line ──
    y_line = y - 14
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(2)
    c.line(L, y_line, R, y_line)

    # ═══════════════════════════════════════
    # SECTION 2: From / Bill To / Dates
    # ═══════════════════════════════════════
    y = y_line - 24
    col_mid = L + CW * 0.38  # split point for 2-column layout

    # ── Left column: Bill To ──
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

    # ── Right column: From + Dates ──
    ry = y_line - 24

    # From
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

    # Date + Due Date
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

    # Amount Due highlight box
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

    # ── Second separator line ──
    y_sep = min(y, ry - 30)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(L, y_sep, R, y_sep)

    # ═══════════════════════════════════════
    # SECTION 3: Items Table
    # ═══════════════════════════════════════
    table_top = y_sep - 16

    # 4 columns that fit within CONTENT_WIDTH
    item_w  = CW * 0.48
    qty_w   = CW * 0.12
    rate_w  = CW * 0.20
    amt_w   = CW * 0.20

    header = ["Description", "Qty", "Rate", "Amount"]
    row    = [item_desc, "1", fmt_amount, fmt_amount]

    t = Table([header, row], colWidths=[item_w, qty_w, rate_w, amt_w])
    t.setStyle(TableStyle([
        # Header
        ('BACKGROUND',  (0, 0), (-1, 0), SECONDARY),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.white),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, 0), 10),
        ('TOPPADDING',  (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 8),

        # Data
        ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',    (0, 1), (-1, -1), 10),
        ('TOPPADDING',  (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 1), (-1, -1), 10),

        # Grid
        ('GRID',        (0, 0), (-1, -1), 0.4, BORDER),
        ('LINEBELOW',   (0, 0), (-1, 0), 1.5, SECONDARY),
        ('BOX',         (0, 0), (-1, -1), 0.8, SECONDARY),

        # Alignment
        ('ALIGN',       (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN',       (0, 0), (0, -1), 'LEFT'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',(0, 0), (-1, -1), 8),
    ]))

    t.wrapOn(c, CW, 200)
    t.drawOn(c, L, table_top - 52)

    # ═══════════════════════════════════════
    # SECTION 4: Summary (right-aligned)
    # ═══════════════════════════════════════
    sum_x = R  # right edge for labels and values
    sum_y = table_top - 82

    # Subtotal
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

    # ── Total bar ──
    sum_y -= 32
    total_bar_x = sum_x - 160
    total_bar_w = 160
    c.setFillColor(SECONDARY)
    c.roundRect(total_bar_x, sum_y - 3, total_bar_w, 20, 3, fill=True, stroke=False)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.white)
    c.drawString(total_bar_x + 10, sum_y + 3, "Total")
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(total_bar_x + total_bar_w - 10, sum_y + 3, fmt_amount)

    # ═══════════════════════════════════════
    # SECTION 5: Notes
    # ═══════════════════════════════════════
    notes_y = table_top - 140
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(GRAY)
    c.drawString(L, notes_y, "NOTES")
    notes_y -= 14
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor('#555555'))
    # Simple word-wrap
    max_chars = int(CW / 5)  # rough estimate for 9pt font
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

    # ═══════════════════════════════════════
    # SECTION 6: Terms / Payment Info
    # ═══════════════════════════════════════
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

    # ── Footer ──
    c.setFont("Helvetica", 7)
    c.setFillColor(GRAY)
    c.drawCentredString(W / 2, 28, "NEM Studios  •  620 Hacienda Dr, Monrovia, CA 91016  •  Info@nemstudios.com")

    # ── Save ──
    c.save()
    return output_path, inv_num


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
    else:
        raw = sys.stdin.read()
        data = json.loads(raw)

    out_path, inv_num = generate_invoice(data)
    print(f"OK:{out_path}:{inv_num}")
