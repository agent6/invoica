# routes/pdf.py

from io import BytesIO
from datetime import datetime
from flask import Blueprint, session, redirect, url_for, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from models import Invoice, Settings

pdf_bp = Blueprint('pdf', __name__, url_prefix='/invoices')


@pdf_bp.route('/<int:invoice_id>/pdf')
def generate(invoice_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    inv      = Invoice.query.get_or_404(invoice_id)
    client   = inv.client
    settings = Settings.query.filter_by(user_id=session['user_id']).first() \
               or Settings(user_id=session['user_id'])

    # prepare buffer & canvas
    buf = BytesIO()
    c   = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    m    = 0.5 * inch  # margin

    # ── Header: Company on left, "INVOICE" on right ─────────────
    c.setFont("Helvetica-Bold", 18)
    c.drawString(m, h - m - 5, settings.company_name or "Your Company")
    c.setFont("Helvetica", 10)
    c.drawString(m, h - m - 20, settings.company_address or "")

    c.setFont("Helvetica-Bold", 32)
    c.drawRightString(w - m, h - m - 5, "INVOICE")

    # ── Meta box ─────────────────────────────────────────────────
    box_w, box_h = 2.2 * inch, 1.0 * inch
    label_height = 32
    gap = 8
    box_x = w - m - box_w
    box_y = (h - m - label_height) - gap - box_h

    c.roundRect(box_x, box_y, box_w, box_h, 6)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(box_x + 8, box_y + box_h - 14, f"Invoice #: {inv.id:03d}")
    c.setFont("Helvetica", 10)
    c.drawString(box_x + 8, box_y + box_h - 28, f"Date: {datetime.today().date()}")
    c.drawString(box_x + 8, box_y + box_h - 42, f"Status: {inv.status}")

    # ── "Bill To" section ───────────────────────────────────────
    bill_x = m
    bill_y = box_y - 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(bill_x, bill_y, "Bill To")
    c.setFont("Helvetica", 11)
    line = 14
    c.drawString(bill_x, bill_y - line, client.name)
    if client.email:
        c.drawString(bill_x, bill_y - 2*line, client.email)
    if client.phone:
        c.drawString(bill_x, bill_y - 3*line, client.phone)

    # ── Line Items table ────────────────────────────────────────
    table_x   = m
    # leave space for up to 3 lines of contact under "Bill To"
    table_top = bill_y - ( (3 if client.phone else (2 if client.email else 1)) * line ) - 20

    c.setLineWidth(1)
    c.line(table_x, table_top, w - m, table_top)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(table_x + 2, table_top - 14, "Description")
    c.drawRightString(w - m - 2, table_top - 14, "Amount")
    c.line(table_x, table_top - 18, w - m, table_top - 18)

    # ── items ───────────────────────────────────────────────────
    row_y = table_top - 32
    c.setFont("Helvetica", 11)
    for item in inv.items:
        c.drawString(table_x + 2, row_y, item.description)
        c.drawRightString(w - m - 2, row_y, f"${item.amount:,.2f}")
        row_y -= 18

    # ── Total Due ───────────────────────────────────────────────
    c.line(table_x, row_y - 4, w - m, row_y - 4)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(table_x + 2, row_y - 20, "Total Due")
    total = sum(i.amount for i in inv.items)
    c.drawRightString(w - m - 2, row_y - 20, f"${total:,.2f}")

    # ── Terms (footer) ─────────────────────────────────────────
    if settings.default_terms:
        c.setFont("Helvetica", 9)
        c.drawString(m, m + 10, f"Terms: {settings.default_terms}")

    # finish up
    c.showPage()
    c.save()
    buf.seek(0)

    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"invoice_{inv.id:03d}.pdf"
    )
